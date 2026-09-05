"""Unit tests for formatters.py."""

from youtube_mcp.formatters import (
    parse_iso8601_duration,
    format_search_results,
    format_video_details,
    format_channel_details,
    format_playlist_item,
    format_comment_thread,
)


def test_parse_iso8601_duration():
    assert parse_iso8601_duration("PT3M33S") == "3:33"
    assert parse_iso8601_duration("PT1H23M45S") == "1:23:45"
    assert parse_iso8601_duration("PT45S") == "0:45"
    assert parse_iso8601_duration("PT2H5S") == "2:00:05"
    assert parse_iso8601_duration(None) == "N/A"
    assert parse_iso8601_duration("invalid") == "invalid"


def test_format_search_results(mock_search_response):
    formatted = format_search_results("Rick Astley", mock_search_response)
    assert formatted["query"] == "Rick Astley"
    assert formatted["total_results"] == 100
    assert formatted["next_page_token"] == "CAUQAA"
    assert len(formatted["results"]) == 1

    item = formatted["results"][0]
    assert item["id"] == "dQw4w9WgXcQ"
    assert item["kind"] == "video"
    assert item["title"] == "Rick Astley - Never Gonna Give You Up (Official Music Video)"
    assert item["channel_title"] == "Rick Astley"
    assert item["url"] == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def test_format_video_details(mock_videos_response):
    item = mock_videos_response["items"][0]
    details = format_video_details(item)

    assert details["video_id"] == "dQw4w9WgXcQ"
    assert details["title"] == "Rick Astley - Never Gonna Give You Up (Official Music Video)"
    assert details["channel_title"] == "Rick Astley"
    assert details["duration"] == "3:33"
    assert details["view_count"] == 1500000000
    assert details["like_count"] == 17000000
    assert details["comment_count"] == 2500000
    assert "rick astley" in details["tags"]
    assert details["url"] == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def test_format_channel_details(mock_channels_response):
    item = mock_channels_response["items"][0]
    channel = format_channel_details(item)

    assert channel["channel_id"] == "UCuAXFkgsw1L7xaCfnd5JJOw"
    assert channel["title"] == "Rick Astley"
    assert channel["custom_url"] == "@rickastley"
    assert channel["subscriber_count"] == 4000000
    assert channel["uploads_playlist_id"] == "UUuAXFkgsw1L7xaCfnd5JJOw"
    assert channel["url"] == "https://www.youtube.com/@rickastley"


def test_format_playlist_item(mock_playlist_items_response):
    item = mock_playlist_items_response["items"][0]
    pli = format_playlist_item(item)

    assert pli["video_id"] == "vid_abc"
    assert pli["title"] == "First Video in Playlist"
    assert pli["channel_title"] == "Tech Channel"
    assert pli["position"] == 0
    assert pli["url"] == "https://www.youtube.com/watch?v=vid_abc"


def test_format_comment_thread(mock_comments_response):
    item = mock_comments_response["items"][0]
    cmt = format_comment_thread(item)

    assert cmt["comment_id"] == "comment_123"
    assert cmt["author"] == "Alice"
    assert cmt["text"] == "Amazing video!"
    assert cmt["like_count"] == 42
    assert cmt["reply_count"] == 5
