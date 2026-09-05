"""Transcript retrieval and formatting using youtube-transcript-api."""

import re
from typing import Any, Dict, List, Optional
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    CouldNotRetrieveTranscript,
)


def extract_video_id(video_id_or_url: str) -> str:
    """Extract an 11-character YouTube video ID from a URL or raw ID string."""
    cleaned = video_id_or_url.strip()
    
    # Check if it's already an 11-char video ID
    if re.fullmatch(r"[a-zA-Z0-9_-]{11}", cleaned):
        return cleaned

    # Match standard patterns:
    # https://www.youtube.com/watch?v=VIDEO_ID
    # https://youtu.be/VIDEO_ID
    # https://www.youtube.com/embed/VIDEO_ID
    # https://www.youtube.com/shorts/VIDEO_ID
    patterns = [
        r"(?:v=|\/v\/|youtu\.be\/|\/embed\/|\/shorts\/)([a-zA-Z0-9_-]{11})",
        r"(?:[?&]v=)([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, cleaned)
        if match:
            return match.group(1)
            
    # Return as-is if no pattern matched
    return cleaned


def format_seconds(seconds: float) -> str:
    """Format seconds into HH:MM:SS or MM:SS."""
    total_sec = int(seconds)
    hours = total_sec // 3600
    minutes = (total_sec % 3600) // 60
    sec = total_sec % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{sec:02d}"
    return f"{minutes:02d}:{sec:02d}"


def _get_raw_transcript_data(video_id: str, languages: List[str]):
    """Fetch raw transcript segments and metadata supporting both 0.x and 1.x API."""
    # Check if modern instantiated API is available (1.x)
    if hasattr(YouTubeTranscriptApi, "list") and hasattr(YouTubeTranscriptApi, "fetch"):
        try:
            api = YouTubeTranscriptApi()
            transcript_list = api.list(video_id)
            transcript = None
            is_generated = False
            selected_lang = languages[0]

            # Try manually created first
            try:
                transcript = transcript_list.find_manually_created_transcript(languages)
                selected_lang = transcript.language_code
                is_generated = False
            except Exception:
                try:
                    transcript = transcript_list.find_generated_transcript(languages)
                    selected_lang = transcript.language_code
                    is_generated = True
                except Exception:
                    try:
                        transcript = transcript_list.find_transcript(languages)
                        selected_lang = transcript.language_code
                        is_generated = getattr(transcript, "is_generated", False)
                    except Exception:
                        pass

            if transcript is not None:
                fetched = transcript.fetch()
                raw_data = fetched.to_raw_data() if hasattr(fetched, "to_raw_data") else fetched
                return raw_data, selected_lang, is_generated

            # Direct fetch fallback
            fetched = api.fetch(video_id, languages=languages)
            raw_data = fetched.to_raw_data() if hasattr(fetched, "to_raw_data") else fetched
            return raw_data, getattr(fetched, "language_code", languages[0]), getattr(fetched, "is_generated", False)
        except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable, CouldNotRetrieveTranscript):
            raise
        except Exception:
            # Fall back to legacy method if present
            pass

    # Legacy static method fallback (0.x)
    if hasattr(YouTubeTranscriptApi, "list_transcripts"):
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = None
        selected_lang = languages[0]
        is_generated = False

        try:
            transcript = transcript_list.find_manually_created_transcript(languages)
            selected_lang = transcript.language_code
            is_generated = False
        except Exception:
            try:
                transcript = transcript_list.find_generated_transcript(languages)
                selected_lang = transcript.language_code
                is_generated = True
            except Exception:
                for t in transcript_list:
                    transcript = t
                    selected_lang = t.language_code
                    is_generated = t.is_generated
                    break

        if transcript is not None:
            return transcript.fetch(), selected_lang, is_generated

        return YouTubeTranscriptApi.get_transcript(video_id, languages=languages), languages[0], False

    raise RuntimeError("Unsupported version of youtube-transcript-api installed.")


