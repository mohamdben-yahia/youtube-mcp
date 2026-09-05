import os
from typing import Any, Dict, List, Optional

try:
    from mcp.server.mcpserver import MCPServer
except ImportError:
    from mcp.server.fastmcp import FastMCP as MCPServer

from youtube_mcp.client import YouTubeClient
from youtube_mcp.transcripts import (
    fetch_transcript,
    extract_video_id,
    generate_video_chapters_and_clips,
)

# Initialize MCP application
mcp = MCPServer("youtube-mcp")

# Lazy-initialized client
_client: Optional[YouTubeClient] = None


def get_client() -> YouTubeClient:
    """Get or initialize the shared YouTubeClient instance."""
    global _client
    if _client is None:
        _client = YouTubeClient()
    return _client


@mcp.tool()
def search_videos(
    query: str,
    max_results: int = 10,
    search_type: str = "video",
    order: str = "relevance",
    published_after: Optional[str] = None,
    region_code: Optional[str] = None,
    raw: bool = False,
) -> Dict[str, Any]:
    """Search YouTube for videos, channels, or playlists.

    Args:
        query: Search keywords or query string.
        max_results: Number of results to return (1 to 50, default 10).
        search_type: Type of resource to search for ('video', 'channel', 'playlist').
        order: Sort order ('relevance', 'date', 'rating', 'viewCount', 'title').
        published_after: RFC 3339 formatted date-time string (e.g. '2024-01-01T00:00:00Z').
        region_code: ISO 3166-1 alpha-2 country code (e.g. 'US', 'FR').
        raw: If True, returns unaltered raw YouTube Data API response.
    """
    client = get_client()
    return client.search(
        query=query,
        max_results=max_results,
        search_type=search_type,
        order=order,
        published_after=published_after,
        region_code=region_code,
        raw=raw,
    )


@mcp.tool()
def get_video_details(
    video_ids: List[str],
    raw: bool = False,
) -> Dict[str, Any]:
    """Retrieve metadata, views, likes, duration, and tags for one or more YouTube videos.

    Args:
        video_ids: List of 11-character video IDs or URLs (up to 50 IDs).
        raw: If True, returns unaltered raw YouTube Data API response.
    """
    cleaned_ids = [extract_video_id(vid) for vid in video_ids]
    client = get_client()
    return client.get_video_details(video_ids=cleaned_ids, raw=raw)


@mcp.tool()
def get_video_transcript(
    video_id_or_url: str,
    languages: Optional[List[str]] = None,
    format: str = "text",
    start_seconds: Optional[float] = None,
    end_seconds: Optional[float] = None,
) -> Dict[str, Any]:
    """Retrieve full video transcripts or subtitles without requiring an API key.

    Args:
        video_id_or_url: YouTube video ID or full URL (e.g., 'dQw4w9WgXcQ' or 'https://youtu.be/...').
        languages: Language priority list (e.g., ['en', 'es']). Defaults to ['en'].
        format: Output format: 'text' (concatenated string), 'timestamped' (lines with [hh:mm:ss]), or 'json' (array of segment objects).
        start_seconds: Optional start timestamp to filter segments.
        end_seconds: Optional end timestamp to filter segments.
    """
    return fetch_transcript(
        video_id_or_url=video_id_or_url,
        languages=languages,
        output_format=format,
        start_seconds=start_seconds,
        end_seconds=end_seconds,
    )


@mcp.tool()
def get_channel_details(
    channel_id: Optional[str] = None,
    for_handle: Optional[str] = None,
    for_username: Optional[str] = None,
    raw: bool = False,
) -> Dict[str, Any]:
    """Retrieve channel information, subscriber counts, total views, and uploads playlist ID.

    Provide at least one identifier: channel_id (e.g. 'UC...'), for_handle (e.g. '@mkbhd'), or for_username.

    Args:
        channel_id: YouTube Channel ID (e.g., 'UCBJycsmduvYEL83R_U4JriQ').
        for_handle: YouTube Channel handle with or without '@' (e.g., '@mkbhd' or 'veritasium').
        for_username: YouTube channel legacy username.
        raw: If True, returns unaltered raw YouTube Data API response.
    """
    client = get_client()
    return client.get_channel_details(
        channel_id=channel_id,
        for_handle=for_handle,
        for_username=for_username,
        raw=raw,
    )


