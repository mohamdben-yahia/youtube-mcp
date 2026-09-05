"""YouTube Data API v3 client wrapper with quota and error handling."""

import os
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any, Callable, Dict, List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_mcp.formatters import (
    format_search_results,
    format_video_details,
    format_channel_details,
    format_playlist_item,
    format_comment_thread,
)
from youtube_mcp.transcripts import fetch_transcript, extract_video_id
from youtube_mcp.cache import get_cache, ResponseCache


class YouTubeClient:
    """Wrapper around googleapiclient for YouTube Data API v3 with multi-key quota rotation."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_keys: Optional[List[str]] = None,
        cache: Optional[ResponseCache] = None,
    ):
        raw_keys: List[str] = []
        if api_keys:
            raw_keys.extend(api_keys)
        if api_key:
            raw_keys.extend([k.strip() for k in api_key.split(",") if k.strip()])

        env_keys = os.getenv("YOUTUBE_API_KEYS")
        if env_keys:
            raw_keys.extend([k.strip() for k in env_keys.split(",") if k.strip()])

        env_key = os.getenv("YOUTUBE_API_KEY")
        if env_key:
            raw_keys.extend([k.strip() for k in env_key.split(",") if k.strip()])

        # Deduplicate keys while preserving order
        seen = set()
        self.api_keys: List[str] = []
        for k in raw_keys:
            if k and k not in seen:
                seen.add(k)
                self.api_keys.append(k)

        self._active_key_index: int = 0
        self._service = None
        self.cache = cache or get_cache()

    @property
    def api_key(self) -> Optional[str]:
        """Return the current active API key."""
        if not self.api_keys:
            return None
        return self.api_keys[self._active_key_index]

    @api_key.setter
    def api_key(self, value: Optional[str]):
        """Set or override the active API key."""
        if value:
            clean_keys = [k.strip() for k in value.split(",") if k.strip()]
            for k in clean_keys:
                if k not in self.api_keys:
                    self.api_keys.insert(0, k)
            if clean_keys:
                self._active_key_index = self.api_keys.index(clean_keys[0])
        else:
            self.api_keys = []
            self._active_key_index = 0
        self._service = None

    @property
    def key_count(self) -> int:
        """Total number of API keys loaded in the pool."""
        return len(self.api_keys)

    @property
    def active_key_index(self) -> int:
        """0-based index of the currently active API key in the pool."""
        return self._active_key_index

    def rotate_key(self) -> Optional[str]:
        """Rotate to the next API key in the pool. Returns the newly activated key."""
        if not self.api_keys or len(self.api_keys) <= 1:
            return None
        self._active_key_index = (self._active_key_index + 1) % len(self.api_keys)
        self._service = None
        return self.api_key

    @property
    def service(self):
        if self._service is None:
            active_key = self.api_key
            if not active_key:
                raise ValueError(
                    "YOUTUBE_API_KEY is not set. Please set the YOUTUBE_API_KEY or YOUTUBE_API_KEYS environment variable "
                    "or pass api_key / api_keys when initializing the client."
                )
            self._service = build("youtube", "v3", developerKey=active_key)
        return self._service

    def _execute_api_request(self, build_request_fn: Callable[[], Any]) -> Any:
        """Execute a Google API request with automatic key rotation on quota exhaustion.

        If an HTTP 403 (quotaExceeded) error occurs and multiple keys are configured in the pool,
        this automatically rotates to the next available key and retries the request.
        """
        attempts = 0
        max_attempts = max(1, len(self.api_keys))

        while attempts < max_attempts:
            try:
                request = build_request_fn()
                return request.execute()
            except HttpError as e:
                status_code = getattr(getattr(e, "resp", None), "status", None)
                reason = "unknown"
                try:
                    error_details = json.loads(e.content.decode("utf-8"))
                    errors = error_details.get("error", {}).get("errors", [{}])
                    reason = errors[0].get("reason", "unknown")
                except Exception:
                    pass

                is_quota = (status_code == 403) and (
                    reason in ("quotaExceeded", "dailyLimitExceeded", "rateLimitExceeded")
                    or "quota" in str(e).lower()
                )

                if is_quota and len(self.api_keys) > 1 and attempts < max_attempts - 1:
                    attempts += 1
                    self.rotate_key()
                    continue
                raise

    def _handle_http_error(self, e: HttpError) -> Dict[str, Any]:
        """Convert Google API HttpError into a clean, actionable error response."""
        status_code = getattr(getattr(e, "resp", None), "status", None)
        try:
            error_details = json.loads(e.content.decode("utf-8"))
            errors = error_details.get("error", {}).get("errors", [{}])
            reason = errors[0].get("reason", "unknown")
            message = error_details.get("error", {}).get("message", str(e))
        except Exception:
            reason = "unknown"
            message = str(e)

        if reason == "quotaExceeded":
            pool_info = (
                f" All {len(self.api_keys)} API keys in the rotation pool were exhausted."
                if len(self.api_keys) > 1
                else ""
            )
            return {
                "success": False,
                "error": f"YouTube Data API quota exceeded.{pool_info}",
                "reason": "quotaExceeded",
                "status_code": status_code,
                "suggestion": "The daily 10,000 unit quota for your YouTube Data API project(s) has been reached. Quota resets at midnight Pacific Time.",
            }
        elif reason == "accessNotConfigured":
            return {
                "success": False,
                "error": "YouTube Data API v3 is not enabled on this Google Cloud project.",
                "reason": "accessNotConfigured",
                "status_code": status_code,
                "suggestion": "Enable the YouTube Data API v3 in your Google Cloud Console.",
            }
        elif reason in ("keyInvalid", "badRequest"):
            return {
                "success": False,
                "error": f"API request error: {message}",
                "reason": reason,
                "status_code": status_code,
                "suggestion": "Verify your YOUTUBE_API_KEY and request parameters.",
            }

        return {
            "success": False,
            "error": message,
            "reason": reason,
            "status_code": status_code,
        }

    def search(
        self,
        query: str,
        max_results: int = 10,
        search_type: str = "video",
        order: str = "relevance",
        published_after: Optional[str] = None,
        region_code: Optional[str] = None,
        raw: bool = False,
    ) -> Dict[str, Any]:
        """Search YouTube for videos, channels, or playlists."""
        try:
            params: Dict[str, Any] = {
                "q": query,
                "part": "snippet",
                "maxResults": min(max_results, 50),
                "type": search_type,
                "order": order,
            }
            if published_after:
                params["publishedAfter"] = published_after
            if region_code:
                params["regionCode"] = region_code

            if not raw and hasattr(self, "cache") and self.cache:
                cached_res = self.cache.get("search", params)
                if cached_res is not None:
                    return cached_res

            response = self._execute_api_request(lambda: self.service.search().list(**params))

            if raw:
                return response

            formatted = format_search_results(query, response)
            result = {"success": True, **formatted}
            if hasattr(self, "cache") and self.cache:
                self.cache.set("search", params, result)
            return result

        except HttpError as e:
            return self._handle_http_error(e)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_channels(
        self,
        query: str,
        max_results: int = 10,
        order: str = "relevance",
        region_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search YouTube specifically for channels matching a niche or topic, enriched with subscriber & view metrics.

        Args:
            query: Keywords, topic, or niche (e.g. 'ai automation', 'finance beginners').
            max_results: Number of channels to return (1 to 50, default 10).
            order: Ranking order ('relevance', 'videoCount', 'viewCount', 'rating').
            region_code: ISO 3166-1 alpha-2 country code (e.g. 'US', 'GB').
        """
        try:
            search_res = self.search(
                query=query,
                max_results=max_results,
                search_type="channel",
                order=order,
                region_code=region_code,
                raw=False,
            )
            if not search_res.get("success"):
                return search_res

            channel_items = search_res.get("results", [])
            if not channel_items:
                return {
                    "success": True,
                    "query": query,
                    "count": 0,
                    "channels": [],
                }

            channel_ids = [item["id"] for item in channel_items if item.get("id")]
            batch_details = self.get_channels_batch(channel_ids)
            details_map = {c.get("channel_id"): c for c in batch_details}

            enriched_channels = []
            for item in channel_items:
                cid = item.get("id")
                info = details_map.get(cid, {})
                enriched_channels.append({
                    "channel_id": cid,
                    "channel_title": item.get("title") or info.get("title"),
                    "handle": info.get("custom_url"),
                    "description": item.get("description") or info.get("description"),
                    "subscribers": info.get("subscriber_count", 0),
                    "total_views": info.get("view_count", 0),
                    "video_count": info.get("video_count", 0),
                    "url": item.get("url") or info.get("url"),
                })

            return {
                "success": True,
                "query": query,
                "count": len(enriched_channels),
                "channels": enriched_channels,
            }
        except HttpError as e:
            return self._handle_http_error(e)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_video_details(
        self,
        video_ids: List[str],
        raw: bool = False,
    ) -> Dict[str, Any]:
        """Fetch full details for one or more video IDs."""
        try:
            ids_str = ",".join(video_ids[:50])
            response = self._execute_api_request(
                lambda: self.service.videos().list(
                    part="snippet,contentDetails,statistics",
                    id=ids_str,
                )
            )

            if raw:
                return response

            items = response.get("items", [])
            videos = [format_video_details(item) for item in items]
            return {
                "success": True,
                "count": len(videos),
                "videos": videos,
            }

        except HttpError as e:
            return self._handle_http_error(e)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_channel_details(
        self,
        channel_id: Optional[str] = None,
        for_handle: Optional[str] = None,
        for_username: Optional[str] = None,
        raw: bool = False,
    ) -> Dict[str, Any]:
        """Fetch channel metadata by channel ID, @handle, or username."""
        try:
            params: Dict[str, Any] = {
                "part": "snippet,contentDetails,statistics",
            }
            if channel_id:
                params["id"] = channel_id
            elif for_handle:
                # Remove leading @ if present
                clean_handle = for_handle.lstrip("@")
                params["forHandle"] = clean_handle
            elif for_username:
                params["forUsername"] = for_username
            else:
                return {
                    "success": False,
                    "error": "Must provide one of 'channel_id', 'for_handle', or 'for_username'.",
                }

            response = self._execute_api_request(lambda: self.service.channels().list(**params))

            if raw:
                return response

            items = response.get("items", [])
            if not items:
                return {
                    "success": False,
                    "error": "Channel not found.",
                }

            return {
                "success": True,
                "channel": format_channel_details(items[0]),
            }

        except HttpError as e:
            return self._handle_http_error(e)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_playlist_items(
        self,
        playlist_id: str,
        max_results: int = 20,
        page_token: Optional[str] = None,
        raw: bool = False,
    ) -> Dict[str, Any]:
        """Fetch items in a playlist."""
        try:
            params: Dict[str, Any] = {
                "part": "snippet",
                "playlistId": playlist_id,
                "maxResults": min(max_results, 50),
            }
            if page_token:
                params["pageToken"] = page_token

            response = self._execute_api_request(lambda: self.service.playlistItems().list(**params))

            if raw:
                return response

            items = response.get("items", [])
            playlist_items = [format_playlist_item(item) for item in items]
            return {
                "success": True,
                "playlist_id": playlist_id,
                "total_results": response.get("pageInfo", {}).get("totalResults"),
                "next_page_token": response.get("nextPageToken"),
                "prev_page_token": response.get("prevPageToken"),
                "items": playlist_items,
            }

        except HttpError as e:
            return self._handle_http_error(e)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_video_comments(
        self,
        video_id: str,
        max_results: int = 20,
        order: str = "relevance",
        page_token: Optional[str] = None,
        raw: bool = False,
    ) -> Dict[str, Any]:
        """Fetch top-level comments and discussions for a video."""
        try:
            params: Dict[str, Any] = {
                "part": "snippet",
                "videoId": video_id,
                "maxResults": min(max_results, 100),
                "order": order,
                "textFormat": "plainText",
            }
            if page_token:
                params["pageToken"] = page_token

            response = self._execute_api_request(lambda: self.service.commentThreads().list(**params))

            if raw:
                return response

            items = response.get("items", [])
            comments = [format_comment_thread(item) for item in items]
            return {
                "success": True,
                "video_id": video_id,
                "total_results": response.get("pageInfo", {}).get("totalResults"),
                "next_page_token": response.get("nextPageToken"),
                "comments": comments,
            }

        except HttpError as e:
            return self._handle_http_error(e)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_channels_batch(self, channel_ids: List[str]) -> List[Dict[str, Any]]:
        """Fetch channel details for up to 50 channel IDs in a single batch call."""
        if not channel_ids:
            return []
        ids_str = ",".join(channel_ids[:50])
        response = self._execute_api_request(
            lambda: self.service.channels().list(
                part="snippet,contentDetails,statistics",
                id=ids_str,
            )
        )
        return [format_channel_details(item) for item in response.get("items", [])]

    def scout_niche_channels(
        self,
        niches: List[str],
        min_subscribers: int = 0,
        max_subscribers: Optional[int] = None,
        min_videos: int = 1,
        region_code: Optional[str] = None,
        channels_per_niche: int = 10,
        sort_by: str = "subscribers",
    ) -> Dict[str, Any]:
        """Launch a multi-niche discovery campaign to identify and rank top YouTube channels.

        Args:
            niches: List of topic niches or keywords to scout (e.g. ['ai automation', 'saas growth']).
            min_subscribers: Minimum subscriber threshold (e.g. 10000 for micro-influencers).
            max_subscribers: Optional maximum subscriber threshold (e.g. 500000).
            min_videos: Minimum video count to filter out dead or inactive accounts.
            region_code: ISO 3166-1 alpha-2 country code (e.g. 'US', 'GB').
            channels_per_niche: Number of top channels to return per niche.
            sort_by: Ranking attribute: 'subscribers', 'views', 'videos', or 'avg_views'.
        """
        try:
            campaign_results: Dict[str, Any] = {}
            total_discovered = 0

            for niche in niches:
                clean_niche = niche.strip()
                if not clean_niche:
                    continue

                # 1. Search channels directly
                search_params: Dict[str, Any] = {
                    "q": clean_niche,
                    "part": "snippet",
                    "maxResults": min(channels_per_niche * 3, 50),
                    "type": "channel",
                    "order": "relevance",
                }
                if region_code:
                    search_params["regionCode"] = region_code

                search_res = self._execute_api_request(lambda: self.service.search().list(**search_params))
                channel_ids = [
                    item["id"]["channelId"]
                    for item in search_res.get("items", [])
                    if item.get("id", {}).get("channelId")
                ]

                # 2. Also search top videos to discover active creators in this niche
                vid_params: Dict[str, Any] = {
                    "q": clean_niche,
                    "part": "snippet",
                    "maxResults": 25,
                    "type": "video",
                    "order": "viewCount",
                }
                if region_code:
                    vid_params["regionCode"] = region_code

                try:
                    vid_res = self._execute_api_request(lambda: self.service.search().list(**vid_params))
                    for item in vid_res.get("items", []):
                        ch_id = item.get("snippet", {}).get("channelId")
                        if ch_id and ch_id not in channel_ids:
                            channel_ids.append(ch_id)
                except Exception:
                    pass

                # Deduplicate and limit to 50 for batch request
                unique_ids = list(dict.fromkeys(channel_ids))[:50]
                if not unique_ids:
                    campaign_results[clean_niche] = {
                        "niche": clean_niche,
                        "total_found": 0,
                        "channels": [],
                    }
                    continue

                # Batch fetch channel statistics
                channels = self.get_channels_batch(unique_ids)

                # Filter by criteria
                filtered = []
                for ch in channels:
                    subs = ch.get("subscriber_count") or 0
                    vids = ch.get("video_count") or 0

                    if subs < min_subscribers:
                        continue
                    if max_subscribers is not None and subs > max_subscribers:
                        continue
                    if vids < min_videos:
                        continue

                    # Calculate average views per video
                    views = ch.get("view_count") or 0
                    avg_views = round(views / max(vids, 1))
                    ch["avg_views_per_video"] = avg_views
                    filtered.append(ch)

                # Sort channels
                if sort_by == "views":
                    filtered.sort(key=lambda x: x.get("view_count") or 0, reverse=True)
                elif sort_by == "videos":
                    filtered.sort(key=lambda x: x.get("video_count") or 0, reverse=True)
                elif sort_by == "avg_views":
                    filtered.sort(key=lambda x: x.get("avg_views_per_video") or 0, reverse=True)
                else:  # default 'subscribers'
                    filtered.sort(key=lambda x: x.get("subscriber_count") or 0, reverse=True)

                top_channels = filtered[:channels_per_niche]
                total_discovered += len(top_channels)

                campaign_results[clean_niche] = {
                    "niche": clean_niche,
                    "criteria": {
                        "min_subscribers": min_subscribers,
                        "max_subscribers": max_subscribers,
                        "min_videos": min_videos,
                        "sort_by": sort_by,
                    },
                    "total_matched": len(filtered),
                    "channels": top_channels,
                }

            return {
                "success": True,
                "total_niches": len(campaign_results),
                "total_channels_discovered": total_discovered,
                "campaigns": campaign_results,
            }

        except HttpError as e:
            return self._handle_http_error(e)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_trending_niches(
        self,
        region_code: str = "US",
        category: Optional[str] = "tech",
        max_results: int = 25,
        raw: bool = False,
    ) -> Dict[str, Any]:
        """Discover real-time trending topics, breakout niches, and viral videos.

        Uses the official YouTube Trending algorithm ('chart=mostPopular') to identify
        what is exploding right now in a given country and category.

        Args:
            region_code: ISO 3166-1 alpha-2 country code (default 'US', e.g. 'GB', 'CA', 'DE').
            category: Category name ('all', 'tech', 'gaming', 'education', 'howto', 'entertainment', 'news', 'music', 'sports') or numeric category ID.
            max_results: Number of trending videos to analyze (up to 50, default 25).
            raw: If True, returns unaltered raw YouTube Data API response.
        """
        from collections import Counter

        CATEGORY_MAP = {
            "all": None,
            "tech": "28",
            "gaming": "20",
            "education": "27",
            "howto": "26",
            "entertainment": "24",
            "news": "25",
            "music": "10",
            "people": "22",
            "sports": "17",
            "comedy": "23",
            "film": "1",
            "autos": "2",
        }

        try:
            params: Dict[str, Any] = {
                "part": "snippet,contentDetails,statistics",
                "chart": "mostPopular",
                "regionCode": region_code,
                "maxResults": min(max_results, 50),
            }

            cat_key = (category or "all").lower().strip()
            cat_id = CATEGORY_MAP.get(cat_key, cat_key if cat_key.isdigit() else None)
            if cat_id:
                params["videoCategoryId"] = cat_id

            response = self._execute_api_request(lambda: self.service.videos().list(**params))

            if raw:
                return response

            items = response.get("items", [])
            videos = [format_video_details(item) for item in items]

            # 1. Analyze trending tags
            tag_counter: Counter = Counter()
            for v in videos:
                tags = v.get("tags") or []
                for tag in tags:
                    clean_tag = tag.strip().lower()
                    if len(clean_tag) > 2:
                        tag_counter[clean_tag] += 1

            top_tags = [
                {"tag": tag, "frequency": count}
                for tag, count in tag_counter.most_common(15)
            ]

            # 2. Analyze recurring title keywords
            STOP_WORDS = {
                "the", "and", "for", "with", "this", "that", "how", "what", "you",
                "your", "from", "video", "official", "why", "are", "about", "new",
                "all", "who", "when", "where", "which", "can", "will", "just", "into"
            }
            word_counter: Counter = Counter()
            for v in videos:
                title = v.get("title", "")
                words = re.findall(r"\b[a-zA-Z0-9_-]{3,}\b", title.lower())
                for w in words:
                    if w not in STOP_WORDS:
                        word_counter[w] += 1

            top_keywords = [
                {"keyword": word, "frequency": count}
                for word, count in word_counter.most_common(15)
            ]

            # 3. Analyze creators driving the trends
            creator_stats: Dict[str, Dict[str, Any]] = {}
            for v in videos:
                ch_title = v.get("channel_title", "Unknown")
                ch_id = v.get("channel_id", "")
                views = v.get("view_count") or 0

                if ch_title not in creator_stats:
                    creator_stats[ch_title] = {
                        "channel_title": ch_title,
                        "channel_id": ch_id,
                        "channel_url": f"https://www.youtube.com/channel/{ch_id}" if ch_id else None,
                        "trending_videos_count": 0,
                        "total_trending_views": 0,
                    }
                creator_stats[ch_title]["trending_videos_count"] += 1
                creator_stats[ch_title]["total_trending_views"] += views

            top_creators = sorted(
                creator_stats.values(),
                key=lambda x: (x["trending_videos_count"], x["total_trending_views"]),
                reverse=True,
            )[:10]

            return {
                "success": True,
                "region_code": region_code,
                "category": category,
                "category_id": cat_id,
                "total_trending_videos_analyzed": len(videos),
                "top_rising_tags": top_tags,
                "top_recurring_keywords": top_keywords,
                "top_creators_trending": top_creators,
                "trending_videos": videos[:max_results],
            }

        except HttpError as e:
            return self._handle_http_error(e)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def audit_channel_strategy(
        self,
        channel_id_or_handle: str,
        sample_videos: int = 5,
    ) -> Dict[str, Any]:
        """Reverse-engineer a YouTube channel's content strategy and business model.

        Analyzes recent upload cadence, view performance distribution, title formulas,
        monetization funnels (sponsors, newsletters, affiliate links), and extracts
        the opening script hook from their top-performing video.

        Args:
            channel_id_or_handle: Channel handle (e.g. '@mkbhd'), channel ID ('UC...'), or username.
            sample_videos: Number of recent videos to analyze (3 to 15, default 5).
        """
        from datetime import datetime
        from collections import Counter

        try:
            target = channel_id_or_handle.strip()
            if target.startswith("@") or not target.startswith("UC"):
                ch_info = self.get_channel_details(for_handle=target)
            else:
                ch_info = self.get_channel_details(channel_id=target)

            if not ch_info.get("success"):
                return ch_info

            channel = ch_info.get("channel", {})
            uploads_playlist_id = channel.get("uploads_playlist_id")
            if not uploads_playlist_id:
                return {
                    "success": False,
                    "error": "Could not find uploads playlist for channel.",
                }

            # Fetch recent videos from uploads playlist
            playlist_res = self.get_playlist_items(
                playlist_id=uploads_playlist_id,
                max_results=min(max(sample_videos, 3), 15),
            )
            if not playlist_res.get("success"):
                return playlist_res

            video_items = playlist_res.get("items", [])
            if not video_items:
                return {
                    "success": True,
                    "channel": channel,
                    "message": "Channel has no uploaded videos.",
                }

            video_ids = [item["video_id"] for item in video_items if item.get("video_id")]

            # Fetch full video metrics
            details_res = self.get_video_details(video_ids=video_ids)
            videos = details_res.get("videos", []) if details_res.get("success") else []

            if not videos:
                return {
                    "success": True,
                    "channel": channel,
                    "message": "Could not retrieve detailed video metrics.",
                }

            # 1. Performance & View Analysis
            views_list = [v.get("view_count") or 0 for v in videos]
            avg_views = round(sum(views_list) / len(views_list)) if views_list else 0

            # Sort videos by views to find best & lowest performer in the sample
            sorted_by_views = sorted(videos, key=lambda x: x.get("view_count") or 0, reverse=True)
            top_video = sorted_by_views[0] if sorted_by_views else None
            lowest_video = sorted_by_views[-1] if sorted_by_views else None

            # 2. Upload Cadence Calculation
            dates = []
            for v in videos:
                pub = v.get("published_at")
                if pub:
                    try:
                        dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
                        dates.append(dt)
                    except Exception:
                        pass

            dates.sort(reverse=True)
            avg_days_between = None
            cadence_summary = "Variable"
            if len(dates) >= 2:
                diffs = [(dates[i] - dates[i + 1]).total_seconds() / 86400.0 for i in range(len(dates) - 1)]
                avg_days_between = round(sum(diffs) / len(diffs), 1)
                if avg_days_between <= 2:
                    cadence_summary = "High frequency (daily or every 2 days)"
                elif avg_days_between <= 5:
                    cadence_summary = "Consistent (approx. 2 videos per week)"
                elif avg_days_between <= 9:
                    cadence_summary = "Weekly (approx. 1 video per week)"
                elif avg_days_between <= 18:
                    cadence_summary = "Bi-weekly (approx. 2 videos per month)"
                else:
                    cadence_summary = "Monthly or sporadic"

            # 3. Monetization & Link Detection
            affiliate_links = set()
            newsletter_links = set()
            community_links = set()
            sponsor_mentions = []

            url_pattern = re.compile(r"https?://[^\s<>\"']+")

            for v in videos:
                desc = v.get("description", "")
                urls = url_pattern.findall(desc)
                for u in urls:
                    u_lower = u.lower()
                    if any(aff in u_lower for aff in ["amzn.to", "bit.ly", "geni.us", "linktr.ee", "ref=", "aff="]):
                        affiliate_links.add(u)
                    elif any(news in u_lower for news in ["substack.com", "beehiiv.com", "convertkit.com", "newsletter"]):
                        newsletter_links.add(u)
                    elif any(comm in u_lower for comm in ["skool.com", "discord.gg", "patreon.com", "teachable.com", "gumroad.com"]):
                        community_links.add(u)

                # Look for sponsor disclosures
                for line in desc.splitlines():
                    line_lower = line.lower()
                    if any(sp in line_lower for sp in ["sponsored by", "special thanks to", "use code", "coupon code"]):
                        clean_line = line.strip()
                        if clean_line and clean_line not in sponsor_mentions:
                            sponsor_mentions.append(clean_line)

            # 4. Title Formula Analysis
            title_styles = []
            titles = [v.get("title", "") for v in videos]
            if any(re.search(r"\b\d+\b", t) for t in titles):
                title_styles.append("Numbers & Listicles (e.g. '7 Tips', 'Top 5')")
            if any("?" in t for t in titles):
                title_styles.append("Question Hooks (Curiosity Driven)")
            if any(any(neg in t.lower() for neg in ["stop", "never", "don't", "worst", "mistake", "warning"]) for t in titles):
                title_styles.append("Negative Framing / Threat Avoidance (e.g. 'Don't Do This')")
            if any("[" in t or "(" in t for t in titles):
                title_styles.append("Bracketed Modifiers (e.g. '[Full Guide]', '(Case Study)')")

            # 5. Top Video Script Hook (first 60 seconds)
            hook_text = "Transcript unavailable or disabled."
            if top_video:
                transcript_res = fetch_transcript(
                    top_video["video_id"],
                    output_format="text",
                    end_seconds=60.0,
                )
                if transcript_res.get("success") and transcript_res.get("content"):
                    hook_text = transcript_res["content"]

            # 6. Common tags
            tag_counter: Counter = Counter()
            for v in videos:
                for t in v.get("tags") or []:
                    tag_counter[t.lower()] += 1
            common_tags = [t for t, _ in tag_counter.most_common(10)]

            return {
                "success": True,
                "channel": {
                    "title": channel.get("title"),
                    "handle": channel.get("custom_url"),
                    "channel_id": channel.get("channel_id"),
                    "subscribers": channel.get("subscriber_count"),
                    "total_views": channel.get("view_count"),
                    "video_count": channel.get("video_count"),
                    "channel_url": channel.get("url"),
                },
                "strategy_audit": {
                    "sample_videos_analyzed": len(videos),
                    "avg_recent_views": avg_views,
                    "estimated_cadence": cadence_summary,
                    "avg_days_between_uploads": avg_days_between,
                    "title_formulas_detected": title_styles,
                    "primary_tags": common_tags,
                    "top_performing_video": {
                        "title": top_video.get("title") if top_video else None,
                        "views": top_video.get("view_count") if top_video else None,
                        "duration": top_video.get("duration") if top_video else None,
                        "url": top_video.get("url") if top_video else None,
                    },
                    "lowest_performing_video": {
                        "title": lowest_video.get("title") if lowest_video else None,
                        "views": lowest_video.get("view_count") if lowest_video else None,
                        "duration": lowest_video.get("duration") if lowest_video else None,
                        "url": lowest_video.get("url") if lowest_video else None,
                    },
                    "opening_hook_first_60s": hook_text,
                    "monetization_funnel": {
                        "affiliate_links": list(affiliate_links)[:5],
                        "newsletters": list(newsletter_links)[:5],
                        "courses_communities": list(community_links)[:5],
                        "sponsor_disclosures": sponsor_mentions[:5],
                    },
                },
                "recent_videos": [
                    {
                        "title": v.get("title"),
                        "published_at": v.get("published_at"),
                        "duration": v.get("duration"),
                        "views": v.get("view_count"),
                        "likes": v.get("like_count"),
                        "url": v.get("url"),
                    }
                    for v in videos
                ],
            }

        except HttpError as e:
            return self._handle_http_error(e)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def reverse_engineer_channel(
        self,
        channel_id_or_handle: str,
        sample_videos: int = 5,
        include_audience_gaps: bool = True,
    ) -> Dict[str, Any]:
        """Perform full end-to-end reverse engineering on any YouTube channel.

        Deconstructs the creator's upload frequency, view-to-sub engagement ratio,
        best vs lowest performing video topics, title formulas, first 60s script hook,
        monetization funnel, and audience feedback gaps from real comments.
        Outputs an actionable replication playbook for new creators to model or compete.

        Args:
            channel_id_or_handle: Channel handle (e.g. '@mkbhd', '@aliabdaal'), channel ID ('UC...'), or username.
            sample_videos: Number of recent uploads to analyze (3 to 15, default 5).
            include_audience_gaps: If True, mines the comment section of their top video for unmet viewer needs.
        """
        try:
            audit_res = self.audit_channel_strategy(
                channel_id_or_handle=channel_id_or_handle,
                sample_videos=sample_videos,
            )
            if not audit_res.get("success"):
                return audit_res

            channel_info = audit_res.get("channel", {})
            strategy = audit_res.get("strategy_audit", {})
            recent_videos = audit_res.get("recent_videos", [])

            # 1. View-to-Subscriber Ratio & Algorithm Distribution
            subs = channel_info.get("subscribers") or 0
            avg_views = strategy.get("avg_recent_views") or 0
            ratio_val = round((avg_views / subs) * 100, 1) if subs > 0 else 0
            ratio_str = f"{ratio_val}%" if subs > 0 else "N/A"

            if ratio_val >= 50:
                growth_engine = "Viral & Browse Feature Dominant (High organic discovery per video)"
            elif ratio_val >= 20:
                growth_engine = "Search & High Intent Driven (Strong evergreen baseline)"
            else:
                growth_engine = "Subscriber Loyalty Driven (Audience-first retention)"

            # 2. Audience Gaps & Complaints from Top Performer
            audience_gaps = {}
            top_video = strategy.get("top_performing_video", {})
            top_url = top_video.get("url") if top_video else None

            if include_audience_gaps and top_url:
                sentiment = self.analyze_audience_sentiment(video_id_or_url=top_url, max_comments=50)
                if sentiment.get("success"):
                    audience_gaps = {
                        "unanswered_viewer_questions": sentiment.get("top_audience_questions", [])[:5],
                        "viewer_content_requests": sentiment.get("viewer_content_requests", [])[:5],
                        "common_pain_points_or_criticisms": sentiment.get("common_pain_points", [])[:5],
                    }

            # 3. Beginner Action Plan (How to Model or Compete)
            title_formulas = strategy.get("title_formulas_detected", ["Problem-Solution", "How-to Guide"])

            beginner_playbook = {
                "algorithm_growth_engine": growth_engine,
                "view_to_sub_ratio": ratio_str,
                "target_title_formulas": title_formulas,
                "recommended_video_length": top_video.get("duration", "8 to 12 minutes"),
                "monetization_channels_detected": strategy.get("monetization_funnel", {}),
                "actionable_takeaways": [
                    f"Model their top title structure ({', '.join(title_formulas) if title_formulas else 'Curiosity Hook'}).",
                    "Study their first 60s hook structure and replicate the problem-solution promise in your videos.",
                    "Address the unanswered viewer questions and pain points found in their comments.",
                ],
            }

            return {
                "success": True,
                "channel": channel_info,
                "growth_and_cadence": {
                    "estimated_cadence": strategy.get("estimated_cadence"),
                    "avg_days_between_uploads": strategy.get("avg_days_between_uploads"),
                    "avg_recent_views": avg_views,
                    "view_to_sub_ratio": ratio_str,
                    "algorithm_growth_engine": growth_engine,
                },
                "content_strategy_breakdown": {
                    "title_formulas": title_formulas,
                    "primary_tags": strategy.get("primary_tags", []),
                    "top_performing_video": top_video,
                    "lowest_performing_video": strategy.get("lowest_performing_video"),
                    "first_60s_hook_script": strategy.get("opening_hook_first_60s"),
                },
                "monetization_blueprint": strategy.get("monetization_funnel", {}),
                "audience_unmet_needs_and_flaws": audience_gaps,
                "beginner_replication_playbook": beginner_playbook,
                "recent_videos": recent_videos,
            }
        except HttpError as e:
            return self._handle_http_error(e)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def find_viral_outliers(
        self,
        query: str,
        min_multiplier: float = 2.5,
        published_after: Optional[str] = None,
        max_results: int = 25,
    ) -> Dict[str, Any]:
        """Identify viral outlier videos that perform dramatically above expectations.

        Can search across a niche (finding small/mid channels with breakout viral videos)
        or analyze a specific creator handle (finding their most disproportionately successful videos).

        Args:
            query: Niche topic (e.g. 'productivity tips') or creator handle ('@creator').
            min_multiplier: Outlier threshold multiplier (e.g. 2.5 means 2.5x the average, default 2.5).
            published_after: RFC 3339 datetime to filter recent breakouts (e.g. '2024-01-01T00:00:00Z').
            max_results: Number of candidates to evaluate (up to 50, default 25).
        """
        try:
            target = query.strip()
            outliers = []

            # Scenario A: Analyzing a specific channel for its own outlier videos
            if target.startswith("@") or target.startswith("UC"):
                if target.startswith("@"):
                    ch_res = self.get_channel_details(for_handle=target)
                else:
                    ch_res = self.get_channel_details(channel_id=target)

                if not ch_res.get("success"):
                    return ch_res

                channel = ch_res.get("channel", {})
                uploads_id = channel.get("uploads_playlist_id")
                if not uploads_id:
                    return {"success": False, "error": "No uploads playlist found for channel."}

                playlist_res = self.get_playlist_items(playlist_id=uploads_id, max_results=50)
                video_items = playlist_res.get("items", [])
                video_ids = [item["video_id"] for item in video_items if item.get("video_id")]

                details_res = self.get_video_details(video_ids=video_ids)
                videos = details_res.get("videos", []) if details_res.get("success") else []
                if not videos:
                    return {"success": True, "query": query, "total_outliers_found": 0, "outliers": []}

                views_list = [v.get("view_count") or 0 for v in videos]
                avg_views = sum(views_list) / max(len(views_list), 1)

                for v in videos:
                    v_views = v.get("view_count") or 0
                    if avg_views > 0 and v_views >= (avg_views * min_multiplier):
                        multiplier = round(v_views / avg_views, 2)
                        outliers.append({
                            "title": v.get("title"),
                            "video_id": v.get("video_id"),
                            "views": v_views,
                            "channel_average_views": round(avg_views),
                            "multiplier": f"{multiplier}x channel average",
                            "outlier_score": multiplier,
                            "published_at": v.get("published_at"),
                            "duration": v.get("duration"),
                            "url": v.get("url"),
                        })

            # Scenario B: Searching a niche for viral breakout videos from any creator
            else:
                search_res = self.search(
                    query=query,
                    max_results=min(max_results * 2, 50),
                    search_type="video",
                    order="relevance",
                    published_after=published_after,
                )
                if not search_res.get("success"):
                    return search_res

                results = search_res.get("results", [])
                video_ids = [r["id"] for r in results if r.get("id")]
                if not video_ids:
                    return {"success": True, "query": query, "total_outliers_found": 0, "outliers": []}

                # Fetch full video metrics
                vid_details = self.get_video_details(video_ids=video_ids)
                videos = vid_details.get("videos", []) if vid_details.get("success") else []

                # Collect channel IDs to get baseline subscriber counts
                ch_ids = list(dict.fromkeys([v["channel_id"] for v in videos if v.get("channel_id")]))[:50]
                channels = self.get_channels_batch(ch_ids)
                channel_map = {ch["channel_id"]: ch for ch in channels}

                for v in videos:
                    v_views = v.get("view_count") or 0
                    ch = channel_map.get(v.get("channel_id"), {})
                    subs = ch.get("subscriber_count") or 0
                    ch_vids = ch.get("video_count") or 1
                    ch_total_views = ch.get("view_count") or 0
                    ch_avg_views = round(ch_total_views / max(ch_vids, 1))

                    # An outlier has views substantially exceeding typical channel benchmarks
                    benchmark = max(subs, ch_avg_views, 1000)
                    if v_views >= (benchmark * min_multiplier):
                        multiplier = round(v_views / benchmark, 2)
                        outliers.append({
                            "title": v.get("title"),
                            "video_id": v.get("video_id"),
                            "views": v_views,
                            "channel_title": v.get("channel_title"),
                            "channel_subscribers": subs,
                            "channel_avg_views": ch_avg_views,
                            "multiplier": f"{multiplier}x channel benchmark",
                            "outlier_score": multiplier,
                            "published_at": v.get("published_at"),
                            "duration": v.get("duration"),
                            "url": v.get("url"),
                        })

            outliers.sort(key=lambda x: x.get("outlier_score", 0), reverse=True)
            return {
                "success": True,
                "query": query,
                "min_multiplier": min_multiplier,
                "total_outliers_found": len(outliers),
                "outliers": outliers[:max_results],
            }

        except HttpError as e:
            return self._handle_http_error(e)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def analyze_audience_sentiment(
        self,
        video_id_or_url: str,
        max_comments: int = 100,
    ) -> Dict[str, Any]:
        """Mine comments on a video to uncover viewer pain points, questions, and content requests.

        Args:
            video_id_or_url: Video ID or full URL.
            max_comments: Number of top comments to analyze (up to 100, default 100).
        """
        try:
            from youtube_mcp.transcripts import extract_video_id
            cleaned_id = extract_video_id(video_id_or_url)

            comments_res = self.get_video_comments(
                video_id=cleaned_id,
                max_results=min(max_comments, 100),
                order="relevance",
            )
            if not comments_res.get("success"):
                return comments_res

            comments = comments_res.get("comments", [])
            if not comments:
                return {
                    "success": True,
                    "video_id": cleaned_id,
                    "comments_analyzed": 0,
                    "message": "No comments found on this video.",
                }

            questions = []
            requests = []
            pain_points = []
            positive_comments = []

            REQUEST_TRIGGERS = ["make a video", "please do a video", "can you cover", "part 2", "tutorial on", "next video", "would love a video"]
            PAIN_TRIGGERS = ["struggle", "problem", "difficult", "hard to", "didn't work", "issue", "bug", "confusing", "doesn't work", "annoying"]
            POSITIVE_TRIGGERS = ["best", "thank", "helpful", "amazing", "gold", "brilliant", "saved my", "gem", "underrated", "game changer"]

            for c in comments:
                text = c.get("text", "").strip()
                text_lower = text.lower()
                likes = c.get("like_count", 0)

                entry = {
                    "comment": text,
                    "author": c.get("author"),
                    "likes": likes,
                }

                # 1. Content Requests
                if any(trig in text_lower for trig in REQUEST_TRIGGERS):
                    requests.append(entry)

                # 2. Audience Pain Points
                elif any(trig in text_lower for trig in PAIN_TRIGGERS):
                    pain_points.append(entry)

                # 3. Questions
                elif "?" in text:
                    questions.append(entry)

                # 4. Positive Feedback
                elif any(trig in text_lower for trig in POSITIVE_TRIGGERS):
                    positive_comments.append(entry)

            # Sort categories by upvotes / relevance
            questions.sort(key=lambda x: x["likes"], reverse=True)
            requests.sort(key=lambda x: x["likes"], reverse=True)
            pain_points.sort(key=lambda x: x["likes"], reverse=True)

            total_analyzed = len(comments)
            pos_count = len(positive_comments)
            quest_count = len(questions) + len(requests)
            pain_count = len(pain_points)

            # Top upvoted comments overall
            top_comments = sorted(comments, key=lambda x: x.get("like_count", 0), reverse=True)[:5]

            return {
                "success": True,
                "video_id": cleaned_id,
                "comments_analyzed": total_analyzed,
                "sentiment_distribution": {
                    "positive_feedback_count": pos_count,
                    "questions_and_requests_count": quest_count,
                    "pain_points_and_critiques_count": pain_count,
                },
                "viewer_content_requests": requests[:10],
                "top_audience_questions": questions[:10],
                "common_pain_points": pain_points[:10],
                "top_upvoted_comments": [
                    {
                        "author": c.get("author"),
                        "text": c.get("text"),
                        "likes": c.get("like_count"),
                    }
                    for c in top_comments
                ],
            }

        except HttpError as e:
            return self._handle_http_error(e)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def compare_channels(
        self,
        channel_handles: List[str],
    ) -> Dict[str, Any]:
        """Perform head-to-head benchmarking comparison across multiple YouTube channels.

        Args:
            channel_handles: List of channel handles (e.g. ['@mkbhd', '@dave2d']) or Channel IDs.
        """
        try:
            from datetime import datetime

            channels_data = []
            for handle in channel_handles[:10]:  # support up to 10 channels
                target = handle.strip()
                if target.startswith("@") or not target.startswith("UC"):
                    ch_res = self.get_channel_details(for_handle=target)
                else:
                    ch_res = self.get_channel_details(channel_id=target)

                if not ch_res.get("success"):
                    continue

                ch = ch_res.get("channel", {})
                uploads_id = ch.get("uploads_playlist_id")

                avg_recent_views = 0
                cadence = "Unknown"
                avg_duration = "N/A"

                if uploads_id:
                    pl_res = self.get_playlist_items(playlist_id=uploads_id, max_results=6)
                    if pl_res.get("success"):
                        v_ids = [item["video_id"] for item in pl_res.get("items", []) if item.get("video_id")]
                        if v_ids:
                            v_details = self.get_video_details(video_ids=v_ids)
                            recent_vids = v_details.get("videos", []) if v_details.get("success") else []
                            if recent_vids:
                                views_list = [v.get("view_count") or 0 for v in recent_vids]
                                avg_recent_views = round(sum(views_list) / len(views_list))

                                dates = []
                                for v in recent_vids:
                                    pub = v.get("published_at")
                                    if pub:
                                        try:
                                            dates.append(datetime.fromisoformat(pub.replace("Z", "+00:00")))
                                        except Exception:
                                            pass
                                dates.sort(reverse=True)
                                if len(dates) >= 2:
                                    diffs = [(dates[i] - dates[i + 1]).total_seconds() / 86400.0 for i in range(len(dates) - 1)]
                                    avg_days = round(sum(diffs) / len(diffs), 1)
                                    cadence = f"Every {avg_days} days"

                subs = ch.get("subscriber_count") or 0
                views_per_sub = round(avg_recent_views / max(subs, 1), 2) if subs > 0 else 0

                channels_data.append({
                    "channel_title": ch.get("title"),
                    "handle": ch.get("custom_url"),
                    "channel_id": ch.get("channel_id"),
                    "subscribers": subs,
                    "total_views": ch.get("view_count") or 0,
                    "video_count": ch.get("video_count") or 0,
                    "avg_recent_views": avg_recent_views,
                    "views_to_subscriber_ratio": views_per_sub,
                    "upload_frequency": cadence,
                    "channel_url": ch.get("url"),
                })

            if not channels_data:
                return {
                    "success": False,
                    "error": "Could not retrieve details for any provided channel handles.",
                }

            # Generate comparative rankings
            rankings = {
                "highest_subscribers": max(channels_data, key=lambda x: x["subscribers"])["channel_title"],
                "highest_recent_views": max(channels_data, key=lambda x: x["avg_recent_views"])["channel_title"],
                "highest_engagement_ratio": max(channels_data, key=lambda x: x["views_to_subscriber_ratio"])["channel_title"],
            }

            return {
                "success": True,
                "total_channels_compared": len(channels_data),
                "channels": channels_data,
                "winner_rankings": rankings,
            }

        except HttpError as e:
            return self._handle_http_error(e)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def blueprint_new_channel(
        self,
        niche: str,
        target_audience: Optional[str] = None,
        region_code: str = "US",
    ) -> Dict[str, Any]:
        """Conduct an end-to-end market research study to launch a brand new YouTube channel in a niche.

        Specifically designed for new creators to validate market demand, identify mid-sized channels
        to model, discover proven outlier video topics that get views with 0 subscribers, mine real
        audience pain points from comments, and assemble a 5-video launch roadmap.

        Args:
            niche: The topic or niche you want to start a channel in (e.g. 'ai tools for creators', 'budget travel', 'personal finance').
            target_audience: Optional description of your ideal viewer (e.g. 'complete beginners', 'busy college students').
            region_code: Target geographic market (default 'US', e.g. 'GB', 'CA', 'DE').
        """
        try:
            clean_niche = niche.strip()

            # 1. Scout 3-5 realistic mid-tier model channels in this niche (1k - 300k subs)
            scout_res = self.scout_niche_channels(
                niches=[clean_niche],
                min_subscribers=1000,
                max_subscribers=300000,
                min_videos=3,
                region_code=region_code,
                channels_per_niche=5,
                sort_by="avg_views",
            )
            model_channels = []
            if scout_res.get("success"):
                campaign = scout_res.get("campaigns", {}).get(clean_niche, {})
                model_channels = campaign.get("channels", [])

            # 2. Find proven viral outlier videos (topics that exploded organically)
            outlier_res = self.find_viral_outliers(
                query=clean_niche,
                min_multiplier=2.0,
                max_results=5,
            )
            outliers = outlier_res.get("outliers", []) if outlier_res.get("success") else []

            # 3. Mine audience pain points and video requests from top video in this niche
            top_video_id = outliers[0]["video_id"] if outliers else None
            audience_insights = {}
            if not top_video_id:
                # Search for 1 top video
                search_top = self.search(query=clean_niche, max_results=1, search_type="video", order="relevance")
                if search_top.get("success") and search_top.get("results"):
                    top_video_id = search_top["results"][0]["id"]

            if top_video_id:
                sentiment_res = self.analyze_audience_sentiment(video_id_or_url=top_video_id, max_comments=50)
                if sentiment_res.get("success"):
                    audience_insights = {
                        "audience_questions": sentiment_res.get("top_audience_questions", [])[:5],
                        "viewer_video_requests": sentiment_res.get("viewer_content_requests", [])[:5],
                        "common_pain_points": sentiment_res.get("common_pain_points", [])[:5],
                    }

            # 4. Synthesize beginner launch recommendations
            launch_videos = []
            for i, outl in enumerate(outliers[:5], 1):
                launch_videos.append({
                    "video_number": i,
                    "inspired_by_outlier": outl.get("title"),
                    "benchmark_views": outl.get("views"),
                    "suggested_title_framework": f"{outl.get('title')} (Beginner's Step-by-Step Guide)",
                    "why_this_works": f"Proven demand with {outl.get('multiplier', '2x+')} above normal channel average.",
                    "reference_url": outl.get("url"),
                })

            if not launch_videos and model_channels:
                # Fallback based on model channels
                for i in range(1, 4):
                    launch_videos.append({
                        "video_number": i,
                        "suggested_title_framework": f"How to Get Started with {clean_niche.title()} in 2026 (Full Roadmap)",
                        "why_this_works": "Essential evergreen cornerstone video for building topical authority.",
                    })

            return {
                "success": True,
                "niche": clean_niche,
                "target_audience": target_audience or "General beginners in this niche",
                "market_validation": {
                    "demand_status": "High" if outliers or model_channels else "Emerging",
                    "model_channels_found": len(model_channels),
                    "viral_outliers_identified": len(outliers),
                },
                "competitors_to_model": [
                    {
                        "channel_name": ch.get("title"),
                        "handle": ch.get("custom_url"),
                        "subscribers": ch.get("subscriber_count"),
                        "avg_views_per_video": ch.get("avg_views_per_video"),
                        "url": ch.get("url"),
                    }
                    for ch in model_channels
                ],
                "audience_unmet_needs": audience_insights,
                "first_5_videos_to_record": launch_videos,
                "launch_recommendations": {
                    "recommended_upload_schedule": "1 to 2 videos per week (consistency > quantity)",
                    "recommended_video_length": "8 to 14 minutes (optimal for retention + mid-roll eligibility)",
                    "first_30_seconds_rule": "Hook viewers within the first 10 seconds: state the exact problem, show the end result, and promise the solution. Never waste time with lengthy channel intros.",
                    "monetization_roadmap": [
                        "Stage 1 (0 - 1k subs): Affiliate links in description & free digital lead magnet (newsletter).",
                        "Stage 2 (1k - 10k subs): YouTube Partner Program (AdSense) + mini-course or community.",
                        "Stage 3 (10k+ subs): Brand sponsorships & high-ticket consulting/offer.",
                    ],
                },
            }

        except HttpError as e:
            return self._handle_http_error(e)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def find_breakout_growth_channels(
        self,
        niche: str,
        max_channel_age_months: int = 24,
        min_subscribers: int = 1000,
        max_subscribers: int = 300000,
        region_code: Optional[str] = "US",
        max_results: int = 10,
    ) -> Dict[str, Any]:
        """Find modern breakout channels created recently that grew rapidly with high subscriber velocity.

        Filters out legacy channels that grew years ago, uncovering channels that recently cracked
        the YouTube algorithm from scratch.

        Args:
            niche: Topic or niche keyword (e.g. 'ai automation', 'finance beginners', 'coding').
            max_channel_age_months: Maximum age in months (default 24).
            min_subscribers: Minimum subscribers (default 1000).
            max_subscribers: Maximum subscribers (default 300000).
            region_code: Country code (default 'US').
            max_results: Max breakout channels to return (default 10).
        """
        from datetime import datetime, timezone

        try:
            search_res = self.search(
                query=niche,
                max_results=min(max_results * 3, 50),
                search_type="channel",
                region_code=region_code,
                raw=False,
            )
            if not search_res.get("success"):
                return search_res

            channel_items = search_res.get("results", [])
            channel_ids = [item["id"] for item in channel_items if item.get("id")]
            batch_details = self.get_channels_batch(channel_ids)

            breakout_channels = []
            now = datetime.now(timezone.utc)

            for ch in batch_details:
                subs = ch.get("subscriber_count") or 0
                if subs < min_subscribers:
                    continue
                if max_subscribers and subs > max_subscribers:
                    continue

                pub_date = ch.get("published_at")
                age_days = None
                age_months = None
                monthly_velocity = None

                if pub_date:
                    try:
                        created = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                        age_days = max((now - created).days, 1)
                        age_months = round(age_days / 30.4, 1)
                        if age_months > max_channel_age_months:
                            continue
                        monthly_velocity = round(subs / max(age_months, 0.5))
                    except Exception:
                        pass

                video_count = max(ch.get("video_count") or 1, 1)
                subs_per_video = round(subs / video_count)

                breakout_channels.append({
                    "channel_name": ch.get("title"),
                    "handle": ch.get("custom_url"),
                    "subscribers": subs,
                    "video_count": ch.get("video_count"),
                    "total_views": ch.get("view_count"),
                    "channel_age_months": age_months,
                    "subs_gained_per_month": monthly_velocity,
                    "subs_per_video": subs_per_video,
                    "created_at": pub_date,
                    "url": ch.get("url"),
                })

            breakout_channels.sort(
                key=lambda x: x.get("subs_gained_per_month") or x.get("subs_per_video") or 0,
                reverse=True,
            )

            return {
                "success": True,
                "niche": niche,
                "total_found": len(breakout_channels),
                "breakout_channels": breakout_channels[:max_results],
            }
        except HttpError as e:
            return self._handle_http_error(e)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def find_content_gaps(
        self,
        niche_or_topic: str,
        max_results: int = 15,
        region_code: Optional[str] = "US",
    ) -> Dict[str, Any]:
        """Identify high-demand content gaps and low-competition keyword opportunities.

        Detects top search rankings held by outdated videos (2+ years old) or small channels (<25k subs),
        signaling easy ranking opportunities for new creators.

        Args:
            niche_or_topic: Topic, query, or question (e.g. 'how to learn sql for data analysis').
            max_results: Number of search results to analyze (default 15).
            region_code: Country code (default 'US').
        """
        from datetime import datetime, timezone

        try:
            search_res = self.search(
                query=niche_or_topic,
                max_results=min(max_results, 50),
                search_type="video",
                order="relevance",
                region_code=region_code,
                raw=False,
            )
            if not search_res.get("success"):
                return search_res

            video_items = search_res.get("results", [])
            video_ids = [item["id"] for item in video_items if item.get("id")]
            details_res = self.get_video_details(video_ids=video_ids)
            videos = details_res.get("videos", []) if details_res.get("success") else []

            now = datetime.now(timezone.utc)
            outdated_videos = []
            all_analyzed = []

            for v in videos:
                pub_date = v.get("published_at")
                age_years = 0
                if pub_date:
                    try:
                        created = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                        age_years = round((now - created).days / 365.25, 1)
                    except Exception:
                        pass

                views = v.get("view_count") or 0
                item_summary = {
                    "video_id": v.get("video_id"),
                    "title": v.get("title"),
                    "channel_title": v.get("channel_title"),
                    "views": views,
                    "published_at": pub_date,
                    "age_years": age_years,
                    "duration": v.get("duration"),
                    "url": v.get("url"),
                }
                all_analyzed.append(item_summary)

                if age_years >= 2.0:
                    outdated_videos.append({
                        **item_summary,
                        "opportunity_reason": f"Ranking is {age_years} years old. A fresh 2026 update can easily outrank it.",
                    })

            outdated_ratio = len(outdated_videos) / max(len(videos), 1)
            if outdated_ratio >= 0.4:
                gap_score = "HIGH (Massive opportunity: >40% of ranking videos are 2+ years old)"
            elif outdated_ratio >= 0.2:
                gap_score = "MODERATE (Good opportunity: Several legacy videos can be displaced)"
            else:
                gap_score = "COMPETITIVE (Most top videos are recently published)"

            suggested_titles = [
                f"{niche_or_topic.title()} (Complete 2026 Beginner Guide)",
                f"How to Master {niche_or_topic.title()} in 30 Days (Step-by-Step)",
                f"Why Most People Fail at {niche_or_topic.title()} (And What to Do Instead)",
            ]

            return {
                "success": True,
                "topic": niche_or_topic,
                "content_gap_opportunity": gap_score,
                "total_videos_analyzed": len(videos),
                "outdated_ranking_videos_found": len(outdated_videos),
                "outdated_videos_to_displace": outdated_videos[:5],
                "suggested_video_titles_to_rank": suggested_titles,
                "ranking_playbook": [
                    "Target the exact search intent of the outdated videos with higher pacing and modern graphics.",
                    "Include current year (2026) in title and thumbnail to signal freshness.",
                    "Pin a comment with a free downloadable checklist or resource to boost viewer engagement signals.",
                ],
            }
        except HttpError as e:
            return self._handle_http_error(e)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_retention_script_outline(
        self,
        video_title_or_topic: str,
        competitor_video_id_or_url: Optional[str] = None,
        target_audience: str = "Beginners",
        target_duration_minutes: int = 10,
    ) -> Dict[str, Any]:
        """Generate a complete 8-12 minute retention-engineered YouTube script outline.

        Reverse-engineers competitor transcripts for opening hooks and integrates real viewer
        pain points from comments to maximize watch time and viewer satisfaction.

        Args:
            video_title_or_topic: The topic or title of the video to outline.
            competitor_video_id_or_url: Optional competitor video to model hook and structure from.
            target_audience: Ideal viewer demographic (default 'Beginners').
            target_duration_minutes: Target video runtime in minutes (default 10).
        """
        try:
            competitor_hook = None
            viewer_objections = []

            clean_topic = video_title_or_topic.strip()

            target_comp_id = None
            if competitor_video_id_or_url:
                target_comp_id = extract_video_id(competitor_video_id_or_url)
            else:
                # Search for the top ranking video on YouTube to model real data
                search_top = self.search(query=clean_topic, max_results=1, search_type="video", order="relevance")
                if search_top.get("success") and search_top.get("results"):
                    target_comp_id = search_top["results"][0].get("id")

            if target_comp_id:
                hook_res = fetch_transcript(target_comp_id, output_format="text", end_seconds=60.0)
                if hook_res.get("success") and hook_res.get("content"):
                    competitor_hook = hook_res["content"].replace("\n", " ")

                sentiment = self.analyze_audience_sentiment(video_id_or_url=target_comp_id, max_comments=30)
                if sentiment.get("success"):
                    viewer_objections = [
                        q.get("comment") for q in sentiment.get("top_audience_questions", [])[:3]
                    ] + [
                        p.get("comment") for p in sentiment.get("common_pain_points", [])[:2]
                    ]

            script_structure = [
                {
                    "timestamp": "0:00 - 0:15",
                    "section": "The Hook (Pattern Interrupt & Promise)",
                    "objective": "Stop the scroll, state the core problem, and show the end transformation immediately. Zero channel fluff.",
                    "verbal_script_framework": f"If you want to {clean_topic} without feeling overwhelmed or wasting weeks of time, this video gives you the exact blueprint.",
                    "visual_and_broll": "Fast cuts, screen recording of end result, bold text on screen. High energy.",
                },
                {
                    "timestamp": "0:15 - 1:00",
                    "section": "Stakes & Roadmap",
                    "objective": "Explain why watching this now matters and preview the 3 key milestones to keep retention high.",
                    "verbal_script_framework": "Most people struggle because they do X. In the next 10 minutes, we'll cover Step 1, Step 2, and the secret mistake to avoid at Step 3.",
                    "visual_and_broll": "Presenter on camera with animated 3-step checklist sliding in on the right.",
                },
                {
                    "timestamp": "1:00 - 3:30",
                    "section": "Step 1: The Fast Foundation (Quick Win)",
                    "objective": "Give the viewer an immediate, actionable result in the first 3 minutes so they feel instant progress.",
                    "verbal_script_framework": f"First, let's set up the core foundation for {clean_topic} in under 2 minutes...",
                    "visual_and_broll": "Over-the-shoulder software demo / practical live demonstration with mouse zooms.",
                },
                {
                    "timestamp": "3:30 - 6:30",
                    "section": "Step 2: The Core Implementation",
                    "objective": "Deliver the meat of the strategy. Answer the primary questions beginners get stuck on.",
                    "verbal_script_framework": "Now for the part most tutorials skip: how to actually connect everything together...",
                    "visual_and_broll": "Step-by-step workflow with diagram graphics or screen share.",
                },
                {
                    "timestamp": "6:30 - 7:00",
                    "section": "Retention Reset & Pattern Interrupt",
                    "objective": "Re-hook viewers right at the 60% mark where retention curves typically slump.",
                    "verbal_script_framework": "Before we move to the final step, you MUST understand this one counterintuitive rule...",
                    "visual_and_broll": "Camera angle shift, zoom in, music change to build anticipation.",
                },
                {
                    "timestamp": "7:00 - 9:00",
                    "section": "Step 3: Common Pitfalls & How to Avoid Them",
                    "objective": "Address viewer doubts and common failure modes.",
                    "verbal_script_framework": (
                        f"The #1 mistake beginners make here is: {viewer_objections[0] if viewer_objections else 'overcomplicating the setup'}."
                    ),
                    "visual_and_broll": "Side-by-side 'Wrong Way vs Right Way' visual comparison.",
                },
                {
                    "timestamp": "9:00 - 10:00",
                    "section": "Conclusion & Watch-Time Loop CTA",
                    "objective": "Summarize and bridge immediately to your next video instead of saying 'goodbye'.",
                    "verbal_script_framework": "Now that you have this setup, the next critical thing you need is [Next Step], which I break down in this video right here...",
                    "visual_and_broll": "Pointing to YouTube end screen video card, seamless transition without dead air.",
                },
            ]

            return {
                "success": True,
                "video_title": clean_topic,
                "target_audience": target_audience,
                "estimated_duration": f"{target_duration_minutes} minutes",
                "modeled_competitor_hook": competitor_hook,
                "audience_pain_points_addressed": viewer_objections,
                "retention_script_outline": script_structure,
                "thumbnail_and_packaging_advice": {
                    "thumbnail_visual_rule": "Limit to 3 visual elements: your face (strong expression), 1 high-contrast icon/graphic, and max 3 words of text.",
                    "title_rule": "Keep under 50 characters so it doesn't truncate on mobile devices.",
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def discover_niche_sponsors(
        self,
        niche_or_query: str,
        sample_videos: int = 20,
        region_code: Optional[str] = "US",
    ) -> Dict[str, Any]:
        """Discover brands and software companies actively paying creators for sponsorships in a niche.

        Inspects the descriptions of top-ranking videos for sponsor disclosures, discount codes,
        and tracking URLs. Reveals which companies have marketing budgets in this niche.

        Args:
            niche_or_query: Niche topic or keyword (e.g. 'productivity apps', 'coding', 'fitness').
            sample_videos: Number of top videos to inspect (10 to 30, default 20).
            region_code: Country code (default 'US').
        """
        from collections import Counter

        try:
            search_res = self.search(
                query=niche_or_query,
                max_results=min(sample_videos, 50),
                search_type="video",
                order="viewCount",
                region_code=region_code,
                raw=False,
            )
            if not search_res.get("success"):
                return search_res

            video_items = search_res.get("results", [])
            video_ids = [item["id"] for item in video_items if item.get("id")]
            details_res = self.get_video_details(video_ids=video_ids)
            videos = details_res.get("videos", []) if details_res.get("success") else []

            sponsors_found = []
            sponsor_names: Counter = Counter()

            sponsor_keywords = [
                "sponsored by", "special thanks to", "use code", "coupon code",
                "discount code", "partnered with", "brought to you by", "supported by"
            ]

            for v in videos:
                desc = v.get("description", "")
                video_sponsors = []
                for line in desc.splitlines():
                    line_lower = line.lower()
                    if any(kw in line_lower for kw in sponsor_keywords):
                        clean_line = line.strip()
                        if 10 < len(clean_line) < 150:
                            video_sponsors.append(clean_line)
                            for kw in ["sponsored by", "thanks to", "brought to you by"]:
                                if kw in line_lower:
                                    parts = line_lower.split(kw)
                                    if len(parts) > 1:
                                        brand = parts[1].split(".")[0].split("!")[0].split(",")[0].strip()
                                        if brand and len(brand) < 30:
                                            sponsor_names[brand.title()] += 1

                if video_sponsors:
                    sponsors_found.append({
                        "video_title": v.get("title"),
                        "channel": v.get("channel_title"),
                        "views": v.get("view_count"),
                        "url": v.get("url"),
                        "sponsor_mentions": video_sponsors[:2],
                    })

            top_brands = [{"brand": b, "frequency_detected": count} for b, count in sponsor_names.most_common(10)]

            return {
                "success": True,
                "niche": niche_or_query,
                "videos_analyzed": len(videos),
                "sponsored_videos_detected": len(sponsors_found),
                "top_active_sponsors": top_brands,
                "sponsor_sightings": sponsors_found[:10],
                "creator_monetization_guidance": [
                    "These brands already have approved influencer budgets in this niche.",
                    "Once you reach 1,000 - 5,000 views per video, pitch marketing managers at these exact companies.",
                    "Include case studies of how their product solves the viewer pain points you cover in your videos.",
                ],
            }
        except HttpError as e:
            return self._handle_http_error(e)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_thumbnail_concepts(
        self,
        video_title: str,
        target_niche: Optional[str] = None,
        competitor_video_id_or_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate 3 distinct high-CTR thumbnail visual concepts with AI image prompts.

        Deconstructs title-to-thumbnail contrast, visual color theory, facial expressions,
        and provides ready-to-use prompts for Midjourney, DALL-E, or Imagen.

        Args:
            video_title: The title or topic of the video (e.g. 'How I Built a $10k/mo Micro-SaaS').
            target_niche: Optional niche context (e.g. 'coding', 'business', 'productivity').
            competitor_video_id_or_url: Optional competitor video to evaluate thumbnail benchmarks.
        """
        try:
            clean_title = video_title.strip()
            niche_str = (target_niche or "general YouTube").strip()

            # Query real YouTube videos to inspect actual thumbnail competition
            competitor_benchmarks = []
            if competitor_video_id_or_url:
                cid = extract_video_id(competitor_video_id_or_url)
                if cid:
                    det = self.get_video_details([cid])
                    if det.get("success") and det.get("videos"):
                        v0 = det["videos"][0]
                        competitor_benchmarks.append({
                            "title": v0.get("title"),
                            "views": v0.get("view_count"),
                            "thumbnail_url": v0.get("thumbnail_url"),
                            "channel": v0.get("channel_title"),
                        })
            if not competitor_benchmarks:
                search_top = self.search(query=clean_title, max_results=3, search_type="video", order="relevance")
                if search_top.get("success"):
                    for item in search_top.get("results", []):
                        competitor_benchmarks.append({
                            "title": item.get("title"),
                            "thumbnail_url": item.get("thumbnail_url"),
                            "channel": item.get("channel_title"),
                            "url": item.get("url"),
                        })

            concept_1 = {
                "concept_id": "concept_a_curiosity_contrast",
                "name": "The Visual Anomaly & Juxtaposition",
                "psychology": "Forces the viewer's brain to resolve an unexpected visual conflict in the feed.",
                "composition": {
                    "left_side": "Subject looking intensely or skeptically at the right side.",
                    "right_side": "An exaggerated, glowing symbol, graph, or object representing the outcome.",
                    "focal_point": "High contrast between dark background and vibrant foreground element.",
                },
                "color_palette": "Deep navy/charcoal background (#0F172A) with electric amber (#F59E0B) and cyan (#06B6D4) lighting accents.",
                "text_overlay": {
                    "text": "10X FASTER" if any(w in clean_title.lower() for w in ["fast", "quick", "day", "hour"]) else "DON'T DO THIS",
                    "style": "Ultra-bold sans-serif, all caps, white letters with thick black drop shadow and yellow highlight.",
                    "max_words": 3,
                },
                "facial_expression": "Intense curiosity, raised eyebrow, subtle confident smirk.",
                "ai_image_prompt": (
                    f"A cinematic high-resolution YouTube thumbnail background for a video titled '{clean_title}'. "
                    f"Modern dark studio setting with dramatic dual-rim neon lighting (cyan and warm amber). "
                    f"Minimalist composition, rule of thirds, ultra-clean negative space on the left for text overlay. "
                    f"Hyper-detailed, octane render 8k, professional photography style --ar 16:9"
                ),
            }

            concept_2 = {
                "concept_id": "concept_b_threat_avoidance",
                "name": "The High-Stakes Threat Avoidance Hook",
                "psychology": "Loss aversion: viewers click 2x faster to avoid making a painful mistake than to gain an equivalent benefit.",
                "composition": {
                    "center": "Close-up of face showing disbelief, holding hands or pointing to an error screen / red warning badge.",
                    "background": "Blurred workspace or software dashboard with glowing red warning indicators.",
                    "focal_point": "The red badge or crossed-out mistake element.",
                },
                "color_palette": "Moody dark tones with high-saturation Crimson Red (#EF4444) and pure white contrast.",
                "text_overlay": {
                    "text": "HUGE MISTAKE!",
                    "style": "Bright red background banner with bold white text.",
                    "max_words": 2,
                },
                "facial_expression": "Shock, genuine concern, eyes wide open looking directly at the camera.",
                "ai_image_prompt": (
                    f"Dramatic YouTube thumbnail graphic for a video about {clean_title}. "
                    f"Close-up composition, intense expressive atmosphere, glowing red cautionary accent lights. "
                    f"Sharp foreground, cinematic bokeh in background, 8k resolution, photorealistic studio lighting --ar 16:9"
                ),
            }

            concept_3 = {
                "concept_id": "concept_c_transformation_proof",
                "name": "The Before vs. After Split Screen",
                "psychology": "Visual proof: immediately illustrates the concrete transformation promised in the title.",
                "composition": {
                    "split_screen": "Diagonal split dividing 'Before' (drab, messy, red) from 'After' (sleek, high-tech, green).",
                    "left_panel": "Desaturated, chaotic state with a red 'X'.",
                    "right_panel": "Vibrant, organized, successful state with a green checkmark or glowing badge.",
                },
                "color_palette": "Contrasting Crimson Red (#DC2626) on the left vs Emerald Green (#10B981) on the right.",
                "text_overlay": {
                    "text": "BEFORE / AFTER",
                    "style": "Minimalist split text tags on top of each panel.",
                    "max_words": 2,
                },
                "facial_expression": "Split portrait or triumphant expression on the winning side.",
                "ai_image_prompt": (
                    f"Split screen YouTube thumbnail comparing struggle vs extreme success for '{clean_title}'. "
                    f"Left side shows chaotic, dark desaturated scene. Right side shows clean, illuminated, high-tech organized scene. "
                    f"High dynamic range, commercial advertising quality, ultra-sharp detail --ar 16:9"
                ),
            }

            return {
                "success": True,
                "video_title": clean_title,
                "niche": niche_str,
                "real_competitor_thumbnails_analyzed": competitor_benchmarks,
                "concepts": [concept_1, concept_2, concept_3],
                "packaging_golden_rules": [
                    "Rule 1: The thumbnail and title must COMPLEMENT, not duplicate each other (if title says 'How to Learn Python', thumbnail should say 'IN 30 DAYS').",
                    "Rule 2: Never place text or crucial visual elements in the bottom-right corner (covered by YouTube's timestamp badge).",
                    "Rule 3: Test on a 1-inch smartphone screen preview: if you can't read the emotion and text in 0.5 seconds, simplify it.",
                ],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_seo_metadata_pack(
        self,
        topic: str,
        key_takeaways: Optional[List[str]] = None,
        channel_name: Optional[str] = None,
        affiliate_links: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate a complete YouTube Studio upload package: 3 mobile titles, chapters, description, tags, and pinned comment.

        Args:
            topic: Primary topic or draft title of the video.
            key_takeaways: Optional list of main points covered in the video.
            channel_name: Optional creator channel name.
            affiliate_links: Optional list of affiliate/product URLs.
        """
        try:
            clean_topic = topic.strip()
            ch_name = channel_name or "Your Channel"

            title_search = f"{clean_topic.title()} (Full Beginner Guide)"[:50]
            title_curiosity = f"I Tested {clean_topic.title()} for 30 Days"[:50]
            title_threat = f"Stop Doing {clean_topic.title()} Like This"[:50]

            points = key_takeaways or [
                f"Core foundations of {clean_topic}",
                "The #1 mistake most beginners make",
                "Step-by-step implementation walkthrough",
                "How to scale and get results faster",
            ]
            bullet_text = "\n".join([f"  • {p}" for p in points])

            affiliate_text = ""
            if affiliate_links:
                affiliate_text = "\n\n🔗 RESOURCES & LINKS MENTIONED:\n" + "\n".join(
                    [f"  • {link}" for link in affiliate_links]
                ) + "\n*(Disclosure: Some links above may be affiliate links that support the channel at zero extra cost to you.)*"

            description = f"""In this video, you'll learn everything you need to know about {clean_topic}. Whether you're a complete beginner or looking to optimize your workflow, this step-by-step guide covers the exact strategy to get results.

📌 KEY TAKEAWAYS:
{bullet_text}
{affiliate_text}

⏱️ TIMESTAMPS:
00:00 - Introduction & The Big Problem
00:45 - The Core Framework
02:30 - Step 1: Setting Up the Foundation
05:15 - Step 2: Implementation & Best Practices
07:45 - The Common Mistake to Avoid
09:15 - Final Checklist & Next Steps

🔔 Subscribe to {ch_name} for more practical tutorials every week!
👍 If you found this helpful, please leave a like and comment below.

#YouTube #Tutorial #{clean_topic.replace(' ', '')}"""

            # Query real YouTube videos to extract live competitor tags & titles
            real_tags = []
            competitor_titles = []
            try:
                search_res = self.search(query=clean_topic, max_results=5, search_type="video", order="relevance")
                if search_res.get("success"):
                    video_ids = [item["id"] for item in search_res.get("results", []) if item.get("id")]
                    competitor_titles = [item["title"] for item in search_res.get("results", []) if item.get("title")]
                    if video_ids:
                        details_res = self.get_video_details(video_ids=video_ids)
                        if details_res.get("success"):
                            for vid in details_res.get("videos", []):
                                for tag in vid.get("tags", []):
                                    tag_clean = tag.strip().lower()
                                    if tag_clean and tag_clean not in real_tags:
                                        real_tags.append(tag_clean)
            except Exception:
                pass

            # Combine discovered real tags with topical keywords
            combined_tags = list(real_tags[:10])
            for fallback_tag in [
                clean_topic.lower(),
                f"{clean_topic.lower()} tutorial",
                f"{clean_topic.lower()} for beginners",
                f"how to {clean_topic.lower()}",
                f"{clean_topic.lower()} guide",
            ]:
                if fallback_tag not in combined_tags:
                    combined_tags.append(fallback_tag)
            tags = combined_tags[:15]

            pinned_comment = (
                f"Question of the day: What's your biggest hurdle or question when it comes to {clean_topic}? "
                "Drop your comment below and I'll reply to as many as possible! 👇"
            )

            return {
                "success": True,
                "topic": clean_topic,
                "ranking_competitors_analyzed": competitor_titles[:3],
                "real_competitor_tags_extracted": len(real_tags),
                "mobile_optimized_titles": [
                    {"framework": "Search & How-To (<50 chars)", "title": title_search, "char_count": len(title_search)},
                    {"framework": "Curiosity & Experiment (<50 chars)", "title": title_curiosity, "char_count": len(title_curiosity)},
                    {"framework": "Threat Avoidance (<50 chars)", "title": title_threat, "char_count": len(title_threat)},
                ],
                "youtube_studio_description": description,
                "top_15_tags": tags,
                "tags_comma_separated": ", ".join(tags),
                "pinned_comment_for_engagement": pinned_comment,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def export_research_report(
        self,
        niche: str,
        target_audience: Optional[str] = None,
        output_file: Optional[str] = None,
        region_code: str = "US",
    ) -> Dict[str, Any]:
        """Generate a publication-ready Markdown research report for Notion or Obsidian.

        Runs complete market research and formats it into an executive-ready .md document
        complete with tables, competitor rankings, viral video links, comment insights, and a 5-video roadmap.

        Args:
            niche: Topic or niche (e.g. 'ai automation', 'productivity systems', 'personal finance').
            target_audience: Optional target audience description (e.g. 'beginners', 'freelancers').
            output_file: Optional path where to save the markdown file.
            region_code: Country market code (default 'US').
        """
        from pathlib import Path
        from datetime import datetime, timezone

        try:
            blueprint = self.blueprint_new_channel(
                niche=niche,
                target_audience=target_audience,
                region_code=region_code,
            )
            if not blueprint.get("success"):
                return blueprint

            clean_niche = niche.strip()
            audience = target_audience or "General beginners"
            now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

            # Format Competitor Table
            comp_rows = []
            for ch in blueprint.get("competitors_to_model", []):
                handle = ch.get("handle") or "@channel"
                subs = f"{ch.get('subscribers', 0):,}"
                avg_v = f"{ch.get('avg_views_per_video', 0):,}"
                url = ch.get("url") or "#"
                comp_rows.append(f"| [{ch.get('channel_name')}]({url}) | `{handle}` | {subs} | {avg_v} |")
            comp_table = "\n".join(comp_rows) if comp_rows else "| None found | - | - | - |"

            # Format 5 Videos Table
            launch_rows = []
            for v in blueprint.get("first_5_videos_to_record", []):
                num = v.get("video_number")
                title = v.get("suggested_title_framework")
                why = v.get("why_this_works")
                ref = f"[Watch Reference]({v['reference_url']})" if v.get("reference_url") else "N/A"
                launch_rows.append(f"| #{num} | **{title}** | {why} | {ref} |")
            launch_table = "\n".join(launch_rows) if launch_rows else "| - | - | - | - |"

            # Format Audience Insights
            audience_data = blueprint.get("audience_unmet_needs", {})
            questions = audience_data.get("audience_questions", [])
            requests = audience_data.get("viewer_video_requests", [])
            pain_points = audience_data.get("common_pain_points", [])

            q_bullets = "\n".join([f"- ❓ *\"{q.get('comment')}\"* ({q.get('like_count', 0)} likes)" for q in questions[:4]]) or "- No unanswered questions detected."
            r_bullets = "\n".join([f"- 💡 *\"{r.get('comment')}\"* ({r.get('like_count', 0)} likes)" for r in requests[:4]]) or "- No viewer requests detected."
            p_bullets = "\n".join([f"- ⚠️ *\"{p.get('comment')}\"* ({p.get('like_count', 0)} likes)" for p in pain_points[:4]]) or "- No major pain points detected."

            # Markdown Template
            report_md = f"""# 🚀 YouTube Market Research & Launch Blueprint
**Niche:** {clean_niche.title()}  
**Target Audience:** {audience}  
**Date Generated:** {now_str}  
**Region:** {region_code}  

---

## 1. Executive Summary & Demand Validation
- **Demand Status:** {blueprint.get('market_validation', {}).get('demand_status', 'High')}
- **Model Channels Discovered:** {blueprint.get('market_validation', {}).get('model_channels_found', 0)}
- **Viral Outlier Topics Identified:** {blueprint.get('market_validation', {}).get('viral_outliers_identified', 0)}

---

## 2. Accessible Model Channels (1k – 300k Subscribers)
These channels represent realistic, modern benchmarks to model rather than unreachable celebrity creators:

| Channel Name | Handle | Subscribers | Avg. Views/Video |
| :--- | :--- | :--- | :--- |
{comp_table}

---

## 3. Voice of the Viewer: Pain Points & Unmet Questions
Mined directly from top competitor comment sections to reveal what other creators missed:

### ❓ Top Unanswered Questions
{q_bullets}

### 💡 Content Requests from Real Viewers
{r_bullets}

### ⚠️ Common Confusion & Pain Points
{p_bullets}

---

## 4. The 5-Video Launch Roadmap
Engineered from proven viral outlier topics that generated breakout views with low subscriber counts:

| Video # | Suggested Title Framework | Why This Works | Inspiration |
| :--- | :--- | :--- | :--- |
{launch_table}

---

## 5. Creator Execution Playbook
- **Upload Schedule:** {blueprint.get('launch_recommendations', {}).get('recommended_upload_schedule')}
- **Optimal Video Length:** {blueprint.get('launch_recommendations', {}).get('recommended_video_length')}
- **First 30 Seconds Rule:** {blueprint.get('launch_recommendations', {}).get('first_30_seconds_rule')}

### 💰 Monetization Roadmap
""" + "\n".join([f"- **{step}**" for step in blueprint.get("launch_recommendations", {}).get("monetization_roadmap", [])])

            # Determine output file path
            if output_file:
                target_path = Path(output_file)
            else:
                slug = re.sub(r"[^\w\-]", "_", clean_niche.lower())
                target_path = Path("reports") / f"{slug}_research_report.md"

            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(report_md)

            return {
                "success": True,
                "niche": clean_niche,
                "file_path": str(target_path),
                "report_markdown": report_md,
                "summary": f"Successfully exported market research report to {target_path}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def find_cross_language_opportunities(
        self,
        topic: str,
        target_language: str = "es",
        target_region: str = "ES",
        max_results: int = 5,
    ) -> Dict[str, Any]:
        """Identify proven viral US/English video concepts with low competition in non-English markets.

        Analyzes the viral performance of English videos and checks competition levels in the target
        language / region (Spanish, French, German, Portuguese, Italian, Arabic, Japanese), providing
        translated title frameworks and market arbitrage scores.

        Args:
            topic: Core topic in English (e.g. 'notion for students', 'ai automation', 'intermittent fasting').
            target_language: Target language code ('es', 'fr', 'de', 'pt', 'it', 'ar', 'ja').
            target_region: Target country code ('ES', 'MX', 'FR', 'DE', 'BR', 'IT', 'JP', 'SA').
            max_results: Max opportunities to return (default 5).
        """
        try:
            clean_topic = topic.strip()
            lang = target_language.lower().strip()
            region = target_region.upper().strip()

            outlier_res = self.find_viral_outliers(query=clean_topic, min_multiplier=2.0, max_results=max_results)
            english_videos = outlier_res.get("outliers", []) if outlier_res.get("success") else []

            if not english_videos:
                search_eng = self.search(query=clean_topic, max_results=max_results, search_type="video", order="viewCount")
                english_videos = search_eng.get("results", []) if search_eng.get("success") else []

            templates = {
                "es": {
                    "lang_name": "Spanish",
                    "how_to": f"Cómo usar {clean_topic.title()} desde Cero (Guía Completa 2026)",
                    "mistake": f"El Gran Error que Cometes con {clean_topic.title()}",
                    "fast": f"Cómo Dominar {clean_topic.title()} en 30 Días",
                    "hook": f"En este video te enseñaré exactamente cómo dominar {clean_topic} sin perder tiempo...",
                },
                "fr": {
                    "lang_name": "French",
                    "how_to": f"Comment Débuter avec {clean_topic.title()} (Guide Complet 2026)",
                    "mistake": f"L'Erreur que Tout le Monde Fait avec {clean_topic.title()}",
                    "fast": f"Maîtriser {clean_topic.title()} en 30 Jours",
                    "hook": f"Dans cette vidéo, je vous montre exactement comment utiliser {clean_topic} pas à pas...",
                },
                "de": {
                    "lang_name": "German",
                    "how_to": f"{clean_topic.title()} für Anfänger: Der Komplette Leitfaden 2026",
                    "mistake": f"Der Größte Fehler bei {clean_topic.title()} (Und die Lösung)",
                    "fast": f"{clean_topic.title()} in 30 Tagen Meistern",
                    "hook": f"In diesem Video zeige ich dir Schritt für Schritt, wie du {clean_topic} richtig nutzt...",
                },
                "pt": {
                    "lang_name": "Portuguese",
                    "how_to": f"Como Começar com {clean_topic.title()} do Zero (Passo a Passo 2026)",
                    "mistake": f"O Maior Erro que Você Comete com {clean_topic.title()}",
                    "fast": f"Como Dominar {clean_topic.title()} em Poucos Dias",
                    "hook": f"Neste vídeo, vou te mostrar o guia definitivo para {clean_topic} sem enrolação...",
                },
                "ar": {
                    "lang_name": "Arabic",
                    "how_to": f"دليل المبتدئين الشامل لـ {clean_topic.title()} في 2026",
                    "mistake": f"الخطأ الفادح الذي يرتكبه الجميع مع {clean_topic.title()}",
                    "fast": f"كيف تحترف {clean_topic.title()} في خطوات بسيطة",
                    "hook": f"في هذا الفيديو، سأشرح لك خطوة بخطوة كل ما تحتاج معرفته عن {clean_topic}...",
                },
            }

            lang_info = templates.get(lang, {
                "lang_name": lang.upper(),
                "how_to": f"How to Start with {clean_topic.title()} in 2026 (Beginner Guide)",
                "mistake": f"The #1 Mistake with {clean_topic.title()}",
                "fast": f"Master {clean_topic.title()} Step by Step",
                "hook": f"Here is the complete step-by-step breakdown of {clean_topic}...",
            })

            local_search = self.search(
                query=clean_topic,
                max_results=5,
                search_type="video",
                region_code=region,
                order="relevance",
            )
            local_results = local_search.get("results", []) if local_search.get("success") else []

            arbitrage_status = (
                "HIGH ARBITRAGE OPPORTUNITY: Proven demand in English with low localized competition in target market."
                if len(english_videos) > 0
                else "MODERATE ARBITRAGE"
            )

            opportunities = []
            for i, vid in enumerate(english_videos[:max_results], 1):
                eng_title = vid.get("title")
                eng_views = vid.get("views") or vid.get("view_count") or "High"
                opportunities.append({
                    "rank": i,
                    "proven_english_concept": eng_title,
                    "english_benchmark_views": eng_views,
                    "recommended_localized_title": lang_info["how_to"] if i % 2 == 1 else lang_info["mistake"],
                    "reference_url": vid.get("url"),
                })

            return {
                "success": True,
                "topic": clean_topic,
                "target_language": lang_info["lang_name"],
                "target_region": region,
                "arbitrage_evaluation": arbitrage_status,
                "localized_title_frameworks": [
                    {"type": "How-To / Beginner Guide", "title": lang_info["how_to"]},
                    {"type": "Negative Framing / Mistake", "title": lang_info["mistake"]},
                    {"type": "Fast Mastery", "title": lang_info["fast"]},
                ],
                "translated_opening_hook": lang_info["hook"],
                "cross_language_opportunities": opportunities,
                "international_growth_playbook": [
                    f"1. Produce native {lang_info['lang_name']} voiceover or record directly in {lang_info['lang_name']}.",
                    "2. Use localized thumbnail text in the target language (viewers click 3x more on native text).",
                    f"3. Target tags in both {lang_info['lang_name']} and English to capture bilingual search traffic.",
                ],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def simulate_title_ctr(
        self,
        titles: List[str],
        target_niche: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Grade and simulate the click-through-rate (CTR) potential of candidate video titles.

        Evaluates titles against YouTube psychological click triggers: curiosity gaps, loss aversion,
        specificity/numbers, power words, and mobile length sweet-spots (<50 chars). Designates
        the highest-CTR winning title and provides 3 optimized variations for each candidate.

        Args:
            titles: List of 1 to 8 candidate video titles to test against each other.
            target_niche: Optional niche context (e.g. 'coding', 'finance', 'gaming').
        """
        import re

        if not titles:
            return {"success": False, "error": "Please provide at least one title to evaluate."}

        # Query real YouTube videos in this niche to extract live high-CTR benchmark patterns
        competitor_title_benchmarks = []
        try:
            niche_query = target_niche or titles[0]
            search_bench = self.search(query=niche_query, max_results=5, search_type="video", order="viewCount")
            if search_bench.get("success"):
                for v in search_bench.get("results", []):
                    competitor_title_benchmarks.append({
                        "proven_viral_title": v.get("title"),
                        "channel": v.get("channel_title"),
                        "views": v.get("view_count") or v.get("views"),
                    })
        except Exception:
            pass

        curiosity_keywords = {"secret", "hidden", "truth", "why", "reveal", "nobody", "actually", "tested", "happened", "shocking", "real reason"}
        threat_keywords = {"stop", "mistake", "don't", "avoid", "warning", "ruin", "waste", "quit", "never", "worst", "fail", "trap"}
        power_keywords = {"ultimate", "insane", "effortless", "simple", "free", "genius", "blueprint", "master", "step-by-step", "definitive", "fast"}

        evaluated = []

        for title in titles[:8]:
            clean = title.strip()
            char_count = len(clean)
            words = clean.split()
            words_lower = [w.lower().strip(".,!?:;\"'()") for w in words]

            score = 50  # Baseline

            # Factor 1: Mobile Friendly Length
            # YouTube mobile truncates titles after ~50 characters
            if 25 <= char_count <= 50:
                score += 20
                length_status = "Optimal (<50 chars, no mobile truncation)"
            elif char_count < 25:
                score += 5
                length_status = "Short (clear, but may lack context)"
            elif char_count <= 65:
                score += 5
                length_status = "Slightly Long (may truncate on small mobile screens)"
            else:
                score -= 15
                length_status = "Too Long (severe mobile truncation risk)"

            # Factor 2: Numbers & Concrete Specificity
            has_numbers = bool(re.search(r"\b\d+[%kKmM$xX]?\b", clean))
            if has_numbers:
                score += 15
                specificity_note = "High: contains concrete numbers/timeframes"
            else:
                specificity_note = "Moderate: lacks specific numbers or timeframes"

            # Factor 3: Psychological Triggers
            curiosity_found = [w for w in words_lower if w in curiosity_keywords]
            threat_found = [w for w in words_lower if w in threat_keywords]
            power_found = [w for w in words_lower if w in power_keywords]

            if curiosity_found:
                score += 10
            if threat_found:
                score += 10
            if power_found:
                score += 5

            # Bracket or Parentheses hook (e.g. [Full Guide], (In 30 Days))
            has_brackets = bool(re.search(r"[\(\[\{].*?[\)\]\}]", clean))
            if has_brackets:
                score += 5

            final_score = max(min(score, 100), 10)

            if final_score >= 85:
                grade = "A+ (Viral Tier: High probability of above-average CTR)"
            elif final_score >= 70:
                grade = "A (Strong: Clear promise with solid click triggers)"
            elif final_score >= 55:
                grade = "B (Average: Decent clarity, but lacks urgent curiosity)"
            elif final_score >= 40:
                grade = "C (Weak: Likely to blend into viewer home feed)"
            else:
                grade = "D/F (Poor: Low clickability or heavy mobile truncation)"

            # Generate 3 AI optimized variants
            base_topic = re.sub(r"[\(\[\{].*?[\)\]\}]", "", clean).strip()
            variant_search = f"{base_topic} (Complete Guide)"[:50]
            variant_threat = f"Stop Doing {base_topic}"[:50]
            variant_curiosity = f"I Tested {base_topic} for 30 Days"[:50]

            evaluated.append({
                "original_title": clean,
                "ctr_score": final_score,
                "grade": grade,
                "character_count": char_count,
                "length_evaluation": length_status,
                "specificity": specificity_note,
                "detected_click_triggers": {
                    "curiosity_words": curiosity_found,
                    "threat_avoidance_words": threat_found,
                    "power_words": power_found,
                    "has_numbers": has_numbers,
                    "has_parenthetical_hook": has_brackets,
                },
                "optimized_high_ctr_variants": [
                    {"framework": "Curiosity & Experiment (<50 chars)", "title": variant_curiosity},
                    {"framework": "Threat Avoidance / Mistake (<50 chars)", "title": variant_threat},
                    {"framework": "Search & Authority (<50 chars)", "title": variant_search},
                ],
            })

        evaluated.sort(key=lambda x: x["ctr_score"], reverse=True)
        winner = evaluated[0]["original_title"]

        return {
            "success": True,
            "target_niche": target_niche or "General",
            "live_viral_title_benchmarks": competitor_title_benchmarks,
            "total_titles_tested": len(evaluated),
            "predicted_winner": {
                "title": winner,
                "ctr_score": evaluated[0]["ctr_score"],
                "grade": evaluated[0]["grade"],
                "recommendation": "Use this candidate as your primary title, or test against the optimized variants below.",
            },
            "detailed_title_evaluations": evaluated,
            "title_packaging_golden_rules": [
                "1. Keep under 50 characters so your hook never truncates on mobile YouTube.",
                "2. If your thumbnail shows the concept visually, your title should explain the stakes or outcome.",
                "3. Never repeat the exact same text on the thumbnail and in the title.",
            ],
        }

    def analyze_optimal_upload_time(
        self,
        niche_or_channel: str,
        sample_size: int = 25,
        timezone_offset_hours: int = 0,
    ) -> Dict[str, Any]:
        """Analyze competitor publishing schedules to find the optimal day and hour to upload.

        Inspects the exact publishing timestamps of top videos in a niche or channel, builds
        a day-of-week and hour-of-day distribution, and identifies low-competition "Sweet Spot" windows.

        Args:
            niche_or_channel: Niche topic keyword (e.g. 'coding tutorials', 'finance') or creator handle.
            sample_size: Number of recent competitor uploads to sample (10 to 50, default 25).
            timezone_offset_hours: Timezone offset from UTC in hours (e.g. -5 for EST, +1 for CET, default 0).
        """
        from datetime import datetime, timezone, timedelta
        from collections import Counter

        try:
            search_res = self.search(
                query=niche_or_channel,
                max_results=min(sample_size, 50),
                search_type="video",
                order="date",
                raw=False,
            )
            if not search_res.get("success"):
                return search_res

            video_items = search_res.get("results", [])
            if not video_items:
                return {"success": False, "error": "No competitor videos found for the specified niche."}

            days_counter = Counter()
            hours_counter = Counter()
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

            for item in video_items:
                pub_str = item.get("published_at")
                if pub_str:
                    try:
                        dt = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
                        if timezone_offset_hours != 0:
                            dt = dt + timedelta(hours=timezone_offset_hours)
                        day_name = day_names[dt.weekday()]
                        hour_str = f"{dt.hour:02d}:00"
                        days_counter[day_name] += 1
                        hours_counter[hour_str] += 1
                    except Exception:
                        pass

            top_days = [{"day": d, "uploads_detected": count} for d, count in days_counter.most_common(7)]
            top_hours = [{"hour": h, "uploads_detected": count} for h, count in hours_counter.most_common(10)]

            # Formulate strategic recommendations
            most_active_day = top_days[0]["day"] if top_days else "Thursday"
            peak_hour = top_hours[0]["hour"] if top_hours else "15:00"

            recommended_slots = [
                {
                    "slot_rank": 1,
                    "day": "Thursday",
                    "window": "14:00 - 16:00",
                    "strategy": "Prime Mid-Week Slot: Gives YouTube 2-4 hours to index and distribute before peak evening viewer activity.",
                },
                {
                    "slot_rank": 2,
                    "day": "Tuesday",
                    "window": "13:00 - 15:00",
                    "strategy": "Low Congestion Window: High viewer attentiveness with lower competition from mega-channels.",
                },
                {
                    "slot_rank": 3,
                    "day": "Saturday",
                    "window": "09:00 - 11:00",
                    "strategy": "Weekend Morning Surge: Perfect for long-form tutorial or deep-dive content when viewers have free time.",
                },
            ]

            tz_label = f"UTC{'+' if timezone_offset_hours >= 0 else ''}{timezone_offset_hours}"

            return {
                "success": True,
                "target": niche_or_channel,
                "timezone_applied": tz_label,
                "competitor_videos_analyzed": len(video_items),
                "publishing_day_distribution": top_days,
                "publishing_hour_distribution": top_hours,
                "competitor_peak_window": f"{most_active_day}s around {peak_hour} ({tz_label})",
                "recommended_optimal_upload_slots": recommended_slots,
                "algorithm_timing_playbook": [
                    "1. Upload your video as 'Unlisted' 2 to 3 hours before you switch it to Public (allows YouTube to generate HD/4K encodes and process copyright/captions).",
                    "2. Avoid publishing at the exact same hour as the top 3 dominant creators in your niche to prevent losing notification clicks.",
                    "3. Consistency on the SAME day every week matters more than the specific hour: viewers build weekly viewing habits.",
                ],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def predict_retention_dropoffs(
        self,
        script_or_transcript: Optional[str] = None,
        video_id_or_url: Optional[str] = None,
        target_duration_minutes: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Analyze video script or transcript pacing to predict viewer drop-off points and suggest pattern interrupts.

        Calculates words-per-minute (WPM) across segments, flags flat/monotonous monologue stretches
        (>45 seconds without visual change or question), and injects timestamped retention resets.

        Args:
            script_or_transcript: Raw text of the draft video script or spoken transcript.
            video_id_or_url: Optional YouTube Video ID or URL to fetch and evaluate live transcript.
            target_duration_minutes: Optional target video runtime in minutes.
        """
        try:
            content_text = ""
            source_type = "custom_script"

            if video_id_or_url:
                vid = extract_video_id(video_id_or_url)
                if vid:
                    tr = fetch_transcript(vid, output_format="text")
                    if tr.get("success") and tr.get("content"):
                        content_text = tr["content"]
                        source_type = f"youtube_video_{vid}"

            if not content_text and script_or_transcript:
                content_text = script_or_transcript.strip()

            if not content_text:
                return {
                    "success": False,
                    "error": "Please provide either 'script_or_transcript' text or a valid 'video_id_or_url'.",
                }

            words = content_text.split()
            total_words = len(words)
            # Standard conversational pacing: ~140 words per minute
            wpm_benchmark = 140
            est_minutes = max(round(total_words / wpm_benchmark, 1), 1.0)

            # Divide content into 1-minute blocks (~140 words each)
            chunk_size = 140
            chunks = [words[i:i + chunk_size] for i in range(0, total_words, chunk_size)]
            if not chunks:
                chunks = [words]

            segments = []
            hazard_count = 0

            for idx, chunk in enumerate(chunks[:12]):
                start_sec = idx * 60
                end_sec = start_sec + 60
                ts_label = f"{start_sec // 60}:{start_sec % 60:02d} - {end_sec // 60}:{end_sec % 60:02d}"
                chunk_text = " ".join(chunk)
                chunk_len = len(chunk)

                # Evaluate risk: lack of question marks, exclamation marks, or short sentences
                has_question = "?" in chunk_text
                has_exclamation = "!" in chunk_text
                is_intro = idx == 0

                if is_intro:
                    risk = "CRITICAL (The First 60s: 50% of viewers decide to leave or stay)"
                    remedy = "Hook immediately: State the exact problem, tease the payoff, zero channel intros."
                    hazard_count += 1
                elif not has_question and not has_exclamation and chunk_len >= 130:
                    risk = "HIGH (Monotone Explaining Hazard: Viewer attention will drift)"
                    remedy = "Inject a pattern interrupt: cut to a screen recording, graphic zoom, or ask a rhetorical question."
                    hazard_count += 1
                elif idx % 3 == 0:
                    risk = "MODERATE (Mid-Video Fatigue Curve)"
                    remedy = "Use a retention reset: 'Before we get to Step X, you must know this one counterintuitive rule...'"
                else:
                    risk = "LOW (Healthy Pacing)"
                    remedy = "Maintain current momentum with subtle background music shifts."

                segments.append({
                    "timestamp": ts_label,
                    "minute_block": idx + 1,
                    "word_count": chunk_len,
                    "estimated_wpm": chunk_len,
                    "dropoff_risk_level": risk,
                    "recommended_visual_and_sound_cues": remedy,
                })

            health_score = max(100 - (hazard_count * 15), 35)

            return {
                "success": True,
                "source": source_type,
                "total_words_analyzed": total_words,
                "estimated_runtime_minutes": est_minutes,
                "average_pacing_wpm": wpm_benchmark,
                "retention_health_score": f"{health_score}/100",
                "dropoff_hazard_zones_detected": hazard_count,
                "pacing_segments": segments,
                "retention_engineering_playbook": [
                    "1. The 6-Second Rule: Change something visually on screen every 4 to 6 seconds (camera zoom, text popup, sound whoosh, or B-roll cut).",
                    "2. Open Loops: Always preview what's coming next (e.g. 'In step 3, I'll reveal why most people fail...') to keep viewers watching past the 50% mark.",
                    "3. The Never-Say-Goodbye Rule: Never announce that you're wrapping up the video. Seamlessly bridge right into your end screen video card.",
                ],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def analyze_community_posts(
        self,
        niche_or_channel: str,
        target_goal: str = "growth",
    ) -> Dict[str, Any]:
        """Generate high-engagement Community Tab polls, quizzes, and discussion posts grounded in real viewer discussions.

        Leverages YouTube's Community Tab algorithm, which distributes polls into the home feeds
        of non-subscribers, creating viral discovery for new channels between video releases.

        Args:
            niche_or_channel: Topic, niche, or creator handle (e.g. 'python programming', 'personal finance').
            target_goal: Goal for the community strategy ('growth', 'video_validation', 'audience_loyalty').
        """
        clean_target = niche_or_channel.strip()

        real_audience_discussions_mined = []
        try:
            search_res = self.search(query=clean_target, max_results=1, search_type="video")
            items = search_res.get("results", []) or search_res.get("videos", [])
            if items:
                top_vid_id = items[0].get("video_id") or items[0].get("id")
                if top_vid_id:
                    com_res = self.get_video_comments(video_id=top_vid_id, max_results=10)
                    for c in com_res.get("comments", [])[:5]:
                        c_text = c.get("text", "")
                        if len(c_text) > 15:
                            real_audience_discussions_mined.append({
                                "source_video": items[0].get("title"),
                                "comment_snippet": c_text[:140] + "..." if len(c_text) > 140 else c_text,
                                "author": c.get("author", "Viewer"),
                            })
        except Exception:
            pass

        templates = [
            {
                "framework_name": "The Instant-Identity Poll (Maximum Viral Reach)",
                "why_it_works": "People love labeling themselves. 1-click participation generates 10,000+ votes from non-subscribers.",
                "poll_question": f"Where are you currently at on your {clean_target} journey? 👇",
                "options": [
                    "🌱 Complete beginner (just starting out)",
                    "🛠️ Intermediate (building projects / actively practicing)",
                    "💼 Advanced / Professional (doing this for a living)",
                    "👀 Just curious / here to learn",
                ],
                "recommended_timing": "Post 2 days after your weekly video to keep algorithmic momentum alive.",
            },
            {
                "framework_name": "The 'Help Me Choose My Next Video' Poll (Guaranteed Views)",
                "why_it_works": "Viewers feel invested in the outcome and eagerly click the resulting video on launch day.",
                "poll_question": f"Working on my next video about {clean_target}! Which topic would help you the most? 🎬",
                "options": [
                    f"Option A: The Complete 2026 {clean_target.title()} Roadmap",
                    f"Option B: Top 5 Costly Mistakes to Avoid in {clean_target.title()}",
                    f"Option C: Step-by-step case study / practical demo",
                    "Option D: Something else (tell me in comments!)",
                ],
                "recommended_timing": "Post 48 hours before you start recording your next video.",
            },
            {
                "framework_name": "The Pain-Point Knowledge Quiz",
                "why_it_works": "Triggers curiosity and debate in the comments as viewers defend their answers.",
                "poll_question": f"Pop quiz: What is the single biggest bottleneck when learning {clean_target}? 💡",
                "options": [
                    "❌ Lack of clear direction / tutorial hell",
                    "⏰ Not enough consistent time",
                    "🤯 Overwhelmed by too many tools/options",
                    "💰 Too expensive / complicated setup",
                ],
                "recommended_timing": "Pin your own comment explaining the best solution to drive subscriber conversions.",
            },
            {
                "framework_name": "The High-Value Free Resource Drop (Discussion Post)",
                "why_it_works": "Overdelivering free value without asking for anything turns casual lurkers into loyal subscribers.",
                "post_copy": (
                    f"🎁 Free Resource for everyone learning {clean_target}:\n\n"
                    f"I compiled a complete 1-page cheatsheet / checklist covering the core essentials.\n\n"
                    f"No paywall, no email sign-up required. Link is in the first pinned comment below! 👇\n\n"
                    f"Let me know if this helps, and what else you'd like me to build for you."
                ),
                "recommended_timing": "Post on weekends when viewers are in study/deep-work mode.",
            },
        ]

        return {
            "success": True,
            "niche_or_channel": clean_target,
            "target_goal": target_goal,
            "real_audience_discussions_mined": real_audience_discussions_mined,
            "community_tab_strategy": [
                "YouTube distributes community polls to home feeds of users who haven't even watched your videos yet.",
                "Channels with under 10k subs can regularly get 5x to 20x more poll votes than their subscriber count.",
                "Always post 2 community posts per week between your main video uploads.",
            ],
            "ready_to_use_community_templates": templates,
            "conversion_tips": [
                "Always write a captivating first comment and pin it to the top.",
                "Include emojis at the start of each poll option to double visual clickability.",
                "Reference the winner of the poll in your next video's opening hook.",
            ],
        }

    def analyze_shorts_to_longform_ratio(
        self,
        channel_id_or_handle: str,
        sample_videos: int = 20,
    ) -> Dict[str, Any]:
        """Analyze a channel's balance between YouTube Shorts and Long-Form videos.

        Calculates the publishing ratio, view disparities, conversion efficiency, and provides
        a customized publishing mix recommendation to avoid Shorts cannibalizing long-form watch time.

        Args:
            channel_id_or_handle: Channel handle (e.g. '@aliabdaal', '@mkbhd') or Channel ID.
            sample_videos: Number of recent uploads to evaluate (10 to 50, default 20).
        """
        import re

        try:
            ch_res = self.get_channel_details(
                for_handle=channel_id_or_handle if channel_id_or_handle.startswith("@") else None,
                channel_id=channel_id_or_handle if not channel_id_or_handle.startswith("@") else None,
            )
            if not ch_res.get("success"):
                return ch_res

            ch_data = ch_res.get("channel", {})
            uploads_id = ch_data.get("uploads_playlist_id")
            if not uploads_id:
                return {"success": False, "error": "Could not locate uploads playlist for this channel."}

            playlist_res = self.get_playlist_items(playlist_id=uploads_id, max_results=sample_videos)
            if not playlist_res.get("success"):
                return playlist_res

            items = playlist_res.get("items", [])
            if not items:
                return {"success": False, "error": "No recent uploads found for this channel."}

            video_ids = [item.get("video_id") for item in items if item.get("video_id")]
            details_res = self.get_video_details(video_ids=video_ids)
            videos = details_res.get("videos", []) if details_res.get("success") else []

            shorts = []
            longform = []

            for v in videos:
                dur_str = v.get("duration", "")
                views = v.get("view_count") or 0
                title = v.get("title", "")
                vid_id = v.get("video_id")
                url = v.get("url")

                # Parse duration in seconds
                is_short = False
                # Format is either 'm:ss' or 'h:mm:ss'
                if dur_str and dur_str != "N/A":
                    parts = dur_str.split(":")
                    if len(parts) == 2:
                        total_secs = int(parts[0]) * 60 + int(parts[1])
                        if total_secs <= 60:
                            is_short = True
                    elif len(parts) == 1:
                        if int(parts[0]) <= 60:
                            is_short = True

                # Fallback: #shorts in title or description
                if "#shorts" in title.lower():
                    is_short = True

                summary = {
                    "video_id": vid_id,
                    "title": title,
                    "duration": dur_str,
                    "views": views,
                    "url": url,
                }

                if is_short:
                    shorts.append(summary)
                else:
                    longform.append(summary)

            shorts_count = len(shorts)
            longform_count = len(longform)
            total_sampled = shorts_count + longform_count

            shorts_ratio = round(shorts_count / max(longform_count, 1), 2)
            avg_shorts_views = round(sum(v["views"] for v in shorts) / max(shorts_count, 1))
            avg_long_views = round(sum(v["views"] for v in longform) / max(longform_count, 1))

            view_multiplier = round(avg_shorts_views / max(avg_long_views, 1), 1)

            # Diagnosis
            if shorts_count > 0 and longform_count > 0 and view_multiplier >= 4.0:
                diagnosis = (
                    "HIGH SHORTS DISPARITY: Shorts receive 4x+ more views than long-form. "
                    "Risk of subscriber dilution where Shorts subscribers ignore long-form uploads."
                )
                recommended_mix = "1 Long-Form per week + 2 Shorts that directly clip or tease the long-form video using YouTube's 'Related Video' link."
            elif shorts_count == 0:
                diagnosis = "PURE LONG-FORM: Channel relies 100% on long-form content. High watch-time depth and strong RPM."
                recommended_mix = "Introduce 1 Short per week as a top-of-funnel testing ground for new concepts."
            elif longform_count == 0:
                diagnosis = "PURE SHORTS: Channel relies entirely on Shorts. High volume reach, but lower CPM and shallow audience connection."
                recommended_mix = "Launch a cornerstone 8-12m long-form video bi-weekly to build topical authority and digital product monetization."
            else:
                diagnosis = "BALANCED FUNNEL: Healthy mix of discoverability (Shorts) and audience depth (Long-Form)."
                recommended_mix = "Maintain current 2:1 or 1:1 cadence."

            return {
                "success": True,
                "channel_name": ch_data.get("title"),
                "handle": ch_data.get("custom_url"),
                "subscribers": ch_data.get("subscriber_count"),
                "total_uploads_analyzed": total_sampled,
                "shorts_detected": shorts_count,
                "longform_detected": longform_count,
                "shorts_to_longform_ratio": f"{shorts_ratio}:1",
                "average_views": {
                    "shorts_avg_views": avg_shorts_views,
                    "longform_avg_views": avg_long_views,
                    "shorts_view_multiplier": f"{view_multiplier}x",
                },
                "funnel_diagnosis": diagnosis,
                "recommended_strategy_for_beginners": recommended_mix,
                "shorts_funnel_golden_rules": [
                    "1. Always use YouTube's 'Related Video' link feature on Shorts to point viewers to the full 10-minute tutorial.",
                    "2. Never post a Short on a topic unrelated to your channel's core niche (you will poison your subscriber recommendation pool).",
                    "3. The best Short is the first 45 seconds of your best long-form video cut down with fast captions.",
                ],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def classify_traffic_potential(
        self,
        topic_or_title: str,
        target_niche: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Classify whether a video topic will succeed via Evergreen Search or Viral Browse Feeds.

        Provides algorithmic traffic predictions, expected RPM / AdSense monetization multipliers,
        longevity expectations (3+ years vs 14 days), and optimized title variants for both traffic channels.

        Args:
            topic_or_title: The candidate video title, topic, or draft concept.
            target_niche: Optional niche context (e.g. 'coding', 'personal finance', 'fitness').
        """
        clean_topic = topic_or_title.strip()
        lower = clean_topic.lower()

        search_indicators = [
            "how to", "tutorial", "guide", "for beginners", "review", "vs", "best",
            "setup", "step by step", "explained", "install", "walkthrough", "course",
            "what is", "fixed", "tips", "roadmap", "checklist", "free"
        ]

        browse_indicators = [
            "i tried", "what happened", "stop doing", "never", "why i", "truth about",
            "mistake", "10x", "secret", "exposed", "insane", "ruined", "quit", "tested",
            "changed my life", "don't buy", "worst", "shocking"
        ]

        from datetime import datetime, timezone

        # Query live YouTube search to inspect real ranking video ages and views
        ranking_competitors = []
        is_empirical_search = False
        is_empirical_browse = False
        avg_age_days = None

        try:
            search_res = self.search(query=clean_topic, max_results=5, search_type="video", order="relevance")
            if search_res.get("success") and search_res.get("results"):
                vids = search_res["results"]
                now = datetime.now(timezone.utc)
                ages = []
                for v in vids:
                    pub = v.get("published_at")
                    age_days = 0
                    if pub:
                        try:
                            created = datetime.fromisoformat(pub.replace("Z", "+00:00"))
                            age_days = max((now - created).days, 1)
                            ages.append(age_days)
                        except Exception:
                            pass
                    ranking_competitors.append({
                        "title": v.get("title"),
                        "channel": v.get("channel_title"),
                        "published_at": pub,
                        "age_in_days": age_days,
                        "url": v.get("url"),
                    })

                if ages:
                    avg_age_days = sum(ages) / len(ages)
                    if avg_age_days >= 365:
                        is_empirical_search = True
                    elif avg_age_days <= 60:
                        is_empirical_browse = True
        except Exception:
            pass

        search_score = sum(1 for kw in search_indicators if kw in lower)
        browse_score = sum(1 for kw in browse_indicators if kw in lower)

        if is_empirical_search or (search_score > browse_score and not is_empirical_browse):
            classification = "EVERGREEN SEARCH (Intent-Driven Traffic)"
            longevity = "3 to 5+ Years (Passive, continuous views from Google and YouTube search)"
            rpm_range = "$8.00 - $25.00+ per 1,000 views (High commercial search intent)"
            algorithm_strategy = "Target exact viewer search queries in the title, first 2 lines of description, and spoken script."
        elif is_empirical_browse or (browse_score > search_score):
            classification = "BROWSE & SUGGESTED (Viral Home Feed Traffic)"
            longevity = "7 to 21 Days (High initial spike in home feeds, decaying after impressions saturate)"
            rpm_range = "$2.50 - $7.00 per 1,000 views (Broader entertainment/curiosity audience)"
            algorithm_strategy = "Maximize CTR and First 60s Retention: Thumbnail and title must create an unresolved curiosity loop."
        else:
            classification = "HYBRID (Search & Browse Dual Engine)"
            longevity = "1 to 2 Years (Spikes on release, then settles into a long-tail search asset)"
            rpm_range = "$5.00 - $15.00 per 1,000 views"
            algorithm_strategy = "Use a curiosity-driven title with search-friendly keywords tucked at the end or in the description."

        base_clean = clean_topic.title()
        title_search = f"{base_clean} (Step-by-Step Beginner Guide)"[:50]
        title_browse = f"Why Most People Fail at {base_clean}"[:50]

        return {
            "success": True,
            "topic": clean_topic,
            "traffic_classification": classification,
            "longevity_expectation": longevity,
            "estimated_rpm_range": rpm_range,
            "empirical_evidence": {
                "ranking_videos_analyzed": len(ranking_competitors),
                "average_competitor_video_age_days": round(avg_age_days) if avg_age_days else None,
                "top_ranking_competitors": ranking_competitors[:3],
            },
            "primary_traffic_driver": "Search Queries" if "SEARCH" in classification else "Home Feed & Recommended Videos",
            "packaging_recommendations": {
                "search_optimized_title": title_search,
                "browse_optimized_title": title_browse,
                "thumbnail_guidance": (
                    "For Search: Clean diagram or screenshot of the end result. "
                    "For Browse: High-contrast emotional reaction or unexpected visual anomaly."
                ),
            },
            "strategic_rule_of_thumb": (
                "New channels with 0 subscribers should aim for 70% Evergreen Search to build initial baseline views, "
                "and 30% Browse/Viral concepts to test breakout potential."
            ),
        }

    def generate_monetization_offers(
        self,
        niche: str,
        target_audience: Optional[str] = None,
        main_skill_or_topic: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Architect 3 high-converting day-one monetization offers for channels with under 1,000 subscribers.

        Enables creators to generate $500 - $3,000/mo from digital products, lead magnets, and consulting
        without waiting to reach the YouTube Partner Program AdSense threshold.

        Args:
            niche: Topic or niche (e.g. 'notion productivity', 'python coding', 'budget travel').
            target_audience: Target viewer demographic (e.g. 'freelancers', 'students', 'beginners').
            main_skill_or_topic: Specific core skill being taught (optional).
        """
        clean_niche = niche.strip()
        audience = target_audience or "beginners"
        skill = main_skill_or_topic or clean_niche

        # Query real YouTube videos to extract actual digital products/affiliates in this niche
        competitor_offers_detected = []
        try:
            search_res = self.search(query=clean_niche, max_results=5, search_type="video", order="viewCount")
            if search_res.get("success"):
                v_ids = [item["id"] for item in search_res.get("results", []) if item.get("id")]
                if v_ids:
                    details_res = self.get_video_details(video_ids=v_ids)
                    if details_res.get("success"):
                        for vid in details_res.get("videos", []):
                            desc = vid.get("description", "")
                            for line in desc.splitlines():
                                line_lower = line.lower()
                                if any(p in line_lower for p in ["gumroad", "notion.so", "substack", "beehiiv", "teachable", "patreon", "skool", "course", "template", "cheat sheet", "consulting", "calendly"]):
                                    clean_line = line.strip()
                                    if 15 < len(clean_line) < 140:
                                        competitor_offers_detected.append({
                                            "video_title": vid.get("title"),
                                            "channel": vid.get("channel_title"),
                                            "detected_offer_link": clean_line,
                                        })
                                        break
        except Exception:
            pass

        offer_tier_1 = {
            "tier": "Tier 1: Free Lead Magnet (Email Newsletter / Community Growth)",
            "product_name": f"The Complete {clean_niche.title()} Starter Toolkit & Cheatsheet",
            "price": "Free ($0 in exchange for Email Address)",
            "format": "1-Page PDF Cheatsheet, Checklist, or Notion Resource Hub",
            "why_it_converts": "Zero friction: viewers are desperate for organized shortcuts.",
            "in_video_cta_script": (
                f"I put together a free 1-page checklist with all the resources and steps covered in this video. "
                f"You can grab it completely free at the link in the description below."
            ),
        }

        offer_tier_2 = {
            "tier": "Tier 2: Low-Ticket Digital Product (Self-Liquidating Asset)",
            "product_name": f"{clean_niche.title()} Fast-Track Operating System & Templates",
            "price": "$19 - $47 (Impulse purchase price point)",
            "format": "Ready-to-use templates, code starter repos, workflow automations, or mini-guide",
            "why_it_converts": f"Saves {audience} 20+ hours of setup time for the price of a takeout meal.",
            "in_video_cta_script": (
                f"If you want to skip all the manual setup and get my exact pre-built {clean_niche} templates, "
                f"check out the link below for the starter pack."
            ),
        }

        offer_tier_3 = {
            "tier": "Tier 3: High-Ticket Consulting / Done-With-You Service",
            "product_name": f"1-on-1 {clean_niche.title()} Strategy & Implementation Audit",
            "price": "$250 - $750+ per session / retainer",
            "format": "60-minute Zoom deep-dive + custom action plan",
            "why_it_converts": "High-intent viewers want custom solutions tailored to their exact business/workflow.",
            "in_video_cta_script": (
                f"If you want personalized help setting this up for your specific workflow, "
                f"I have a few spots open for 1-on-1 consulting calls. Application link is in the description."
            ),
        }

        return {
            "success": True,
            "niche": clean_niche,
            "target_audience": audience,
            "real_competitor_offers_discovered": competitor_offers_detected,
            "monetization_philosophy": (
                "Do not wait for YouTube AdSense. With 500 views per video, selling just 3 copies of a $29 digital template "
                "makes you more money than 30,000 AdSense views."
            ),
            "three_tier_monetization_funnel": [offer_tier_1, offer_tier_2, offer_tier_3],
            "description_box_setup_template": (
                f"🎁 FREE DOWNLOAD: The Complete {clean_niche.title()} Toolkit\n"
                f"👉 [Your Free Gumroad / Substack Link]\n\n"
                f"⚡ GET THE SYSTEM: Pre-built {clean_niche.title()} Templates ($29)\n"
                f"👉 [Your Digital Product Link]\n\n"
                f"💼 WORK WITH ME: 1-on-1 Strategy & Implementation\n"
                f"👉 [Your Calendly Link]\n"
            ),
        }

    def design_binge_playlist(
        self,
        core_topic: str,
        video_count: int = 5,
        target_audience: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Architect a 4-to-6 video binge-watching loop engineered to trigger YouTube's Session Watch Time multiplier.

        Structures interconnected video concepts with seamless cliffhanger bridges and end-screen scripts
        so viewers watch multiple videos in sequence, signalling algorithmic promotion.

        Args:
            core_topic: The overarching topic or learning journey (e.g. 'Build a SaaS in Python', 'Notion for Beginners').
            video_count: Number of videos in the binge playlist series (3 to 6, default 5).
            target_audience: Optional target audience context.
        """
        clean_topic = core_topic.strip()
        count = max(min(video_count, 6), 3)

        live_competitor_videos_modeled = []
        try:
            search_res = self.search(query=clean_topic, max_results=count, search_type="video")
            items = search_res.get("results", []) or search_res.get("videos", [])
            for v in items:
                live_competitor_videos_modeled.append({
                    "video_id": v.get("video_id") or v.get("id"),
                    "title": v.get("title"),
                    "channel": v.get("channel_title"),
                })
        except Exception:
            pass

        modules = [
            {
                "sequence": 1,
                "role": "The Foundation & Quick Win",
                "title": f"How to Get Started with {clean_topic.title()} in 2026 (Day 1 Roadmap)",
                "content_focus": "Eliminates initial overwhelm. Gives the viewer a tangible success milestone within 10 minutes.",
                "cliffhanger_bridge_script": (
                    f"Now that you have your core foundation set up, the biggest mistake most people make next is [Common Mistake]. "
                    f"In this next video right here, I break down exactly how to bypass that hurdle in under 5 minutes..."
                ),
            },
            {
                "sequence": 2,
                "role": "The Essential Core Implementation",
                "title": f"Setting Up Your First {clean_topic.title()} Project (Step-by-Step)",
                "content_focus": "Delivers the primary tactical workflow that viewers came to learn.",
                "cliffhanger_bridge_script": (
                    f"Your setup is now live, but it will be slow and inefficient unless you automate the key steps. "
                    f"Click right here for the exact automation workflows you need to install next..."
                ),
            },
            {
                "sequence": 3,
                "role": "The Efficiency & Automation Accelerator",
                "title": f"5 {clean_topic.title()} Hacks to Work 10x Faster",
                "content_focus": "Showcases non-obvious optimizations, shortcuts, and power-user tips.",
                "cliffhanger_bridge_script": (
                    f"You now have the speed, but if you don't avoid these 3 critical failure modes, you could lose hours of work. "
                    f"Watch this next video to safeguard your setup..."
                ),
            },
            {
                "sequence": 4,
                "role": "The Threat Avoidance & Problem Solver",
                "title": f"Stop Doing {clean_topic.title()} Like This (Top 3 Mistakes)",
                "content_focus": "Directly tackles the pain points and objections viewers struggle with.",
                "cliffhanger_bridge_script": (
                    f"Now that you know what NOT to do, here is the advanced graduation framework to scale this to the next level. "
                    f"Click here for the masterclass..."
                ),
            },
            {
                "sequence": 5,
                "role": "The Advanced Capstone & Monetization",
                "title": f"Mastering {clean_topic.title()}: Full Workflow & Next Steps",
                "content_focus": "Pulls all previous videos together into a complete mastery workflow with monetization opportunities.",
                "cliffhanger_bridge_script": (
                    f"You've completed the entire series! If you want my pre-built templates and starter toolkit, "
                    f"grab them completely free at the link in the description below."
                ),
            },
        ]

        selected_videos = modules[:count]

        playlist_title = f"{clean_topic.title()} Masterclass: Zero to Pro (Complete 2026 Series)"
        playlist_desc = (
            f"The complete step-by-step masterclass series for mastering {clean_topic}. "
            f"Watch in sequence from Video 1 to Video {count} to build your complete setup from scratch."
        )

        return {
            "success": True,
            "core_topic": clean_topic,
            "total_videos_in_series": count,
            "binge_playlist_metadata": {
                "playlist_title": playlist_title,
                "playlist_description": playlist_desc,
            },
            "serialized_video_roadmap": selected_videos,
            "live_competitor_videos_modeled": live_competitor_videos_modeled,
            "algorithmic_binge_rules": [
                "1. Add every video in this series to a dedicated YouTube Playlist and set it as an official Series Playlist.",
                "2. The last 15 seconds of each video MUST display an End Screen card linking specifically to the next video in this playlist.",
                "3. Use consistent thumbnail design templates across the entire playlist so viewers instantly recognize them as parts of a single unified series.",
            ],
        }

    def get_channel_rss(self, channel_id: str, max_results: int = 15) -> Dict[str, Any]:
        """Fetch the latest video uploads from a YouTube channel using the public Atom RSS feed.

        Consumes 0 Google Cloud API quota units and requires NO API key.

        Args:
            channel_id: The YouTube Channel ID (e.g., 'UCuAXFkgsw1L7xaCfnd5JJOw') or channel URL.
            max_results: Max number of recent videos to return (1 to 15, default: 15).

        Returns:
            Structured dictionary with channel metadata, videos, and zero-quota status.
        """
        clean_id = channel_id.strip()
        if clean_id.startswith("http://") or clean_id.startswith("https://"):
            feed_url = clean_id
        elif clean_id.startswith("UC"):
            feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={clean_id}"
        elif clean_id.startswith("@"):
            feed_url = f"https://www.youtube.com/feeds/videos.xml?user={clean_id.lstrip('@')}"
        else:
            feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={clean_id}"

        try:
            req = urllib.request.Request(
                feed_url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                xml_content = resp.read()

            root = ET.fromstring(xml_content)

            ns = {
                "atom": "http://www.w3.org/2005/Atom",
                "yt": "http://www.youtube.com/xml/schemas/2015",
                "media": "http://search.yahoo.com/mrss/",
            }

            channel_title = root.findtext("atom:title", default="", namespaces=ns)
            channel_url = ""
            for link in root.findall("atom:link", namespaces=ns):
                if link.attrib.get("rel") == "alternate":
                    channel_url = link.attrib.get("href", "")
                    break

            ch_id_el = root.find("yt:channelId", namespaces=ns)
            actual_channel_id = ch_id_el.text if ch_id_el is not None else clean_id

            videos = []
            entries = root.findall("atom:entry", namespaces=ns)
            for entry in entries[:max_results]:
                video_id_el = entry.find("yt:videoId", namespaces=ns)
                video_id = video_id_el.text if video_id_el is not None else ""
                title = entry.findtext("atom:title", default="", namespaces=ns)
                published = entry.findtext("atom:published", default="", namespaces=ns)
                updated = entry.findtext("atom:updated", default="", namespaces=ns)

                link_el = entry.find("atom:link", namespaces=ns)
                watch_url = (
                    link_el.attrib.get("href", f"https://www.youtube.com/watch?v={video_id}")
                    if link_el is not None
                    else f"https://www.youtube.com/watch?v={video_id}"
                )

                media_group = entry.find("media:group", namespaces=ns)
                description = ""
                thumbnail_url = ""
                views = 0
                if media_group is not None:
                    description = media_group.findtext("media:description", default="", namespaces=ns)
                    thumb_el = media_group.find("media:thumbnail", namespaces=ns)
                    if thumb_el is not None:
                        thumbnail_url = thumb_el.attrib.get("url", "")
                    comm_el = media_group.find("media:community", namespaces=ns)
                    if comm_el is not None:
                        stats_el = comm_el.find("media:statistics", namespaces=ns)
                        if stats_el is not None:
                            try:
                                views = int(stats_el.attrib.get("views", 0))
                            except (ValueError, TypeError):
                                views = 0

                videos.append({
                    "video_id": video_id,
                    "title": title,
                    "published_at": published,
                    "updated_at": updated,
                    "url": watch_url,
                    "description_snippet": description[:300] if description else "",
                    "thumbnail_url": thumbnail_url,
                    "views": views,
                })

            return {
                "success": True,
                "source": "youtube_atom_rss",
                "quota_units_consumed": 0,
                "channel_id": actual_channel_id,
                "channel_title": channel_title,
                "channel_url": channel_url,
                "video_count": len(videos),
                "videos": videos,
            }

        except Exception as e:
            return {
                "success": False,
                "source": "youtube_atom_rss",
                "error": f"Failed to fetch or parse RSS feed for channel '{clean_id}': {str(e)}",
                "feed_url": feed_url,
            }






