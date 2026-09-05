"""Pytest fixtures and mock response factories for YouTube MCP tests."""

import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_search_response():
    return {
        "kind": "youtube#searchListResponse",
        "etag": "etag_123",
        "nextPageToken": "CAUQAA",
        "pageInfo": {"totalResults": 100, "resultsPerPage": 1},
        "items": [
            {
                "kind": "youtube#searchResult",
                "etag": "etag_item_1",
                "id": {"kind": "youtube#video", "videoId": "dQw4w9WgXcQ"},
                "snippet": {
                    "publishedAt": "2009-10-25T06:57:33Z",
                    "channelId": "UCuAXFkgsw1L7xaCfnd5JJOw",
                    "title": "Rick Astley - Never Gonna Give You Up (Official Music Video)",
                    "description": "The official video for “Never Gonna Give You Up” by Rick Astley.",
                    "channelTitle": "Rick Astley",
                },
            }
        ],
    }


@pytest.fixture
def mock_videos_response():
    return {
        "kind": "youtube#videoListResponse",
        "etag": "etag_vid_123",
        "items": [
            {
                "kind": "youtube#video",
                "etag": "item_etag",
                "id": "dQw4w9WgXcQ",
                "snippet": {
                    "publishedAt": "2009-10-25T06:57:33Z",
                    "channelId": "UCuAXFkgsw1L7xaCfnd5JJOw",
                    "title": "Rick Astley - Never Gonna Give You Up (Official Music Video)",
                    "description": "The official video for “Never Gonna Give You Up”.",
                    "channelTitle": "Rick Astley",
                    "tags": ["rick astley", "never gonna give you up", "pop"],
                },
                "contentDetails": {
                    "duration": "PT3M33S",
                    "dimension": "2d",
                    "definition": "hd",
                },
                "statistics": {
                    "viewCount": "1500000000",
                    "likeCount": "17000000",
                    "commentCount": "2500000",
                },
            }
        ],
    }


@pytest.fixture
def mock_channels_response():
    return {
        "kind": "youtube#channelListResponse",
        "items": [
            {
                "kind": "youtube#channel",
                "id": "UCuAXFkgsw1L7xaCfnd5JJOw",
                "snippet": {
                    "title": "Rick Astley",
                    "description": "Welcome to the official Rick Astley YouTube channel.",
                    "customUrl": "@rickastley",
                    "publishedAt": "2006-11-28T14:32:00Z",
                },
                "contentDetails": {
                    "relatedPlaylists": {
                        "uploads": "UUuAXFkgsw1L7xaCfnd5JJOw",
                    }
                },
                "statistics": {
                    "viewCount": "2000000000",
                    "subscriberCount": "4000000",
                    "videoCount": "120",
                },
            }
        ],
    }


@pytest.fixture
def mock_playlist_items_response():
    return {
        "kind": "youtube#playlistItemListResponse",
        "nextPageToken": "CDIQAA",
        "pageInfo": {"totalResults": 50, "resultsPerPage": 1},
        "items": [
            {
                "kind": "youtube#playlistItem",
                "id": "pli_123",
                "snippet": {
                    "publishedAt": "2023-01-01T00:00:00Z",
                    "channelId": "UC123",
                    "title": "First Video in Playlist",
                    "channelTitle": "Tech Channel",
                    "position": 0,
                    "resourceId": {"kind": "youtube#video", "videoId": "vid_abc"},
                },
            }
        ],
    }


@pytest.fixture
def mock_comments_response():
    return {
        "kind": "youtube#commentThreadListResponse",
        "pageInfo": {"totalResults": 10},
        "nextPageToken": "comment_token_next",
        "items": [
            {
                "kind": "youtube#commentThread",
                "id": "comment_123",
                "snippet": {
                    "totalReplyCount": 5,
                    "topLevelComment": {
                        "id": "comment_123",
                        "snippet": {
                            "authorDisplayName": "Alice",
                            "authorChannelUrl": "http://www.youtube.com/channel/UCAlice",
                            "textDisplay": "Amazing video!",
                            "likeCount": 42,
                            "publishedAt": "2024-01-15T10:00:00Z",
                        },
                    },
                },
            }
        ],
    }


@pytest.fixture
def sample_raw_transcript():
    return [
        {"text": "We're no strangers to love", "start": 18.5, "duration": 4.2},
        {"text": "You know the rules and so do I", "start": 22.8, "duration": 3.9},
        {"text": "A full commitment's what I'm thinking of", "start": 27.1, "duration": 4.5},
    ]
