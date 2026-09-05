---
name: youtube-content-repurposing
description: >-
  Transcribe long-form YouTube videos, automatically generate timestamped chapters,
  extract punchy 30-to-60-second viral Shorts clips, and create Community Tab interactive polls.
---

# YouTube Content Repurposing Skill

Use this workflow to maximize the algorithmic ROI of existing long-form videos by automatically generating chapters, viral 30-to-60-second Shorts clips, and Community Tab engagement posts.

## Procedure

### 1. Extract and Analyze Video Transcript
Call `get_video_transcript`:
- Pass `video_id_or_url` with `format="timestamped"`.
- Obtain the full spoken dialogue with millisecond timestamps.

### 2. Auto-Generate Chapters and Viral Shorts Clips
Call `extract_shorts_clips`:
- Pass `video_id_or_url` or raw transcript.
- The tool automatically identifies:
  - **Timestamped Chapters**: 4 to 8 logical chapter markers with SEO-friendly titles formatted for YouTube video descriptions.
  - **Viral Shorts Clip Segments**: 2 to 4 high-energy 30-to-60-second clips featuring punchy hooks, clear takeaways, and strong CTA conclusions.

### 3. Package Shorts Clips for Social Distribution
For each extracted Short:
- Generate a vertical hook headline (first 3 seconds on screen).
- Ensure the clip ends with a cliffhanger or direct call-to-action pointing viewers to the full long-form video (Related Video link).

### 4. Create Community Tab Discussion & Polls
Call `analyze_community_posts`:
- Pass the video topic and `target_goal="video_validation"`.
- Deploy the "Pain-Point Knowledge Quiz" or "Instant-Identity Poll" directly quoting the most debated topic from the video transcript to reignite engagement in subscriber and non-subscriber feeds.