@mcp.tool()
def get_playlist_items(
    playlist_id: str,
    max_results: int = 20,
    page_token: Optional[str] = None,
    raw: bool = False,
) -> Dict[str, Any]:
    """Retrieve video items contained within a YouTube playlist.

    Args:
        playlist_id: The ID of the playlist (e.g. 'PLrAXtmErZgOdP_8GzKt233nyGH51l50DH' or channel uploads ID).
        max_results: Number of items to retrieve (up to 50, default 20).
        page_token: Token for retrieving next page of results.
        raw: If True, returns unaltered raw YouTube Data API response.
    """
    client = get_client()
    return client.get_playlist_items(
        playlist_id=playlist_id,
        max_results=max_results,
        page_token=page_token,
        raw=raw,
    )


@mcp.tool()
def get_video_comments(
    video_id: str,
    max_results: int = 20,
    order: str = "relevance",
    page_token: Optional[str] = None,
    raw: bool = False,
) -> Dict[str, Any]:
    """Retrieve top-level comment threads and discussions for a video.

    Args:
        video_id: Video ID or URL to fetch comments for.
        max_results: Number of comments to retrieve (up to 100, default 20).
        order: Sort order: 'relevance' (most popular) or 'time' (newest first).
        page_token: Token for retrieving next page of comments.
        raw: If True, returns unaltered raw YouTube Data API response.
    """
    cleaned_id = extract_video_id(video_id)
    client = get_client()
    return client.get_video_comments(
        video_id=cleaned_id,
        max_results=max_results,
        order=order,
        page_token=page_token,
        raw=raw,
    )


@mcp.tool()
def scout_niche_channels(
    niches: List[str],
    min_subscribers: int = 0,
    max_subscribers: Optional[int] = None,
    min_videos: int = 1,
    region_code: Optional[str] = None,
    channels_per_niche: int = 10,
    sort_by: str = "subscribers",
) -> Dict[str, Any]:
    """Launch a multi-niche discovery campaign to identify and rank top YouTube channels.

    Useful for creator scouting, influencer marketing campaigns, competitor analysis,
    and sponsorship outreach.

    Args:
        niches: List of niche keywords/topics (e.g. ['ai automation', 'saas tools', 'b2b sales']).
        min_subscribers: Minimum subscriber threshold (e.g. 5000 or 10000 for micro-influencers).
        max_subscribers: Optional maximum subscriber threshold (e.g. 100000).
        min_videos: Minimum video count to filter out inactive accounts (default: 1).
        region_code: ISO 3166-1 alpha-2 country code (e.g. 'US', 'GB', 'FR').
        channels_per_niche: Number of top channels to return per niche (default: 10).
        sort_by: Ranking attribute: 'subscribers' (default), 'views', 'videos', or 'avg_views'.
    """
    client = get_client()
    return client.scout_niche_channels(
        niches=niches,
        min_subscribers=min_subscribers,
        max_subscribers=max_subscribers,
        min_videos=min_videos,
        region_code=region_code,
        channels_per_niche=channels_per_niche,
        sort_by=sort_by,
    )


@mcp.tool()
def get_trending_niches(
    region_code: str = "US",
    category: Optional[str] = "tech",
    max_results: int = 25,
    raw: bool = False,
) -> Dict[str, Any]:
    """Discover real-time trending topics, breakout niches, and viral videos right now.

    Analyzes YouTube's official real-time trending chart to extract top rising tags,
    recurring title keywords, and breakout creators dominating the algorithm.

    Args:
        region_code: Country code (default 'US', e.g. 'GB', 'CA', 'DE', 'FR', 'IN').
        category: Niche category ('all', 'tech', 'gaming', 'education', 'howto', 'entertainment', 'news', 'music', 'sports') or numeric ID.
        max_results: Number of trending videos to analyze (up to 50, default 25).
        raw: If True, returns unaltered raw YouTube Data API response.
    """
    client = get_client()
    return client.get_trending_niches(
        region_code=region_code,
        category=category,
        max_results=max_results,
        raw=raw,
    )


