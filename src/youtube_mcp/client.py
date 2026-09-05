"""YouTube Data API v3 client wrapper with quota and error handling."""

import os
import json
import re
from typing import Any, Dict, List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_mcp.formatters import (
    format_search_results,
    format_video_details,
    format_channel_details,
    format_playlist_item,
    format_comment_thread,
)
from youtube_mcp.transcripts import fetch_transcript


class YouTubeClient:
    """Wrapper around googleapiclient for YouTube Data API v3."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        self._service = None

    @property
    def service(self):
        if self._service is None:
            if not self.api_key:
                raise ValueError(
                    "YOUTUBE_API_KEY is not set. Please set the YOUTUBE_API_KEY environment variable "
                    "or pass it when initializing the client."
                )
            self._service = build("youtube", "v3", developerKey=self.api_key)
        return self._service

    def _handle_http_error(self, e: HttpError) -> Dict[str, Any]:
        """Convert Google API HttpError into a clean, actionable error response."""
        status_code = e.resp.status
        try:
            error_details = json.loads(e.content.decode("utf-8"))
            errors = error_details.get("error", {}).get("errors", [{}])
            reason = errors[0].get("reason", "unknown")
            message = error_details.get("error", {}).get("message", str(e))
        except Exception:
            reason = "unknown"
            message = str(e)

        if reason == "quotaExceeded":
            return {
                "success": False,
                "error": "YouTube Data API quota exceeded.",
                "reason": "quotaExceeded",
                "status_code": status_code,
                "suggestion": "The daily 10,000 unit quota for your YouTube Data API project has been reached. Quota resets at midnight Pacific Time.",
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

            request = self.service.search().list(**params)
            response = request.execute()

            if raw:
                return response

            formatted = format_search_results(query, response)
            return {"success": True, **formatted}

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
            request = self.service.videos().list(
                part="snippet,contentDetails,statistics",
                id=ids_str,
            )
            response = request.execute()

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

            request = self.service.channels().list(**params)
            response = request.execute()

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

            request = self.service.playlistItems().list(**params)
            response = request.execute()

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

            request = self.service.commentThreads().list(**params)
            response = request.execute()

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
        request = self.service.channels().list(
            part="snippet,contentDetails,statistics",
            id=ids_str,
        )
        response = request.execute()
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

                search_res = self.service.search().list(**search_params).execute()
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
                    vid_res = self.service.search().list(**vid_params).execute()
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

            request = self.service.videos().list(**params)
            response = request.execute()

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
            for handle in channel_handles[:5]:  # limit to 5 channels
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
