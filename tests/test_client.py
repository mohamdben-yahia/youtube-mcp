"""Unit tests for client.py."""

import json
import pytest
from unittest.mock import MagicMock, patch
from googleapiclient.errors import HttpError
from httplib2 import Response
from youtube_mcp.client import YouTubeClient


def test_client_missing_key_raises():
    client = YouTubeClient(api_key=None)
    with patch.dict("os.environ", {}, clear=True):
        client.api_key = None
        with pytest.raises(ValueError, match="YOUTUBE_API_KEY is not set"):
            _ = client.service


def test_search_videos_mocked(mock_search_response):
    client = YouTubeClient(api_key="test_key")
    mock_service = MagicMock()
    mock_request = MagicMock()
    mock_request.execute.return_value = mock_search_response
    mock_service.search().list.return_value = mock_request
    client._service = mock_service

    result = client.search(query="Rick Astley", max_results=5)

    assert result["success"] is True
    assert result["query"] == "Rick Astley"
    assert len(result["results"]) == 1
    assert result["results"][0]["id"] == "dQw4w9WgXcQ"


def test_search_videos_raw(mock_search_response):
    client = YouTubeClient(api_key="test_key")
    mock_service = MagicMock()
    mock_request = MagicMock()
    mock_request.execute.return_value = mock_search_response
    mock_service.search().list.return_value = mock_request
    client._service = mock_service

    result = client.search(query="Rick Astley", raw=True)
    assert result["kind"] == "youtube#searchListResponse"


def test_get_video_details_mocked(mock_videos_response):
    client = YouTubeClient(api_key="test_key")
    mock_service = MagicMock()
    mock_request = MagicMock()
    mock_request.execute.return_value = mock_videos_response
    mock_service.videos().list.return_value = mock_request
    client._service = mock_service

    result = client.get_video_details(video_ids=["dQw4w9WgXcQ"])

    assert result["success"] is True
    assert result["count"] == 1
    assert result["videos"][0]["video_id"] == "dQw4w9WgXcQ"
    assert result["videos"][0]["duration"] == "3:33"


def test_get_channel_details_handle(mock_channels_response):
    client = YouTubeClient(api_key="test_key")
    mock_service = MagicMock()
    mock_request = MagicMock()
    mock_request.execute.return_value = mock_channels_response
    mock_service.channels().list.return_value = mock_request
    client._service = mock_service

    result = client.get_channel_details(for_handle="@rickastley")

    assert result["success"] is True
    assert result["channel"]["custom_url"] == "@rickastley"
    assert result["channel"]["subscriber_count"] == 4000000


def test_get_playlist_items_mocked(mock_playlist_items_response):
    client = YouTubeClient(api_key="test_key")
    mock_service = MagicMock()
    mock_request = MagicMock()
    mock_request.execute.return_value = mock_playlist_items_response
    mock_service.playlistItems().list.return_value = mock_request
    client._service = mock_service

    result = client.get_playlist_items(playlist_id="pli_123")

    assert result["success"] is True
    assert result["playlist_id"] == "pli_123"
    assert len(result["items"]) == 1
    assert result["items"][0]["video_id"] == "vid_abc"


def test_get_video_comments_mocked(mock_comments_response):
    client = YouTubeClient(api_key="test_key")
    mock_service = MagicMock()
    mock_request = MagicMock()
    mock_request.execute.return_value = mock_comments_response
    mock_service.commentThreads().list.return_value = mock_request
    client._service = mock_service

    result = client.get_video_comments(video_id="dQw4w9WgXcQ")

    assert result["success"] is True
    assert len(result["comments"]) == 1
    assert result["comments"][0]["author"] == "Alice"
    assert result["comments"][0]["text"] == "Amazing video!"


def test_quota_exceeded_error_handling():
    client = YouTubeClient(api_key="test_key")
    mock_service = MagicMock()

    error_payload = {
        "error": {
            "errors": [{"reason": "quotaExceeded", "message": "The request cannot be completed because quota exceeded."}],
            "message": "The request cannot be completed because quota exceeded.",
            "code": 403,
        }
    }
    resp = Response({"status": 403})
    http_error = HttpError(resp, json.dumps(error_payload).encode("utf-8"))

    mock_service.search().list.side_effect = http_error
    client._service = mock_service

    result = client.search("query")

    assert result["success"] is False
    assert result["reason"] == "quotaExceeded"
    assert "quota exceeded" in result["error"].lower()
    assert "10,000 unit quota" in result["suggestion"]