@mcp.tool()
def audit_channel_strategy(
    channel_id_or_handle: str,
    sample_videos: int = 5,
) -> Dict[str, Any]:
    """Reverse-engineer any YouTube channel's content strategy and monetization model.

    Analyzes upload cadence, view performance distribution, title formulas,
    monetization links (sponsors, newsletters, affiliate links), and extracts
    the opening script hook from their top-performing video.

    Args:
        channel_id_or_handle: Channel handle (e.g. '@mkbhd', '@aliabdaal'), channel ID ('UC...'), or username.
        sample_videos: Number of recent uploads to analyze (3 to 15, default 5).
    """
    client = get_client()
    return client.audit_channel_strategy(
        channel_id_or_handle=channel_id_or_handle,
        sample_videos=sample_videos,
    )


@mcp.tool()
def find_viral_outliers(
    query: str,
    min_multiplier: float = 2.5,
    published_after: Optional[str] = None,
    max_results: int = 25,
) -> Dict[str, Any]:
    """Identify viral outlier videos that perform dramatically above a channel's normal average.

    Discovers breakout video ideas from either a specific creator (e.g. '@creator') or
    across a broad niche topic (e.g. 'productivity tools') by flagging videos whose views
    surpass the channel's subscriber/view baseline by 2.5x, 5x, or 10x+.

    Args:
        query: Niche topic keyword or creator handle ('@creator').
        min_multiplier: Outlier threshold multiplier (default 2.5 means 2.5x the channel benchmark).
        published_after: RFC 3339 datetime to filter recent breakouts (e.g. '2024-01-01T00:00:00Z').
        max_results: Number of candidates to evaluate (up to 50, default 25).
    """
    client = get_client()
    return client.find_viral_outliers(
        query=query,
        min_multiplier=min_multiplier,
        published_after=published_after,
        max_results=max_results,
    )


@mcp.tool()
def analyze_audience_sentiment(
    video_id_or_url: str,
    max_comments: int = 100,
) -> Dict[str, Any]:
    """Mine video comments to discover audience pain points, questions, and content requests.

    Identifies what viewers struggle with, questions the creator missed,
    topics requested for future videos, and the highest-upvoted comments.

    Args:
        video_id_or_url: YouTube Video ID or full URL.
        max_comments: Number of top comments to analyze (up to 100, default 100).
    """
    client = get_client()
    return client.analyze_audience_sentiment(
        video_id_or_url=video_id_or_url,
        max_comments=max_comments,
    )


@mcp.tool()
def compare_channels(
    channel_handles: List[str],
) -> Dict[str, Any]:
    """Perform a head-to-head benchmarking comparison between 2 to 5 competing YouTube channels.

    Compares subscriber growth velocity, recent average views, upload cadence,
    views-to-subscriber efficiency, and highlights category winners.

    Args:
        channel_handles: List of 2 to 5 channel handles (e.g. ['@mkbhd', '@dave2d']) or Channel IDs.
    """
    client = get_client()
    return client.compare_channels(
        channel_handles=channel_handles,
    )


@mcp.tool()
def extract_shorts_clips(
    video_id_or_url: str,
    min_duration_seconds: int = 20,
    max_duration_seconds: int = 60,
    max_clips: int = 5,
) -> Dict[str, Any]:
    """Generate YouTube chapters and extract the top 30-60s viral Shorts/Reels clips from transcripts.

    Does NOT require a YouTube API key. Scans spoken transcripts for psychological hook triggers
    and formats timestamps ready to paste into video descriptions or feed into video editors.

    Args:
        video_id_or_url: YouTube Video ID or full URL.
        min_duration_seconds: Minimum clip duration for Shorts/Reels (default 20).
        max_duration_seconds: Maximum clip duration for Shorts/Reels (default 60).
        max_clips: Maximum number of candidate clips to return (default 5).
    """
    return generate_video_chapters_and_clips(
        video_id_or_url=video_id_or_url,
        min_duration_seconds=min_duration_seconds,
        max_duration_seconds=max_duration_seconds,
        max_clips=max_clips,
    )