def fetch_transcript(
    video_id_or_url: str,
    languages: Optional[List[str]] = None,
    output_format: str = "text",
    start_seconds: Optional[float] = None,
    end_seconds: Optional[float] = None,
) -> Dict[str, Any]:
    """Retrieve video transcript with language fallback, time filtering, and format options.
    
    Args:
        video_id_or_url: YouTube video ID or full URL.
        languages: List of language codes in order of preference (e.g. ['en', 'es']).
                   Defaults to ['en'].
        output_format: 'text', 'timestamped', or 'json'.
        start_seconds: Optional start timestamp to filter transcript.
        end_seconds: Optional end timestamp to filter transcript.
    """
    video_id = extract_video_id(video_id_or_url)
    langs = languages or ["en"]

    try:
        raw_snippets, selected_lang, is_generated = _get_raw_transcript_data(video_id, langs)

        # Apply time window filters if provided
        filtered_snippets = []
        for s in raw_snippets:
            start = s.get("start", 0.0)
            if start_seconds is not None and start < start_seconds:
                continue
            if end_seconds is not None and start > end_seconds:
                break
            filtered_snippets.append(s)

        # Format output
        content: Any
        if output_format == "json":
            content = [
                {
                    "text": s.get("text", "").strip(),
                    "start": round(s.get("start", 0.0), 2),
                    "duration": round(s.get("duration", 0.0), 2),
                }
                for s in filtered_snippets
            ]
        elif output_format == "timestamped":
            lines = [
                f"[{format_seconds(s.get('start', 0.0))}] {s.get('text', '').strip()}"
                for s in filtered_snippets
            ]
            content = "\n".join(lines)
        else:  # "text"
            text_parts = [s.get("text", "").strip() for s in filtered_snippets if s.get("text")]
            content = " ".join(text_parts)

        return {
            "success": True,
            "video_id": video_id,
            "language": selected_lang,
            "is_generated": is_generated,
            "format": output_format,
            "segment_count": len(filtered_snippets),
            "content": content,
        }

    except TranscriptsDisabled:
        return {
            "success": False,
            "video_id": video_id,
            "error": "Transcripts are disabled for this video.",
            "suggestion": "The creator or YouTube has disabled closed captions for this video.",
        }
    except NoTranscriptFound:
        return {
            "success": False,
            "video_id": video_id,
            "error": f"No transcript found matching languages {langs}.",
            "suggestion": "Try fetching without specifying languages or verify if captions are available on YouTube.",
        }
    except VideoUnavailable:
        return {
            "success": False,
            "video_id": video_id,
            "error": "Video is unavailable, private, or has been deleted.",
            "suggestion": "Verify that the video ID or URL is correct and publicly accessible.",
        }
    except CouldNotRetrieveTranscript as e:
        return {
            "success": False,
            "video_id": video_id,
            "error": f"Could not retrieve transcript: {str(e)}",
            "suggestion": "Check if captions are available or if network connectivity is unrestricted.",
        }
    except Exception as e:
        return {
            "success": False,
            "video_id": video_id,
            "error": f"Failed to fetch transcript: {str(e)}",
        }