def test_scout_niche_channels(mock_channels_response):
    client = YouTubeClient(api_key="test_key")
    mock_service = MagicMock()

    # Search returns 1 channel
    search_mock = MagicMock()
    search_mock.execute.return_value = {
        "items": [
            {"id": {"channelId": "UCuAXFkgsw1L7xaCfnd5JJOw"}}
        ]
    }
    mock_service.search().list.return_value = search_mock

    # Channels batch returns channel info
    channels_mock = MagicMock()
    channels_mock.execute.return_value = mock_channels_response
    mock_service.channels().list.return_value = channels_mock

    client._service = mock_service

    result = client.scout_niche_channels(
        niches=["rick roll pop"],
        min_subscribers=1000,
        max_subscribers=10000000,
        min_videos=10,
        sort_by="subscribers",
    )

    assert result["success"] is True
    assert result["total_niches"] == 1
    assert "rick roll pop" in result["campaigns"]
    campaign = result["campaigns"]["rick roll pop"]
    assert len(campaign["channels"]) == 1
    assert campaign["channels"][0]["channel_id"] == "UCuAXFkgsw1L7xaCfnd5JJOw"
    assert campaign["channels"][0]["subscriber_count"] == 4000000
    assert "avg_views_per_video" in campaign["channels"][0]


def test_get_trending_niches(mock_videos_response):
    client = YouTubeClient(api_key="test_key")
    mock_service = MagicMock()
    mock_request = MagicMock()
    mock_request.execute.return_value = mock_videos_response
    mock_service.videos().list.return_value = mock_request
    client._service = mock_service

    result = client.get_trending_niches(region_code="US", category="tech", max_results=10)

    assert result["success"] is True
    assert result["region_code"] == "US"
    assert result["category"] == "tech"
    assert result["category_id"] == "28"
    assert result["total_trending_videos_analyzed"] == 1
    assert len(result["trending_videos"]) == 1
    assert len(result["top_rising_tags"]) > 0
    assert len(result["top_creators_trending"]) == 1
    assert result["top_creators_trending"][0]["channel_title"] == "Rick Astley"


@patch("youtube_mcp.client.fetch_transcript")
def test_audit_channel_strategy(mock_fetch_transcript, mock_channels_response, mock_playlist_items_response, mock_videos_response):
    client = YouTubeClient(api_key="test_key")
    mock_service = MagicMock()

    # Channels mock
    ch_req = MagicMock()
    ch_req.execute.return_value = mock_channels_response
    mock_service.channels().list.return_value = ch_req

    # Playlist items mock
    pli_req = MagicMock()
    pli_req.execute.return_value = mock_playlist_items_response
    mock_service.playlistItems().list.return_value = pli_req

    # Video details mock
    vid_req = MagicMock()
    vid_req.execute.return_value = mock_videos_response
    mock_service.videos().list.return_value = vid_req

    client._service = mock_service

    # Mock transcript
    mock_fetch_transcript.return_value = {
        "success": True,
        "content": "Never gonna give you up, never gonna let you down.",
    }

    result = client.audit_channel_strategy(channel_id_or_handle="@rickastley", sample_videos=5)

    assert result["success"] is True
    assert result["channel"]["title"] == "Rick Astley"
    assert result["strategy_audit"]["sample_videos_analyzed"] == 1
    assert result["strategy_audit"]["avg_recent_views"] == 1500000000
    assert result["strategy_audit"]["top_performing_video"]["title"] == "Rick Astley - Never Gonna Give You Up (Official Music Video)"
    assert "Never gonna give you up" in result["strategy_audit"]["opening_hook_first_60s"]


def test_find_viral_outliers(mock_channels_response, mock_playlist_items_response, mock_videos_response):
    client = YouTubeClient(api_key="test_key")
    mock_service = MagicMock()

    # Channel mock
    ch_req = MagicMock()
    ch_req.execute.return_value = mock_channels_response
    mock_service.channels().list.return_value = ch_req

    # Playlist items mock
    pli_req = MagicMock()
    pli_req.execute.return_value = mock_playlist_items_response
    mock_service.playlistItems().list.return_value = pli_req

    # Videos mock
    vid_req = MagicMock()
    vid_req.execute.return_value = mock_videos_response
    mock_service.videos().list.return_value = vid_req

    client._service = mock_service

    result = client.find_viral_outliers(query="@rickastley", min_multiplier=1.0)
    assert result["success"] is True
    assert result["total_outliers_found"] >= 1
    assert result["outliers"][0]["video_id"] == "dQw4w9WgXcQ"


