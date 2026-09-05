"""Formatters to transform raw YouTube API responses into token-efficient structures."""

import re
from typing import Any, Dict, List, Optional
from youtube_mcp.models import (
    VideoSummary,
    ChannelSummary,
    PlaylistItemSummary,
    CommentSummary,
    SearchItem,
    SearchResponse,
)


def parse_iso8601_duration(duration_str: Optional[str]) -> str:
    """Convert an ISO 8601 duration (e.g., 'PT1H23M45S') to human readable format ('1:23:45')."""
    if not duration_str:
        return "N/A"
    
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration_str)
    if not match:
        return duration_str
    
    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def format_search_results(query: str, raw_response: Dict[str, Any]) -> Dict[str, Any]:
    """Extract clean search results from YouTube search.list response."""
    items = raw_response.get("items", [])
    results: List[Dict[str, Any]] = []

    for item in items:
        id_info = item.get("id", {})
        kind = id_info.get("kind", "")
        
        target_id = ""
        url = ""
        category = "unknown"

        if "video" in kind:
            target_id = id_info.get("videoId", "")
            url = f"https://www.youtube.com/watch?v={target_id}"
            category = "video"
        elif "channel" in kind:
            target_id = id_info.get("channelId", "")
            url = f"https://www.youtube.com/channel/{target_id}"
            category = "channel"
        elif "playlist" in kind:
            target_id = id_info.get("playlistId", "")
            url = f"https://www.youtube.com/playlist?list={target_id}"
            category = "playlist"

        snippet = item.get("snippet", {})
        results.append(
            SearchItem(
                id=target_id,
                kind=category,
                title=snippet.get("title", ""),
                channel_title=snippet.get("channelTitle", ""),
                published_at=snippet.get("publishedAt", ""),
                description=snippet.get("description", ""),
                url=url,
            ).model_dump()
        )

    page_info = raw_response.get("pageInfo", {})
    return {
        "query": query,
        "total_results": page_info.get("totalResults"),
        "next_page_token": raw_response.get("nextPageToken"),
        "results": results,
    }


def format_video_details(item: Dict[str, Any]) -> Dict[str, Any]:
    """Format a single video item from YouTube videos.list."""
    video_id = item.get("id", "")
    snippet = item.get("snippet", {})
    content_details = item.get("contentDetails", {})
    statistics = item.get("statistics", {})

    raw_duration = content_details.get("duration")
    human_duration = parse_iso8601_duration(raw_duration)

    return VideoSummary(
        video_id=video_id,
        title=snippet.get("title", ""),
        channel_id=snippet.get("channelId", ""),
        channel_title=snippet.get("channelTitle", ""),
        published_at=snippet.get("publishedAt", ""),
        description=snippet.get("description", ""),
        duration=human_duration,
        view_count=int(statistics.get("viewCount", 0)) if statistics.get("viewCount") else None,
        like_count=int(statistics.get("likeCount", 0)) if statistics.get("likeCount") else None,
        comment_count=int(statistics.get("commentCount", 0)) if statistics.get("commentCount") else None,
        tags=snippet.get("tags", []),
        url=f"https://www.youtube.com/watch?v={video_id}",
    ).model_dump()


def format_channel_details(item: Dict[str, Any]) -> Dict[str, Any]:
    """Format a channel item from YouTube channels.list."""
    channel_id = item.get("id", "")
    snippet = item.get("snippet", {})
    statistics = item.get("statistics", {})
    content_details = item.get("contentDetails", {})
    related_playlists = content_details.get("relatedPlaylists", {})

    uploads_id = related_playlists.get("uploads")
    custom_url = snippet.get("customUrl")

    return ChannelSummary(
        channel_id=channel_id,
        title=snippet.get("title", ""),
        description=snippet.get("description", ""),
        custom_url=custom_url,
        published_at=snippet.get("publishedAt"),
        subscriber_count=int(statistics.get("subscriberCount", 0)) if statistics.get("subscriberCount") else None,
        video_count=int(statistics.get("videoCount", 0)) if statistics.get("videoCount") else None,
        view_count=int(statistics.get("viewCount", 0)) if statistics.get("viewCount") else None,
        uploads_playlist_id=uploads_id,
        url=f"https://www.youtube.com/{custom_url}" if custom_url else f"https://www.youtube.com/channel/{channel_id}",
    ).model_dump()


def format_playlist_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Format an item from YouTube playlistItems.list."""
    snippet = item.get("snippet", {})
    resource_id = snippet.get("resourceId", {})
    video_id = resource_id.get("videoId", "")

    return PlaylistItemSummary(
        video_id=video_id,
        title=snippet.get("title", ""),
        channel_title=snippet.get("videoOwnerChannelTitle", snippet.get("channelTitle", "")),
        published_at=snippet.get("publishedAt", ""),
        position=snippet.get("position", 0),
        url=f"https://www.youtube.com/watch?v={video_id}",
    ).model_dump()


def format_comment_thread(item: Dict[str, Any]) -> Dict[str, Any]:
    """Format an item from YouTube commentThreads.list."""
    snippet = item.get("snippet", {})
    top_comment = snippet.get("topLevelComment", {}).get("snippet", {})
    comment_id = item.get("id", "")

    return CommentSummary(
        comment_id=comment_id,
        author=top_comment.get("authorDisplayName", "Unknown"),
        author_channel_url=top_comment.get("authorChannelUrl"),
        text=top_comment.get("textDisplay", ""),
        like_count=int(top_comment.get("likeCount", 0)),
        published_at=top_comment.get("publishedAt", ""),
        reply_count=int(snippet.get("totalReplyCount", 0)),
    ).model_dump()