def generate_video_chapters_and_clips(
    video_id_or_url: str,
    min_duration_seconds: int = 20,
    max_duration_seconds: int = 60,
    max_clips: int = 5,
) -> Dict[str, Any]:
    """Generate automatic YouTube chapters and detect high-impact Shorts/Reels clips from transcripts.

    Args:
        video_id_or_url: Video ID or URL.
        min_duration_seconds: Minimum clip duration for Shorts (default 20).
        max_duration_seconds: Maximum clip duration for Shorts (default 60).
        max_clips: Maximum number of recommended Shorts clips to return (default 5).
    """
    raw_res = fetch_transcript(video_id_or_url, output_format="json")
    if not raw_res.get("success"):
        return raw_res

    segments = raw_res.get("content", [])
    if not segments:
        return {
            "success": False,
            "video_id": raw_res.get("video_id"),
            "error": "Transcript contains no segments.",
        }

    total_duration = segments[-1]["start"] + segments[-1]["duration"]

    # 1. Generate YouTube Chapters
    chapters = []
    # Always include 00:00
    chapters.append({
        "timestamp": "00:00",
        "seconds": 0,
        "title": "Introduction & Hook",
    })

    # Decide interval: for short videos (<5 min), every 60s; for medium (5-20 min), every 2-3 min; long, every 4-5 min
    if total_duration < 300:
        interval = 60
    elif total_duration < 1200:
        interval = 180
    else:
        interval = 300

    next_target = interval
    for s in segments:
        if s["start"] >= next_target and s["start"] < (total_duration - 45):
            words = s["text"].split()
            preview = " ".join(words[:5]).capitalize()
            # Clean up punctuation
            preview = re.sub(r"[^\w\s]", "", preview).strip()
            if not preview:
                preview = f"Chapter at {format_seconds(s['start'])}"
            chapters.append({
                "timestamp": format_seconds(s["start"]),
                "seconds": round(s["start"]),
                "title": preview,
            })
            next_target = s["start"] + interval

    formatted_chapter_text = "\n".join(f"{c['timestamp']} - {c['title']}" for c in chapters)

    # 2. Extract High-Impact Viral Shorts/Reels Clips (30-60s)
    HOOK_KEYWORDS = {
        "secret", "mistake", "never", "always", "number one", "first",
        "most important", "here's why", "truth is", "rule", "step",
        "hack", "advice", "stop", "key", "remember", "problem",
        "solution", "money", "million", "success", "fail", "don't", "worst"
    }

    candidate_clips = []
    n_segs = len(segments)

    for i in range(n_segs):
        start_time = segments[i]["start"]
        clip_texts = []
        clip_score = 0

        for j in range(i, n_segs):
            seg = segments[j]
            curr_duration = (seg["start"] + seg["duration"]) - start_time
            clip_texts.append(seg["text"])

            # Check if within valid shorts duration range
            if min_duration_seconds <= curr_duration <= max_duration_seconds:
                full_text = " ".join(clip_texts)
                text_lower = full_text.lower()

                # Score based on hook keywords
                for kw in HOOK_KEYWORDS:
                    if kw in text_lower:
                        clip_score += 2

                # Give bonus to clips that start with questions or bold statements
                if any(clip_texts[0].lower().startswith(q) for q in ["how", "why", "what", "if you", "the biggest"]):
                    clip_score += 3

                # First sentence as hook
                sentences = re.split(r"[.!?]+", full_text)
                first_sentence = sentences[0].strip() if sentences else full_text[:80]

                candidate_clips.append({
                    "score": clip_score,
                    "start_time": format_seconds(start_time),
                    "end_time": format_seconds(seg["start"] + seg["duration"]),
                    "start_seconds": round(start_time, 2),
                    "end_seconds": round(seg["start"] + seg["duration"], 2),
                    "duration_seconds": round(curr_duration),
                    "hook_sentence": first_sentence,
                    "full_transcript_excerpt": full_text,
                })

            elif curr_duration > max_duration_seconds:
                break

    # Pick top non-overlapping clips
    candidate_clips.sort(key=lambda x: x["score"], reverse=True)
    selected_clips = []

    for cand in candidate_clips:
        # Check overlap
        overlaps = False
        for sel in selected_clips:
            if not (cand["end_seconds"] <= sel["start_seconds"] or cand["start_seconds"] >= sel["end_seconds"]):
                overlaps = True
                break
        if not overlaps:
            cand_copy = dict(cand)
            del cand_copy["score"]
            cand_copy["clip_number"] = len(selected_clips) + 1
            selected_clips.append(cand_copy)
            if len(selected_clips) >= max_clips:
                break

    # Fallback if no specific hook keyword scored clips
    if not selected_clips and segments:
        # Take first 45 seconds as clip 1
        clip_texts = []
        for s in segments:
            clip_texts.append(s["text"])
            if s["start"] + s["duration"] >= min_duration_seconds:
                selected_clips.append({
                    "clip_number": 1,
                    "start_time": format_seconds(segments[0]["start"]),
                    "end_time": format_seconds(s["start"] + s["duration"]),
                    "start_seconds": round(segments[0]["start"], 2),
                    "end_seconds": round(s["start"] + s["duration"], 2),
                    "duration_seconds": round(s["start"] + s["duration"] - segments[0]["start"]),
                    "hook_sentence": clip_texts[0],
                    "full_transcript_excerpt": " ".join(clip_texts),
                })
                break

    return {
        "success": True,
        "video_id": raw_res.get("video_id"),
        "total_video_duration": format_seconds(total_duration),
        "total_duration_seconds": round(total_duration),
        "youtube_chapters": chapters,
        "formatted_chapters_text": formatted_chapter_text,
        "recommended_shorts_clips": selected_clips,
    }