def test_analyze_audience_sentiment():
    client = YouTubeClient(api_key="test_key")
    mock_service = MagicMock()

    comments_payload = {
        "items": [
            {
                "id": "c1",
                "snippet": {
                    "totalReplyCount": 0,
                    "topLevelComment": {
                        "snippet": {
                            "authorDisplayName": "Bob",
                            "textDisplay": "Please do a video on React 19!",
                            "likeCount": 15,
                            "publishedAt": "2024-01-01T00:00:00Z",
                        }
                    }
                }
            },
            {
                "id": "c2",
                "snippet": {
                    "totalReplyCount": 0,
                    "topLevelComment": {
                        "snippet": {
                            "authorDisplayName": "Charlie",
                            "textDisplay": "I struggle with understanding async generators, it is confusing.",
                            "likeCount": 8,
                            "publishedAt": "2024-01-01T00:00:00Z",
                        }
                    }
                }
            },
            {
                "id": "c3",
                "snippet": {
                    "totalReplyCount": 0,
                    "topLevelComment": {
                        "snippet": {
                            "authorDisplayName": "Dave",
                            "textDisplay": "How do you deploy this to production?",
                            "likeCount": 20,
                            "publishedAt": "2024-01-01T00:00:00Z",
                        }
                    }
                }
            },
            {
                "id": "c4",
                "snippet": {
                    "totalReplyCount": 0,
                    "topLevelComment": {
                        "snippet": {
                            "authorDisplayName": "Eve",
                            "textDisplay": "This is pure gold, thank you!",
                            "likeCount": 50,
                            "publishedAt": "2024-01-01T00:00:00Z",
                        }
                    }
                }
            },
        ]
    }
    mock_req = MagicMock()
    mock_req.execute.return_value = comments_payload
    mock_service.commentThreads().list.return_value = mock_req
    client._service = mock_service

    result = client.analyze_audience_sentiment(video_id_or_url="dQw4w9WgXcQ")
    assert result["success"] is True
    assert result["comments_analyzed"] == 4
    assert len(result["viewer_content_requests"]) == 1
    assert "React 19" in result["viewer_content_requests"][0]["comment"]
    assert len(result["common_pain_points"]) == 1
    assert "confusing" in result["common_pain_points"][0]["comment"]
    assert len(result["top_audience_questions"]) == 1
    assert len(result["top_upvoted_comments"]) == 4


def test_compare_channels(mock_channels_response, mock_playlist_items_response, mock_videos_response):
    client = YouTubeClient(api_key="test_key")
    mock_service = MagicMock()

    ch_req = MagicMock()
    ch_req.execute.return_value = mock_channels_response
    mock_service.channels().list.return_value = ch_req

    pli_req = MagicMock()
    pli_req.execute.return_value = mock_playlist_items_response
    mock_service.playlistItems().list.return_value = pli_req

    vid_req = MagicMock()
    vid_req.execute.return_value = mock_videos_response
    mock_service.videos().list.return_value = vid_req

    client._service = mock_service

    result = client.compare_channels(channel_handles=["@rickastley"])
    assert result["success"] is True
    assert result["total_channels_compared"] == 1
    assert result["channels"][0]["channel_title"] == "Rick Astley"
    assert result["winner_rankings"]["highest_subscribers"] == "Rick Astley"


def test_blueprint_new_channel():
    client = YouTubeClient(api_key="test_key")

    with patch.object(client, "scout_niche_channels") as mock_scout, \
         patch.object(client, "find_viral_outliers") as mock_outliers, \
         patch.object(client, "analyze_audience_sentiment") as mock_sentiment:

        mock_scout.return_value = {
            "success": True,
            "campaigns": {
                "ai tools": {
                    "channels": [
                        {
                            "title": "AI Creator Lab",
                            "custom_url": "@aicreatorlab",
                            "subscriber_count": 45000,
                            "avg_views_per_video": 18000,
                            "url": "https://youtube.com/@aicreatorlab",
                        }
                    ]
                }
            }
        }

        mock_outliers.return_value = {
            "success": True,
            "outliers": [
                {
                    "video_id": "outlier123",
                    "title": "How to Automate Content with AI",
                    "views": 150000,
                    "multiplier": "4.2x",
                    "url": "https://www.youtube.com/watch?v=outlier123",
                }
            ]
        }

        mock_sentiment.return_value = {
            "success": True,
            "top_audience_questions": [{"comment": "How much does this cost?", "like_count": 45}],
            "viewer_content_requests": [{"comment": "Can you do a video on free tools?", "like_count": 80}],
            "common_pain_points": [{"comment": "Too confusing for beginners", "like_count": 25}],
        }

        blueprint = client.blueprint_new_channel(niche="ai tools", target_audience="beginners")

        assert blueprint["success"] is True
        assert blueprint["niche"] == "ai tools"
        assert blueprint["target_audience"] == "beginners"
        assert blueprint["market_validation"]["demand_status"] == "High"
        assert len(blueprint["competitors_to_model"]) == 1
        assert blueprint["competitors_to_model"][0]["channel_name"] == "AI Creator Lab"
        assert len(blueprint["first_5_videos_to_record"]) == 1
        assert blueprint["first_5_videos_to_record"][0]["inspired_by_outlier"] == "How to Automate Content with AI"
        assert "audience_unmet_needs" in blueprint
        assert "launch_recommendations" in blueprint
        assert len(blueprint["launch_recommendations"]["monetization_roadmap"]) == 3