@mcp.tool()
def blueprint_new_channel(
    niche: str,
    target_audience: Optional[str] = None,
    region_code: str = "US",
) -> Dict[str, Any]:
    """Conduct a full market research study and launch blueprint for starting a new YouTube channel.

    Specifically engineered for beginners and new creators. Validates topic demand,
    identifies 3-5 realistic mid-sized channels to model (1k-300k subs), discovers proven
    outlier video topics where smaller channels blew up, mines audience pain points from comments,
    and provides a ready-to-record 5-video launch roadmap with recommended upload cadence.

    Args:
        niche: The niche/topic you want to launch a channel in (e.g. 'ai automation', 'budget travel', 'personal finance for teens').
        target_audience: Optional description of who your videos are for (e.g. 'complete beginners', 'busy moms').
        region_code: Geographic market code (default 'US', e.g. 'GB', 'CA', 'DE').
    """
    client = get_client()
    return client.blueprint_new_channel(
        niche=niche,
        target_audience=target_audience,
        region_code=region_code,
    )


# --- MCP Prompts for New Creators ---

@mcp.prompt()
def launch_new_channel_prompt(niche: str) -> str:
    """Guided prompt for new creators: full niche research and 30-day launch plan."""
    return f"""You are an elite YouTube growth strategist and channel launch consultant.
A new creator wants to start a successful YouTube channel in the following niche: '{niche}'.

Please perform a comprehensive, data-driven market research study:
1. Run `blueprint_new_channel(niche="{niche}")` to pull real-time competitor data, proven outlier topics, and audience pain points.
2. Analyze 2-3 of the top model channels found using `audit_channel_strategy` to understand their upload schedule, video length, and title formulas.
3. Check `find_viral_outliers(query="{niche}", min_multiplier=2.5)` to find breakout video concepts that generated views for smaller channels.
4. Synthesize all findings into an actionable, step-by-step 'New Channel Launch Blueprint' including:
   - Niche Viability & Competition Assessment
   - Top 3 Creators to Model (and why)
   - First 5 Videos to Record (Titles, Thumbnail Concepts, and First 30-Second Hooks)
   - Recommended Weekly Cadence & Optimal Video Runtime
   - Monetization Roadmap from 0 to 10,000 Subscribers
"""


@mcp.prompt()
def viral_video_ideas_prompt(niche: str) -> str:
    """Guided prompt to generate 10 high-CTR video ideas for beginners with proven demand."""
    return f"""You are a YouTube content director specializing in high-CTR, viral video concepts.
For a new channel in the niche: '{niche}', please:
1. Run `find_viral_outliers(query="{niche}", min_multiplier=2.5)` to identify topics that proved viral for other channels.
2. Extract common complaints and video requests from comments using `analyze_audience_sentiment`.
3. Provide 10 validated video concepts. For each idea include:
   - High-CTR Title (tested against curiosity and threat-avoidance frameworks)
   - Thumbnail Visual Hook description (what viewers see)
   - The Opening 30-Second Script Hook (exact spoken words to maximize viewer retention)
"""


@mcp.prompt()
def competitor_playbook_prompt(creator_handle: str) -> str:
    """Guided prompt to reverse-engineer any creator's strategy for a new channel to model."""
    return f"""You are a YouTube channel auditor.
Please run `audit_channel_strategy(channel_id_or_handle="{creator_handle}")` on '{creator_handle}'.
Break down their exact playbook so a new creator can ethically model what works:
- What is their upload frequency and optimal video length?
- What title formulas and thumbnail patterns do they rely on?
- What is their exact first 60-second hook formula?
- How do they monetize their audience (sponsors, digital products, newsletters)?
- What content gaps are they leaving open that a new creator could fill?
"""
