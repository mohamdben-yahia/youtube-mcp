"""Unit tests for server.py tool definitions and dispatch."""

import pytest
from unittest.mock import patch, MagicMock
from youtube_mcp.server import (
    mcp,
    search_videos,
    get_video_details,
    get_video_transcript,
    get_channel_details,
    get_playlist_items,
    get_video_comments,
)


@pytest.mark.asyncio
async def test_server_tools_registered():
    """Verify that all 6 tools are registered on the MCPServer instance."""
    tools = await mcp.list_tools()
    tool_names = {t.name for t in tools}

    expected_tools = {
        "search_videos",
        "get_video_details",
        "get_video_transcript",
        "get_channel_details",
        "get_playlist_items",
        "get_video_comments",
        "scout_niche_channels",
        "get_trending_niches",
        "audit_channel_strategy",
        "find_viral_outliers",
        "analyze_audience_sentiment",
        "compare_channels",
        "extract_shorts_clips",
        "blueprint_new_channel",
        "search_channels",
        "reverse_engineer_channel",
        "find_breakout_growth_channels",
        "find_content_gaps",
        "generate_retention_script_outline",
        "discover_niche_sponsors",
    }
    assert expected_tools.issubset(tool_names)


@patch("youtube_mcp.server.get_client")
def test_search_videos_tool(mock_get_client):
    mock_client = MagicMock()
    mock_client.search.return_value = {"success": True, "results": []}
    mock_get_client.return_value = mock_client

    res = search_videos(query="test", max_results=5)
    assert res["success"] is True
    mock_client.search.assert_called_once_with(
        query="test",
        max_results=5,
        search_type="video",
        order="relevance",
        published_after=None,
        region_code=None,
        raw=False,
    )