def test_search_channels():
    client = YouTubeClient(api_key="test_key")

    with patch.object(client, "search") as mock_search, \
         patch.object(client, "get_channels_batch") as mock_batch:

        mock_search.return_value = {
            "success": True,
            "results": [
                {
                    "id": "UC12345",
                    "title": "Tech With Tim",
                    "description": "Python coding tutorials",
                    "url": "https://www.youtube.com/channel/UC12345",
                }
            ],
        }

        mock_batch.return_value = [
            {
                "channel_id": "UC12345",
                "title": "Tech With Tim",
                "custom_url": "@techwithtim",
                "subscriber_count": 1200000,
                "view_count": 150000000,
                "video_count": 850,
            }
        ]

        result = client.search_channels(query="python tutorials", max_results=5)
        assert result["success"] is True
        assert result["count"] == 1
        ch = result["channels"][0]
        assert ch["channel_title"] == "Tech With Tim"
        assert ch["handle"] == "@techwithtim"
        assert ch["subscribers"] == 1200000
        assert ch["video_count"] == 850


def test_reverse_engineer_channel():
    client = YouTubeClient(api_key="test_key")

    with patch.object(client, "audit_channel_strategy") as mock_audit, \
         patch.object(client, "analyze_audience_sentiment") as mock_sentiment:

        mock_audit.return_value = {
            "success": True,
            "channel": {
                "title": "Ali Abdaal",
                "handle": "@aliabdaal",
                "subscribers": 5000000,
                "total_views": 400000000,
                "video_count": 700,
            },
            "strategy_audit": {
                "sample_videos_analyzed": 5,
                "avg_recent_views": 1500000,
                "estimated_cadence": "Weekly",
                "avg_days_between_uploads": 7.0,
                "title_formulas_detected": ["Numbers & Listicles (e.g. '7 Tips', 'Top 5')"],
                "primary_tags": ["productivity", "study"],
                "top_performing_video": {
                    "title": "How I Study",
                    "views": 3000000,
                    "duration": "12:30",
                    "url": "https://www.youtube.com/watch?v=study123",
                },
                "lowest_performing_video": {
                    "title": "My Vlog",
                    "views": 400000,
                    "duration": "8:00",
                    "url": "https://www.youtube.com/watch?v=vlog123",
                },
                "opening_hook_first_60s": "In this video, I will show you the active recall method.",
                "monetization_funnel": {
                    "affiliate_links": ["https://amzn.to/example"],
                    "newsletters": ["https://newsletter.example.com"],
                    "courses_communities": ["https://skool.com/community"],
                    "sponsor_disclosures": ["Sponsored by Notion"],
                },
            },
            "recent_videos": [],
        }

        mock_sentiment.return_value = {
            "success": True,
            "top_audience_questions": [{"comment": "Can you share the flashcard app?", "like_count": 150}],
            "viewer_content_requests": [{"comment": "Do a version for medical students!", "like_count": 220}],
            "common_pain_points": [{"comment": "Anki is too hard to set up on Mac", "like_count": 85}],
        }

        res = client.reverse_engineer_channel(channel_id_or_handle="@aliabdaal", sample_videos=5)
        assert res["success"] is True
        assert res["channel"]["title"] == "Ali Abdaal"
        assert res["growth_and_cadence"]["avg_recent_views"] == 1500000
        assert res["growth_and_cadence"]["view_to_sub_ratio"] == "30.0%"
        assert "content_strategy_breakdown" in res
        assert res["content_strategy_breakdown"]["first_60s_hook_script"] == "In this video, I will show you the active recall method."
        assert len(res["audience_unmet_needs_and_flaws"]["unanswered_viewer_questions"]) == 1
        assert "beginner_replication_playbook" in res
        assert len(res["beginner_replication_playbook"]["actionable_takeaways"]) == 3


