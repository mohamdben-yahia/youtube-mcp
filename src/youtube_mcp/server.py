import os
import json
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
def search_channels(
    query: str,
    max_results: int = 10,
    order: str = "relevance",
    region_code: Optional[str] = None,
) -> Dict[str, Any]:
    """Search YouTube specifically for channels matching a query or niche, enriched with subscribers, views, and video counts.

    Ideal for creator discovery, niche research, and competitor mapping.

    Args:
        query: Topic or niche keywords (e.g. 'ai automation', 'budget travel', 'investing for beginners').
        max_results: Number of channels to return (1 to 50, default 10).
        order: Ranking order ('relevance', 'videoCount', 'viewCount', 'rating').
        region_code: ISO 3166-1 alpha-2 country code (e.g. 'US', 'GB', 'CA').
    """
    client = get_client()
    return client.search_channels(
        query=query,
        max_results=max_results,
        order=order,
        region_code=region_code,
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
def reverse_engineer_channel(
    channel_id_or_handle: str,
    sample_videos: int = 5,
    include_audience_gaps: bool = True,
) -> Dict[str, Any]:
    """Perform full end-to-end reverse engineering on any YouTube channel.

    Deconstructs upload cadence, view-to-sub engagement ratio, title formulas,
    the opening 60s script hook of their top video, full monetization funnel,
    and mines real viewer comments for unmet content requests and pain points.
    Delivers a step-by-step replication playbook for a new creator to model or compete.

    Args:
        channel_id_or_handle: Channel handle (e.g. '@mkbhd', '@aliabdaal'), channel ID ('UC...'), or username.
        sample_videos: Number of recent uploads to analyze (3 to 15, default 5).
        include_audience_gaps: If True, mines the comment section of their top video for unmet viewer needs.
    """
    client = get_client()
    return client.reverse_engineer_channel(
        channel_id_or_handle=channel_id_or_handle,
        sample_videos=sample_videos,
        include_audience_gaps=include_audience_gaps,
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


@mcp.tool()
def find_breakout_growth_channels(
    niche: str,
    max_channel_age_months: int = 24,
    min_subscribers: int = 1000,
    max_subscribers: int = 300000,
    region_code: Optional[str] = "US",
    max_results: int = 10,
) -> Dict[str, Any]:
    """Find modern breakout channels created recently that grew rapidly from scratch.

    Discovers new channels that recently solved the YouTube algorithm rather than legacy giants.

    Args:
        niche: Topic or niche keyword (e.g. 'ai automation', 'finance beginners').
        max_channel_age_months: Maximum channel age in months (default 24).
        min_subscribers: Minimum subscribers (default 1000).
        max_subscribers: Maximum subscribers (default 300000).
        region_code: ISO country code (default 'US').
        max_results: Max results to return (default 10).
    """
    client = get_client()
    return client.find_breakout_growth_channels(
        niche=niche,
        max_channel_age_months=max_channel_age_months,
        min_subscribers=min_subscribers,
        max_subscribers=max_subscribers,
        region_code=region_code,
        max_results=max_results,
    )


@mcp.tool()
def find_content_gaps(
    niche_or_topic: str,
    max_results: int = 15,
    region_code: Optional[str] = "US",
) -> Dict[str, Any]:
    """Identify high-demand content gaps and low-competition keyword opportunities.

    Finds topics where top search results are outdated (2+ years old), signaling easy ranking
    opportunities for a new channel to displace them with a fresh 2026 update.

    Args:
        niche_or_topic: Topic, query, or question to analyze (e.g. 'how to learn sql for data analysis').
        max_results: Number of search results to inspect (default 15).
        region_code: ISO country code (default 'US').
    """
    client = get_client()
    return client.find_content_gaps(
        niche_or_topic=niche_or_topic,
        max_results=max_results,
        region_code=region_code,
    )


@mcp.tool()
def generate_retention_script_outline(
    video_title_or_topic: str,
    competitor_video_id_or_url: Optional[str] = None,
    target_audience: str = "Beginners",
    target_duration_minutes: int = 10,
) -> Dict[str, Any]:
    """Generate a full 8-12 minute retention-engineered YouTube video script outline.

    Reverse-engineers competitor transcripts for opening hooks and integrates real viewer
    pain points from comments to maximize watch time and viewer satisfaction.

    Args:
        video_title_or_topic: The topic or title of the video to outline.
        competitor_video_id_or_url: Optional competitor video to model hook and structure from.
        target_audience: Ideal viewer demographic (default 'Beginners').
        target_duration_minutes: Target video runtime in minutes (default 10).
    """
    client = get_client()
    return client.generate_retention_script_outline(
        video_title_or_topic=video_title_or_topic,
        competitor_video_id_or_url=competitor_video_id_or_url,
        target_audience=target_audience,
        target_duration_minutes=target_duration_minutes,
    )


@mcp.tool()
def discover_niche_sponsors(
    niche_or_query: str,
    sample_videos: int = 20,
    region_code: Optional[str] = "US",
) -> Dict[str, Any]:
    """Discover brands actively sponsoring creators in a niche with discount codes and URLs.

    Reveals companies with active influencer marketing budgets in your niche so you can pitch
    them as soon as you reach 1k-5k views per video.

    Args:
        niche_or_query: Niche topic or keyword (e.g. 'productivity apps', 'coding', 'fitness').
        sample_videos: Number of top videos to inspect (10 to 30, default 20).
        region_code: Country code (default 'US').
    """
    client = get_client()
    return client.discover_niche_sponsors(
        niche_or_query=niche_or_query,
        sample_videos=sample_videos,
        region_code=region_code,
    )


@mcp.tool()
def generate_thumbnail_concepts(
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
    client = get_client()
    return client.generate_thumbnail_concepts(
        video_title=video_title,
        target_niche=target_niche,
        competitor_video_id_or_url=competitor_video_id_or_url,
    )


@mcp.tool()
def generate_seo_metadata_pack(
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
    client = get_client()
    return client.generate_seo_metadata_pack(
        topic=topic,
        key_takeaways=key_takeaways,
        channel_name=channel_name,
        affiliate_links=affiliate_links,
    )


@mcp.tool()
def export_research_report(
    niche: str,
    target_audience: Optional[str] = None,
    output_file: Optional[str] = None,
    region_code: str = "US",
) -> Dict[str, Any]:
    """Generate a publication-ready Markdown research report for Notion or Obsidian.

    Runs comprehensive market research and formats it into an executive-ready .md document
    complete with tables, competitor rankings, viral video links, comment insights, and a 5-video roadmap.

    Args:
        niche: Topic or niche (e.g. 'ai automation', 'productivity systems', 'personal finance').
        target_audience: Optional target audience description (e.g. 'beginners', 'freelancers').
        output_file: Optional path where to save the markdown file (defaults to reports/<niche>_research_report.md).
        region_code: Country market code (default 'US').
    """
    client = get_client()
    return client.export_research_report(
        niche=niche,
        target_audience=target_audience,
        output_file=output_file,
        region_code=region_code,
    )


@mcp.tool()
def find_cross_language_opportunities(
    topic: str,
    target_language: str = "es",
    target_region: str = "ES",
    max_results: int = 5,
) -> Dict[str, Any]:
    """Identify proven viral US/English video concepts with low competition in non-English markets.

    Analyzes viral performance of English videos and checks competition levels in the target
    language / region (Spanish, French, German, Portuguese, Italian, Arabic, Japanese), providing
    translated title frameworks and market arbitrage scores.

    Args:
        topic: Core topic in English (e.g. 'notion for students', 'ai automation', 'intermittent fasting').
        target_language: Target language code ('es', 'fr', 'de', 'pt', 'it', 'ar', 'ja').
        target_region: Target country code ('ES', 'MX', 'FR', 'DE', 'BR', 'IT', 'JP', 'SA').
        max_results: Max opportunities to return (default 5).
    """
    client = get_client()
    return client.find_cross_language_opportunities(
        topic=topic,
        target_language=target_language,
        target_region=target_region,
        max_results=max_results,
    )


@mcp.tool()
def simulate_title_ctr(
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
    client = get_client()
    return client.simulate_title_ctr(
        titles=titles,
        target_niche=target_niche,
    )


@mcp.tool()
def analyze_optimal_upload_time(
    niche_or_channel: str,
    sample_size: int = 25,
    timezone_offset_hours: int = 0,
) -> Dict[str, Any]:
    """Analyze competitor publishing schedules to find the optimal day and hour to upload.

    Inspects publishing timestamps of top videos in a niche or channel, builds
    a day-of-week and hour-of-day distribution, and identifies low-competition "Sweet Spot" windows.

    Args:
        niche_or_channel: Niche topic keyword (e.g. 'coding tutorials', 'finance') or creator handle.
        sample_size: Number of recent competitor uploads to sample (10 to 50, default 25).
        timezone_offset_hours: Timezone offset from UTC in hours (e.g. -5 for EST, +1 for CET, default 0).
    """
    client = get_client()
    return client.analyze_optimal_upload_time(
        niche_or_channel=niche_or_channel,
        sample_size=sample_size,
        timezone_offset_hours=timezone_offset_hours,
    )


@mcp.tool()
def predict_retention_dropoffs(
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
    client = get_client()
    return client.predict_retention_dropoffs(
        script_or_transcript=script_or_transcript,
        video_id_or_url=video_id_or_url,
        target_duration_minutes=target_duration_minutes,
    )


@mcp.tool()
def analyze_community_posts(
    niche_or_channel: str,
    target_goal: str = "growth",
) -> Dict[str, Any]:
    """Generate high-engagement Community Tab polls, quizzes, and discussion posts.

    Leverages YouTube's Community Tab algorithm, which distributes polls into the home feeds
    of non-subscribers, creating viral discovery for new channels between video releases.

    Args:
        niche_or_channel: Topic, niche, or creator handle (e.g. 'python programming', 'personal finance').
        target_goal: Goal for the community strategy ('growth', 'video_validation', 'audience_loyalty').
    """
    client = get_client()
    return client.analyze_community_posts(
        niche_or_channel=niche_or_channel,
        target_goal=target_goal,
    )


@mcp.tool()
def analyze_shorts_to_longform_ratio(
    channel_id_or_handle: str,
    sample_videos: int = 20,
) -> Dict[str, Any]:
    """Analyze a channel's balance between YouTube Shorts and Long-Form videos.

    Calculates publishing ratio, view disparities, conversion efficiency, and provides
    a customized publishing mix recommendation to avoid Shorts cannibalizing long-form watch time.

    Args:
        channel_id_or_handle: Channel handle (e.g. '@aliabdaal', '@mkbhd') or Channel ID.
        sample_videos: Number of recent uploads to evaluate (10 to 50, default 20).
    """
    client = get_client()
    return client.analyze_shorts_to_longform_ratio(
        channel_id_or_handle=channel_id_or_handle,
        sample_videos=sample_videos,
    )


@mcp.tool()
def classify_traffic_potential(
    topic_or_title: str,
    target_niche: Optional[str] = None,
) -> Dict[str, Any]:
    """Classify whether a video topic will succeed via Evergreen Search or Viral Browse Feeds.

    Provides algorithmic traffic predictions, expected RPM / AdSense monetization multipliers,
    longevity expectations (3+ years vs 14 days), and optimized title variants for both traffic channels.

    Args:
        topic_or_title: Candidate video title, topic, or draft concept.
        target_niche: Optional niche context (e.g. 'coding', 'personal finance', 'fitness').
    """
    client = get_client()
    return client.classify_traffic_potential(
        topic_or_title=topic_or_title,
        target_niche=target_niche,
    )


@mcp.tool()
def generate_monetization_offers(
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
    client = get_client()
    return client.generate_monetization_offers(
        niche=niche,
        target_audience=target_audience,
        main_skill_or_topic=main_skill_or_topic,
    )


@mcp.tool()
def design_binge_playlist(
    core_topic: str,
    video_count: int = 5,
    target_audience: Optional[str] = None,
) -> Dict[str, Any]:
    """Architect a 4-to-6 video binge-watching loop engineered to trigger YouTube's Session Watch Time multiplier.

    Structures interconnected video concepts with seamless cliffhanger bridges and end-screen scripts
    so viewers watch multiple videos in sequence, signalling algorithmic promotion.

    Args:
        core_topic: Overarching topic or learning journey (e.g. 'Build a SaaS in Python', 'Notion for Beginners').
        video_count: Number of videos in the binge playlist series (3 to 6, default 5).
        target_audience: Optional target audience context.
    """
    client = get_client()
    return client.design_binge_playlist(
        core_topic=core_topic,
        video_count=video_count,
        target_audience=target_audience,
    )


@mcp.tool()
def get_channel_rss_videos(
    channel_id: str,
    max_results: int = 15,
) -> Dict[str, Any]:
    """Fetch the latest video uploads from a YouTube channel using the public Atom RSS feed.

    Consumes 0 Google Cloud API quota units and requires NO API key. Ideal for monitoring recent
    uploads without burning quota.

    Args:
        channel_id: The YouTube Channel ID (e.g., 'UCuAXFkgsw1L7xaCfnd5JJOw') or channel URL.
        max_results: Maximum recent uploads to return (1 to 15, default 15).
    """
    client = get_client()
    return client.get_channel_rss(channel_id=channel_id, max_results=max_results)


# --- Dynamic MCP Resources (youtube:// URIs) ---

@mcp.resource("youtube://trending/{category}")
def get_trending_resource(category: str) -> str:
    """Live trending videos and rising keywords context document."""
    client = get_client()
    data = client.get_trending_niches(category=category, max_results=15)
    return json.dumps(data, indent=2)


@mcp.resource("youtube://channel/{handle}/playbook")
def get_channel_playbook_resource(handle: str) -> str:
    """Live reverse-engineered strategy report for any YouTube creator."""
    client = get_client()
    data = client.reverse_engineer_channel(channel_id_or_handle=handle, sample_videos=5)
    return json.dumps(data, indent=2)


@mcp.resource("youtube://niche/{niche}/blueprint")
def get_niche_blueprint_resource(niche: str) -> str:
    """Live 5-video launch roadmap and competitor research for any niche."""
    client = get_client()
    data = client.blueprint_new_channel(niche=niche)
    return json.dumps(data, indent=2)


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