@patch("youtube_mcp.server.get_client")
def test_get_video_details_tool(mock_get_client):
    mock_client = MagicMock()
    mock_client.get_video_details.return_value = {"success": True, "videos": []}
    mock_get_client.return_value = mock_client

    res = get_video_details(video_ids=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"])
    assert res["success"] is True
    mock_client.get_video_details.assert_called_once_with(
        video_ids=["dQw4w9WgXcQ"],
        raw=False,
    )


@patch("youtube_mcp.server.fetch_transcript")
def test_get_video_transcript_tool(mock_fetch):
    mock_fetch.return_value = {"success": True, "content": "hello world"}

    res = get_video_transcript(video_id_or_url="dQw4w9WgXcQ", format="text")
    assert res["success"] is True
    mock_fetch.assert_called_once_with(
        video_id_or_url="dQw4w9WgXcQ",
        languages=None,
        output_format="text",
        start_seconds=None,
        end_seconds=None,
    )


@patch("youtube_mcp.server.get_client")
def test_get_channel_details_tool(mock_get_client):
    mock_client = MagicMock()
    mock_client.get_channel_details.return_value = {"success": True, "channel": {}}
    mock_get_client.return_value = mock_client

    res = get_channel_details(for_handle="@veritasium")
    assert res["success"] is True
    mock_client.get_channel_details.assert_called_once_with(
        channel_id=None,
        for_handle="@veritasium",
        for_username=None,
        raw=False,
    )


@patch("youtube_mcp.server.get_client")
def test_get_playlist_items_tool(mock_get_client):
    mock_client = MagicMock()
    mock_client.get_playlist_items.return_value = {"success": True, "items": []}
    mock_get_client.return_value = mock_client

    res = get_playlist_items(playlist_id="PL123")
    assert res["success"] is True
    mock_client.get_playlist_items.assert_called_once_with(
        playlist_id="PL123",
        max_results=20,
        page_token=None,
        raw=False,
    )


@patch("youtube_mcp.server.get_client")
def test_get_video_comments_tool(mock_get_client):
    mock_client = MagicMock()
    mock_client.get_video_comments.return_value = {"success": True, "comments": []}
    mock_get_client.return_value = mock_client

    res = get_video_comments(video_id="https://youtu.be/dQw4w9WgXcQ")
    assert res["success"] is True
    mock_client.get_video_comments.assert_called_once_with(
        video_id="dQw4w9WgXcQ",
        max_results=20,
        order="relevance",
        page_token=None,
        raw=False,
    )


@patch("youtube_mcp.server.get_client")
def test_scout_niche_channels_tool(mock_get_client):
    from youtube_mcp.server import scout_niche_channels
    mock_client = MagicMock()
    mock_client.scout_niche_channels.return_value = {"success": True, "campaigns": {}}
    mock_get_client.return_value = mock_client

    res = scout_niche_channels(
        niches=["ai automation", "saas"],
        min_subscribers=10000,
        max_subscribers=100000,
        min_videos=5,
        region_code="US",
        channels_per_niche=5,
        sort_by="subscribers",
    )
    assert res["success"] is True
    mock_client.scout_niche_channels.assert_called_once_with(
        niches=["ai automation", "saas"],
        min_subscribers=10000,
        max_subscribers=100000,
        min_videos=5,
        region_code="US",
        channels_per_niche=5,
        sort_by="subscribers",
    )


@patch("youtube_mcp.server.get_client")
def test_get_trending_niches_tool(mock_get_client):
    from youtube_mcp.server import get_trending_niches
    mock_client = MagicMock()
    mock_client.get_trending_niches.return_value = {"success": True, "top_rising_tags": []}
    mock_get_client.return_value = mock_client

    res = get_trending_niches(region_code="US", category="tech", max_results=15, raw=False)
    assert res["success"] is True
    mock_client.get_trending_niches.assert_called_once_with(
        region_code="US",
        category="tech",
        max_results=15,
        raw=False,
    )


@patch("youtube_mcp.server.get_client")
def test_audit_channel_strategy_tool(mock_get_client):
    from youtube_mcp.server import audit_channel_strategy
    mock_client = MagicMock()
    mock_client.audit_channel_strategy.return_value = {"success": True, "strategy_audit": {}}
    mock_get_client.return_value = mock_client

    res = audit_channel_strategy(channel_id_or_handle="@mkbhd", sample_videos=7)
    assert res["success"] is True
    mock_client.audit_channel_strategy.assert_called_once_with(
        channel_id_or_handle="@mkbhd",
        sample_videos=7,
    )


@patch("youtube_mcp.server.get_client")
def test_find_viral_outliers_tool(mock_get_client):
    from youtube_mcp.server import find_viral_outliers
    mock_client = MagicMock()
    mock_client.find_viral_outliers.return_value = {"success": True, "outliers": []}
    mock_get_client.return_value = mock_client

    res = find_viral_outliers(query="ai productivity", min_multiplier=3.0, max_results=10)
    assert res["success"] is True
    mock_client.find_viral_outliers.assert_called_once_with(
        query="ai productivity",
        min_multiplier=3.0,
        published_after=None,
        max_results=10,
    )


@patch("youtube_mcp.server.get_client")
def test_analyze_audience_sentiment_tool(mock_get_client):
    from youtube_mcp.server import analyze_audience_sentiment
    mock_client = MagicMock()
    mock_client.analyze_audience_sentiment.return_value = {"success": True, "sentiment_distribution": {}}
    mock_get_client.return_value = mock_client

    res = analyze_audience_sentiment(video_id_or_url="dQw4w9WgXcQ", max_comments=50)
    assert res["success"] is True
    mock_client.analyze_audience_sentiment.assert_called_once_with(
        video_id_or_url="dQw4w9WgXcQ",
        max_comments=50,
    )


@patch("youtube_mcp.server.get_client")
def test_compare_channels_tool(mock_get_client):
    from youtube_mcp.server import compare_channels
    mock_client = MagicMock()
    mock_client.compare_channels.return_value = {"success": True, "channels": []}
    mock_get_client.return_value = mock_client

    res = compare_channels(channel_handles=["@mkbhd", "@dave2d"])
    assert res["success"] is True
    mock_client.compare_channels.assert_called_once_with(
        channel_handles=["@mkbhd", "@dave2d"],
    )


@patch("youtube_mcp.server.generate_video_chapters_and_clips")
def test_extract_shorts_clips_tool(mock_clips):
    from youtube_mcp.server import extract_shorts_clips
    mock_clips.return_value = {"success": True, "recommended_shorts_clips": []}

    res = extract_shorts_clips(video_id_or_url="dQw4w9WgXcQ", min_duration_seconds=25, max_duration_seconds=50, max_clips=3)
    assert res["success"] is True
    mock_clips.assert_called_once_with(
        video_id_or_url="dQw4w9WgXcQ",
        min_duration_seconds=25,
        max_duration_seconds=50,
        max_clips=3,
    )


@patch("youtube_mcp.server.get_client")
def test_blueprint_new_channel_tool(mock_get_client):
    from youtube_mcp.server import blueprint_new_channel
    mock_client = MagicMock()
    mock_client.blueprint_new_channel.return_value = {"success": True, "niche": "notion tutorials"}
    mock_get_client.return_value = mock_client

    res = blueprint_new_channel(niche="notion tutorials", target_audience="students", region_code="US")
    assert res["success"] is True
    mock_client.blueprint_new_channel.assert_called_once_with(
        niche="notion tutorials",
        target_audience="students",
        region_code="US",
    )


@patch("youtube_mcp.server.get_client")
def test_search_channels_tool(mock_get_client):
    from youtube_mcp.server import search_channels
    mock_client = MagicMock()
    mock_client.search_channels.return_value = {"success": True, "channels": []}
    mock_get_client.return_value = mock_client

    res = search_channels(query="ai creators", max_results=5)
    assert res["success"] is True
    mock_client.search_channels.assert_called_once_with(
        query="ai creators",
        max_results=5,
        order="relevance",
        region_code=None,
    )


@patch("youtube_mcp.server.get_client")
def test_reverse_engineer_channel_tool(mock_get_client):
    from youtube_mcp.server import reverse_engineer_channel
    mock_client = MagicMock()
    mock_client.reverse_engineer_channel.return_value = {"success": True, "channel": {}}
    mock_get_client.return_value = mock_client

    res = reverse_engineer_channel(channel_id_or_handle="@mkbhd", sample_videos=5, include_audience_gaps=True)
    assert res["success"] is True
    mock_client.reverse_engineer_channel.assert_called_once_with(
        channel_id_or_handle="@mkbhd",
        sample_videos=5,
        include_audience_gaps=True,
    )


@patch("youtube_mcp.server.get_client")
def test_find_breakout_growth_channels_tool(mock_get_client):
    from youtube_mcp.server import find_breakout_growth_channels
    mock_client = MagicMock()
    mock_client.find_breakout_growth_channels.return_value = {"success": True, "breakout_channels": []}
    mock_get_client.return_value = mock_client

    res = find_breakout_growth_channels(niche="ai coding", max_channel_age_months=18, min_subscribers=5000)
    assert res["success"] is True
    mock_client.find_breakout_growth_channels.assert_called_once_with(
        niche="ai coding",
        max_channel_age_months=18,
        min_subscribers=5000,
        max_subscribers=300000,
        region_code="US",
        max_results=10,
    )


@patch("youtube_mcp.server.get_client")
def test_find_content_gaps_tool(mock_get_client):
    from youtube_mcp.server import find_content_gaps
    mock_client = MagicMock()
    mock_client.find_content_gaps.return_value = {"success": True, "content_gap_opportunity": "HIGH"}
    mock_get_client.return_value = mock_client

    res = find_content_gaps(niche_or_topic="python for finance", max_results=10)
    assert res["success"] is True
    mock_client.find_content_gaps.assert_called_once_with(
        niche_or_topic="python for finance",
        max_results=10,
        region_code="US",
    )


@patch("youtube_mcp.server.get_client")
def test_generate_retention_script_outline_tool(mock_get_client):
    from youtube_mcp.server import generate_retention_script_outline
    mock_client = MagicMock()
    mock_client.generate_retention_script_outline.return_value = {"success": True, "retention_script_outline": []}
    mock_get_client.return_value = mock_client

    res = generate_retention_script_outline(video_title_or_topic="Build an MCP Server", target_duration_minutes=12)
    assert res["success"] is True
    mock_client.generate_retention_script_outline.assert_called_once_with(
        video_title_or_topic="Build an MCP Server",
        competitor_video_id_or_url=None,
        target_audience="Beginners",
        target_duration_minutes=12,
    )


@patch("youtube_mcp.server.get_client")
def test_discover_niche_sponsors_tool(mock_get_client):
    from youtube_mcp.server import discover_niche_sponsors
    mock_client = MagicMock()
    mock_client.discover_niche_sponsors.return_value = {"success": True, "top_active_sponsors": []}
    mock_get_client.return_value = mock_client

    res = discover_niche_sponsors(niche_or_query="productivity apps", sample_videos=15)
    assert res["success"] is True
    mock_client.discover_niche_sponsors.assert_called_once_with(
        niche_or_query="productivity apps",
        sample_videos=15,
        region_code="US",
    )


@pytest.mark.asyncio
async def test_server_prompts_registered():
    """Verify that beginner and creator prompts are registered."""
    prompts = await mcp.list_prompts()
    prompt_names = {p.name for p in prompts}
    expected_prompts = {
        "launch_new_channel_prompt",
        "viral_video_ideas_prompt",
        "competitor_playbook_prompt",
    }
    assert expected_prompts.issubset(prompt_names)