def test_find_breakout_growth_channels():
    client = YouTubeClient(api_key="test_key")

    with patch.object(client, "search") as mock_search, \
         patch.object(client, "get_channels_batch") as mock_batch:

        mock_search.return_value = {
            "success": True,
            "results": [{"id": "UC_breakout"}],
        }

        mock_batch.return_value = [
            {
                "channel_id": "UC_breakout",
                "title": "Modern AI Creator",
                "custom_url": "@modernaicreator",
                "subscriber_count": 45000,
                "video_count": 15,
                "view_count": 900000,
                "published_at": "2025-01-01T00:00:00Z",
                "url": "https://youtube.com/@modernaicreator",
            }
        ]

        res = client.find_breakout_growth_channels(niche="ai creator", max_channel_age_months=24)
        assert res["success"] is True
        assert res["total_found"] == 1
        ch = res["breakout_channels"][0]
        assert ch["channel_name"] == "Modern AI Creator"
        assert ch["subscribers"] == 45000
        assert ch["subs_per_video"] == 3000


def test_find_content_gaps():
    client = YouTubeClient(api_key="test_key")

    with patch.object(client, "search") as mock_search, \
         patch.object(client, "get_video_details") as mock_details:

        mock_search.return_value = {
            "success": True,
            "results": [{"id": "vid_old"}, {"id": "vid_new"}],
        }

        mock_details.return_value = {
            "success": True,
            "videos": [
                {
                    "video_id": "vid_old",
                    "title": "SQL Tutorial for Beginners 2021",
                    "channel_title": "Old Channel",
                    "view_count": 500000,
                    "published_at": "2021-01-01T00:00:00Z",
                    "duration": "20:00",
                    "url": "https://youtube.com/watch?v=vid_old",
                },
                {
                    "video_id": "vid_new",
                    "title": "SQL in 2026",
                    "channel_title": "New Channel",
                    "view_count": 10000,
                    "published_at": "2026-08-01T00:00:00Z",
                    "duration": "10:00",
                    "url": "https://youtube.com/watch?v=vid_new",
                }
            ],
        }

        res = client.find_content_gaps(niche_or_topic="sql tutorial")
        assert res["success"] is True
        assert "HIGH" in res["content_gap_opportunity"]
        assert res["outdated_ranking_videos_found"] == 1
        assert len(res["suggested_video_titles_to_rank"]) == 3


def test_generate_retention_script_outline():
    client = YouTubeClient(api_key="test_key")

    with patch("youtube_mcp.client.fetch_transcript") as mock_transcript, \
         patch.object(client, "analyze_audience_sentiment") as mock_sentiment:

        mock_transcript.return_value = {
            "success": True,
            "content": "Stop wasting time learning Python the wrong way.",
        }

        mock_sentiment.return_value = {
            "success": True,
            "top_audience_questions": [{"comment": "How do I install libraries on Windows?"}],
            "common_pain_points": [{"comment": "Virtual environments are so confusing"}],
        }

        res = client.generate_retention_script_outline(
            video_title_or_topic="How to Learn Python in 2026",
            competitor_video_id_or_url="https://youtube.com/watch?v=abc12345678",
            target_duration_minutes=10,
        )

        assert res["success"] is True
        assert res["video_title"] == "How to Learn Python in 2026"
        assert res["modeled_competitor_hook"] == "Stop wasting time learning Python the wrong way."
        assert len(res["retention_script_outline"]) == 7
        assert res["retention_script_outline"][0]["section"] == "The Hook (Pattern Interrupt & Promise)"


def test_discover_niche_sponsors():
    client = YouTubeClient(api_key="test_key")

    with patch.object(client, "search") as mock_search, \
         patch.object(client, "get_video_details") as mock_details:

        mock_search.return_value = {
            "success": True,
            "results": [{"id": "vid_sponsored"}],
        }

        mock_details.return_value = {
            "success": True,
            "videos": [
                {
                    "video_id": "vid_sponsored",
                    "title": "My Favorite Tech Setup",
                    "channel_title": "Tech Reviewer",
                    "view_count": 80000,
                    "description": "This video is sponsored by Notion! Use code TECH for 20% off.\nCheck out my gear: https://amzn.to/example",
                    "url": "https://youtube.com/watch?v=vid_sponsored",
                }
            ],
        }

        res = client.discover_niche_sponsors(niche_or_query="tech setup")
        assert res["success"] is True
        assert res["videos_analyzed"] == 1
        assert res["sponsored_videos_detected"] == 1
        assert any(b["brand"] == "Notion" for b in res["top_active_sponsors"])
        assert len(res["creator_monetization_guidance"]) == 3



