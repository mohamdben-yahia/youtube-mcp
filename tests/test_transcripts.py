"""Unit tests for transcripts.py."""

from unittest.mock import patch, MagicMock
from youtube_transcript_api import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    CouldNotRetrieveTranscript,
)
from youtube_mcp.transcripts import (
    extract_video_id,
    format_seconds,
    fetch_transcript,
)


def test_extract_video_id():
    assert extract_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://www.youtube.com/shorts/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://www.youtube.com/watch?feature=share&v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"


def test_format_seconds():
    assert format_seconds(0) == "00:00"
    assert format_seconds(65) == "01:05"
    assert format_seconds(3665) == "01:01:05"


@patch("youtube_mcp.transcripts._get_raw_transcript_data")
def test_fetch_transcript_text_format(mock_get_raw, sample_raw_transcript):
    mock_get_raw.return_value = (sample_raw_transcript, "en", False)

    result = fetch_transcript("dQw4w9WgXcQ", output_format="text")

    assert result["success"] is True
    assert result["video_id"] == "dQw4w9WgXcQ"
    assert result["language"] == "en"
    assert result["is_generated"] is False
    assert result["format"] == "text"
    assert result["segment_count"] == 3
    assert "We're no strangers to love You know the rules and so do I" in result["content"]


@patch("youtube_mcp.transcripts._get_raw_transcript_data")
def test_fetch_transcript_timestamped_format(mock_get_raw, sample_raw_transcript):
    mock_get_raw.return_value = (sample_raw_transcript, "en", True)

    result = fetch_transcript("dQw4w9WgXcQ", output_format="timestamped")

    assert result["success"] is True
    assert result["is_generated"] is True
    assert "[00:18] We're no strangers to love" in result["content"]
    assert "[00:22] You know the rules and so do I" in result["content"]


@patch("youtube_mcp.transcripts._get_raw_transcript_data")
def test_fetch_transcript_json_format(mock_get_raw, sample_raw_transcript):
    mock_get_raw.return_value = (sample_raw_transcript, "en", False)

    result = fetch_transcript("dQw4w9WgXcQ", output_format="json")

    assert result["success"] is True
    assert isinstance(result["content"], list)
    assert len(result["content"]) == 3
    assert result["content"][0]["start"] == 18.5
    assert result["content"][0]["text"] == "We're no strangers to love"


@patch("youtube_mcp.transcripts._get_raw_transcript_data")
def test_fetch_transcript_time_filter(mock_get_raw, sample_raw_transcript):
    mock_get_raw.return_value = (sample_raw_transcript, "en", False)

    # Filter between 20s and 25s (should only include the second segment at 22.8s)
    result = fetch_transcript("dQw4w9WgXcQ", start_seconds=20.0, end_seconds=25.0)

    assert result["success"] is True
    assert result["segment_count"] == 1
    assert result["content"] == "You know the rules and so do I"


@patch("youtube_mcp.transcripts._get_raw_transcript_data")
def test_fetch_transcript_disabled(mock_get_raw):
    mock_get_raw.side_effect = TranscriptsDisabled("video_id")

    result = fetch_transcript("dQw4w9WgXcQ")
    assert result["success"] is False
    assert "Transcripts are disabled" in result["error"]


@patch("youtube_mcp.transcripts._get_raw_transcript_data")
def test_fetch_transcript_unavailable(mock_get_raw):
    mock_get_raw.side_effect = VideoUnavailable("video_id")

    result = fetch_transcript("dQw4w9WgXcQ")
    assert result["success"] is False
    assert "Video is unavailable" in result["error"]


@patch("youtube_mcp.transcripts._get_raw_transcript_data")
def test_fetch_transcript_not_found(mock_get_raw):
    mock_get_raw.side_effect = NoTranscriptFound("video_id", ["es"], {})

    result = fetch_transcript("dQw4w9WgXcQ", languages=["es"])
    assert result["success"] is False
    assert "No transcript found" in result["error"]


@patch("youtube_mcp.transcripts._get_raw_transcript_data")
def test_fetch_transcript_could_not_retrieve(mock_get_raw):
    mock_get_raw.side_effect = CouldNotRetrieveTranscript("video_id")

    result = fetch_transcript("dQw4w9WgXcQ")
    assert result["success"] is False
    assert "Could not retrieve transcript" in result["error"]


@patch("youtube_mcp.transcripts._get_raw_transcript_data")
def test_generate_video_chapters_and_clips(mock_get_raw):
    sample_segments = [
        {"text": "Welcome to the video, here is the secret to success.", "start": 0.0, "duration": 15.0},
        {"text": "The number one mistake beginners make is giving up early.", "start": 15.0, "duration": 15.0},
        {"text": "In this chapter we look at the main hack for growth.", "start": 70.0, "duration": 15.0},
        {"text": "Finally remember to subscribe and like for more tips.", "start": 130.0, "duration": 20.0},
    ]
    mock_get_raw.return_value = (sample_segments, "en", False)

    from youtube_mcp.transcripts import generate_video_chapters_and_clips
    res = generate_video_chapters_and_clips("dQw4w9WgXcQ", min_duration_seconds=20, max_duration_seconds=60)

    assert res["success"] is True
    assert res["video_id"] == "dQw4w9WgXcQ"
    assert len(res["youtube_chapters"]) >= 1
    assert res["youtube_chapters"][0]["timestamp"] == "00:00"
    assert "formatted_chapters_text" in res
    assert len(res["recommended_shorts_clips"]) >= 1
    assert "hook_sentence" in res["recommended_shorts_clips"][0]
    assert "start_time" in res["recommended_shorts_clips"][0]
