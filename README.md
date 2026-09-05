# YouTube MCP Server: Market Research & Channel Launch Engine for New Creators

A production-ready **Model Context Protocol (MCP)** server providing AI assistants (Claude Desktop, Cursor, Antigravity, and custom LLM agents) high-signal, token-efficient access to YouTube data.

**Specifically architected for aspiring creators and new YouTubers** to conduct deep, data-driven market research before recording a single video: validate niche viability, find realistic model channels (1k–300k subscribers), uncover viral outlier video ideas, mine audience pain points directly from comments, and generate a validated 5-video launch blueprint.

Built with **MCPServer / FastMCP** (`mcp>=1.2.0`), **Google API Client** (`google-api-python-client`), and **`youtube-transcript-api`**.

---

## 🎯 Built for New Creators: The 5-Step Market Research Workflow

Starting a YouTube channel without research leads to months of making videos nobody watches. This server equips AI agents with the tools to run **full, real market research**:

```
 ┌────────────────────────┐       ┌────────────────────────┐       ┌────────────────────────┐
 │ 1. Validate Niche      │       │ 2. Scout Model Channels│       │ 3. Find Outlier Topics │
 │ `blueprint_new_channel`│ ────> │ `scout_niche_channels` │ ────> │ `find_viral_outliers`  │
 │ `get_trending_niches`  │       │ (1k - 300k subs)       │       │ (2.5x - 10x+ views)    │
 └────────────────────────┘       └────────────────────────┘       └────────────────────────┘
                                                                               │
                                                                               ▼
 ┌────────────────────────┐       ┌────────────────────────┐       ┌────────────────────────┐
 │ 5. Plan Launch & Hooks │       │ 5-Video Launch Roadmap │       │ 4. Mine Audience Pains │
 │ `audit_channel_strategy│ <──── │ Structured titles,     │ <──── │ `analyze_audience_     │
 │ `extract_shorts_clips` │       │ angles, and 60s hooks  │       │  sentiment`            │
 └────────────────────────┘       └────────────────────────┘       └────────────────────────┘
```

1. **Validate Demand**: Run `blueprint_new_channel` to instantly inspect competitor volume, subscriber health, and audience appetite in any niche.
2. **Find Channels to Model**: Scout accessible competitors (1k to 300k subs) who are actively growing today using `scout_niche_channels`, instead of trying to copy 10M+ sub creators with massive teams.
3. **Discover Outlier Topics**: Use `find_viral_outliers` to identify videos that got 5x–20x a channel's normal views. These prove that **the topic itself has viral search/browse demand**, even with 0 subscribers.
4. **Mine Real Viewer Pain Points**: Run `analyze_audience_sentiment` on competitor videos to extract genuine viewer frustrations, unanswered questions, and requests for future videos.
5. **Reverse-Engineer the Script & Hook**: Use `audit_channel_strategy` and `get_video_transcript` to see exactly how top creators hook viewers in the first 60 seconds and structure retention.

---

## Features & Tool Suite

### 🔍 Search & Discovery Engine
- **🔎 Channel Search (`search_channels`)**: Search YouTube specifically for channels matching any niche or query, instantly enriched with live subscriber counts, total view counts, video counts, handles, and URLs in one token-efficient call.
- **📹 Video & Playlist Search (`search_videos`)**: Search videos, channels, or playlists with filters for date (`published_after`), order (`relevance`, `viewCount`, `date`), and region codes.
- **🚀 Breakout Growth Channels (`find_breakout_growth_channels`)**: Identify newly created channels (e.g. last 6–24 months) that grew rapidly with high subscriber velocity, revealing what's working in today's algorithm.
- **🎯 Content Gap & Low-Competition Search (`find_content_gaps`)**: Find high-demand search topics where top rankings are held by outdated videos (2+ years old) or small channels, revealing easy rank-1 opportunities.
- **🎯 Multi-Niche Campaign Scouting (`scout_niche_channels`)**: Run batch discovery campaigns across multiple topics to find, filter, and rank the best creators by subscriber size, total views, or average views per video.
- **🚀 Viral Outlier Detection (`find_viral_outliers`)**: Spot 2.5x to 10x+ breakout videos that dramatically outperform a channel's normal average to discover viral concepts.
- **🔥 Real-Time Trend Discovery (`get_trending_niches`)**: Tap directly into YouTube's official real-time trending chart (`chart="mostPopular"`) to surface exploding niches, rising tags, recurring keywords, and breakout creators.

### 🔬 Channel Reverse Engineering Engine
- **🧬 Deep Channel Reverse Engineering (`reverse_engineer_channel`)**: **(Flagship)** Conducts complete reverse engineering of any YouTube channel:
  - **Algorithm Engine**: Detects whether growth is driven by Search & Browse (viral) or subscriber loyalty via view-to-subscriber ratios.
  - **Upload Cadence & Consistency**: Calculates average days between uploads and consistency rating.
  - **Title & Packaging Formulas**: Deconstructs high-CTR patterns (listicles, question hooks, negative framing, brackets).
  - **Top vs Flop Analysis**: Identifies what video topics blow up vs what gets ignored.
  - **Opening 60s Script Hook**: Transcribes and extracts the exact problem-solution hook from their best video.
  - **Monetization Blueprint**: Detects sponsors, affiliate links, newsletters (Beehiiv/Substack), and paid communities (Skool/Discord).
  - **Audience Flaws & Gaps**: Mines real viewer comments on their top video to find unanswered questions and complaints.
  - **Beginner Replication Playbook**: Provides exact title frameworks and differentiation angles for a new creator to model or compete.
- **📝 Retention Script Generator (`generate_retention_script_outline`)**: Generates an 8-12 minute psychology-backed video outline modeled on competitor hooks and real viewer comments to maximize watch time.
- **💰 Niche Sponsor Radar (`discover_niche_sponsors`)**: Scans top videos in any niche to identify active paying brand sponsors, promo codes, tracking links, and sponsorship frequency.
- **📊 Channel Strategy & Playbook Auditor (`audit_channel_strategy`)**: Fast audit of a creator's publishing cadence, title formulas, and monetization funnel.
- **⚔️ Competitor Benchmarking (`compare_channels`)**: Perform head-to-head performance comparisons across 2 to 5 rival channels.
- **💬 Audience Sentiment & Pain-Point Mining (`analyze_audience_sentiment`)**: Mine comments for unanswered questions, viewer content requests, and recurring audience problems.
- **✂️ Video Chapters & Viral Shorts Extractor (`extract_shorts_clips`)**: Generate timestamped chapters and extract top 30-60s punchy Shorts clips from transcripts.
- **🗺️ Channel Launch Blueprint (`blueprint_new_channel`)**: All-in-one market research and 5-video launch roadmap for beginners.

### 🛠️ Core Data & Transcript Tools
- **📹 Video Details (`get_video_details`)**: Clean metadata (views, likes, human-formatted duration, channel info, tags).
- **📝 Transcripts (`get_video_transcript`)**: Fetch full video subtitles **without requiring an API key or OAuth** in `text`, `timestamped`, or `json` formats.
- **👤 Channel Insights (`get_channel_details`)**: Look up subscriber counts, view statistics, and upload playlists by Channel ID, `@handle`, or username.
- **📂 Playlists (`get_playlist_items`)**: Browse items and videos within any public playlist.
- **💬 Comments (`get_video_comments`)**: Fetch top-level comments and community discussions.

### 🧠 Built-in MCP Prompts
- **`launch_new_channel_prompt`**: End-to-end prompt that instructs the LLM to research a niche and design a 90-day launch roadmap.
- **`viral_video_ideas_prompt`**: Analyzes competitor outliers and generates 10 high-CTR video concepts with thumbnail descriptions and opening hooks.
- **`competitor_playbook_prompt`**: Deconstructs competitor retention, scripting, and monetization funnels.

---

## Prerequisites

- **Python**: 3.10 or higher
- **Package Manager**: [uv](https://docs.astral.sh/uv/) (recommended) or `pip`
- **YouTube API Key (Optional for transcripts, required for Data API calls)**:
  1. Go to [Google Cloud Console](https://console.cloud.google.com/).
  2. Create a project and enable **YouTube Data API v3**.
  3. Create an API Key under **APIs & Services > Credentials**.

---

## Quickstart

### 1. Run with `uvx` (Instant Execution)

You can run the server directly without manual installation using `uvx`:

```bash
export YOUTUBE_API_KEY="your_api_key_here"
uvx --from . youtube-mcp
```

### 2. Local Installation & Development

```bash
# Clone and enter directory
cd youtube-mcp

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Copy environment template and configure key
cp .env.example .env
# Edit .env and set your YOUTUBE_API_KEY
```

Run locally:
```bash
# Standard stdio mode (default)
python -m youtube_mcp

# SSE remote mode
python -m youtube_mcp --transport sse --host 127.0.0.1 --port 8000
```

---

## MCP Client Configuration

### Claude Desktop

Add the following to your Claude Desktop configuration file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "youtube": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/mohamedbenyahia/Desktop/dev-projects/youtube-mcp",
        "run",
        "youtube-mcp"
      ],
      "env": {
        "YOUTUBE_API_KEY": "YOUR_YOUTUBE_API_KEY"
      }
    }
  }
}
```

### Cursor & Windsurf

Add to your project's `.cursor/mcp.json` or global MCP settings:

```json
{
  "mcpServers": {
    "youtube": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/mohamedbenyahia/Desktop/dev-projects/youtube-mcp",
        "run",
        "youtube-mcp"
      ],
      "env": {
        "YOUTUBE_API_KEY": "YOUR_YOUTUBE_API_KEY"
      }
    }
  }
}
```

### Antigravity IDE

Add to `.agents/mcp_config.json` (or `~/.gemini/config/mcp_config.json`):

```json
{
  "mcpServers": {
    "youtube": {
      "command": "/Users/mohamedbenyahia/Desktop/dev-projects/youtube-mcp/.venv/bin/python",
      "args": [
        "-m",
        "youtube_mcp"
      ],
      "env": {
        "YOUTUBE_API_KEY": "YOUR_YOUTUBE_API_KEY"
      }
    }
  }
}
```

---

## Available Tools & Schema

### `get_video_transcript`
Extracts subtitles and transcripts from YouTube videos. **Does not require a YouTube API key.**

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `video_id_or_url` | `string` | *required* | Video ID (`dQw4w9WgXcQ`) or full URL (`https://youtu.be/...`). |
| `languages` | `list[string]` | `["en"]` | Priority list of ISO 639-1 language codes. |
| `format` | `string` | `"text"` | Output format: `"text"`, `"timestamped"` (`[hh:mm:ss] text`), or `"json"`. |
| `start_seconds` | `float` | `None` | Start timestamp in seconds to crop transcript. |
| `end_seconds` | `float` | `None` | End timestamp in seconds to crop transcript. |

---

### `search_videos`
Search YouTube for videos, channels, or playlists.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `query` | `string` | *required* | Search query text. |
| `max_results` | `integer` | `10` | Number of results (1 to 50). |
| `search_type` | `string` | `"video"` | `"video"`, `"channel"`, or `"playlist"`. |
| `order` | `string` | `"relevance"` | `"relevance"`, `"date"`, `"viewCount"`, `"rating"`, or `"title"`. |
| `published_after` | `string` | `None` | RFC 3339 datetime (e.g. `'2024-01-01T00:00:00Z'`). |
| `region_code` | `string` | `None` | ISO 3166-1 alpha-2 country code (e.g. `'US'`, `'GB'`). |
| `raw` | `boolean` | `false` | Return unparsed raw API payload if `true`. |

---

### `search_channels` (Direct Channel Discovery)
Search YouTube specifically for channels matching a niche or topic, automatically enriched with current subscriber counts, total view counts, video counts, handles, and URLs in one token-efficient call.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `query` | `string` | *required* | Channel topic, niche keywords, or creator name (e.g. `"ai automation"`, `"budget travel"`). |
| `max_results` | `integer` | `10` | Number of channels to return (1 to 50). |
| `order` | `string` | `"relevance"` | `"relevance"`, `"videoCount"`, `"viewCount"`, or `"rating"`. |
| `region_code` | `string` | `None` | ISO 3166-1 alpha-2 country code (e.g. `"US"`, `"GB"`, `"CA"`). |

---

### `get_video_details`
Retrieve structured metadata for one or more video IDs.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `video_ids` | `list[string]` | *required* | List of video IDs or URLs (up to 50). |
| `raw` | `boolean` | `false` | Return unparsed raw API payload if `true`. |

---

### `get_channel_details`
Retrieve channel details, stats, subscriber count, and upload playlist ID.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `channel_id` | `string` | `None` | Channel ID (`UC...`). |
| `for_handle` | `string` | `None` | Channel handle with or without `@` (`@mkbhd` or `veritasium`). |
| `for_username` | `string` | `None` | Legacy YouTube username. |
| `raw` | `boolean` | `false` | Return unparsed raw API payload if `true`. |

---

### `get_playlist_items`
Retrieve videos within a playlist.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `playlist_id` | `string` | *required* | Playlist ID or channel upload playlist ID. |
| `max_results` | `integer` | `20` | Results per page (up to 50). |
| `page_token` | `string` | `None` | Pagination token. |
| `raw` | `boolean` | `false` | Return unparsed raw API payload if `true`. |

---

### `get_video_comments`
Retrieve top-level comment threads and discussion for a video.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `video_id` | `string` | *required* | Video ID or URL. |
| `max_results` | `integer` | `20` | Number of comments (up to 100). |
| `order` | `string` | `"relevance"` | `"relevance"` or `"time"`. |
| `page_token` | `string` | `None` | Pagination token. |
| `raw` | `boolean` | `false` | Return unparsed raw API payload if `true`. |

---

### `scout_niche_channels` (Campaign Discovery)
Launch multi-niche creator scouting campaigns to find, filter, and rank the best YouTube channels.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `niches` | `list[string]` | *required* | List of topic niches / keywords (e.g. `["ai automation", "productivity tools"]`). |
| `min_subscribers` | `integer` | `0` | Minimum subscriber threshold (e.g. `10000` for micro-influencers). |
| `max_subscribers` | `integer` | `None` | Maximum subscriber threshold (e.g. `200000`). |
| `min_videos` | `integer` | `1` | Filter out dead/inactive channels with fewer videos. |
| `region_code` | `string` | `None` | ISO 3166-1 alpha-2 country code (e.g. `"US"`, `"GB"`). |
| `channels_per_niche` | `integer` | `10` | Top channels to return per niche. |
| `sort_by` | `string` | `"subscribers"` | Ranking metric: `"subscribers"`, `"views"`, `"videos"`, or `"avg_views"`. |

---

### `get_trending_niches` (Real-Time Trend Discovery)
Discover real-time trending topics, breakout niches, and viral videos right now using the official YouTube Trending algorithm.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `region_code` | `string` | `"US"` | Country code (e.g. `"US"`, `"GB"`, `"DE"`, `"CA"`, `"FR"`). |
| `category` | `string` | `"tech"` | Niche category (`"all"`, `"tech"`, `"gaming"`, `"education"`, `"howto"`, `"entertainment"`, `"news"`, `"music"`, `"sports"`, `"comedy"`). |
| `max_results` | `integer` | `25` | Number of trending videos to analyze (up to 50). |
| `raw` | `boolean` | `false` | Return unparsed raw API payload if `true`. |

---

### `reverse_engineer_channel` (Deep Channel Reverse Engineering & Replication Playbook)
Conducts full end-to-end reverse engineering on any YouTube channel. Deconstructs upload frequency, view-to-sub engagement ratio, best vs lowest performing video topics, title formulas, first 60s script hook, full monetization funnel, and mines real viewer comments for unmet content requests and pain points.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `channel_id_or_handle` | `string` | *required* | Channel handle (e.g. `"@mkbhd"`, `"@aliabdaal"`), channel ID (`"UC..."`), or username. |
| `sample_videos` | `integer` | `5` | Number of recent uploads to analyze (3 to 15, default 5). |
| `include_audience_gaps` | `boolean` | `true` | Mine top video comment section for audience complaints and video requests. |

#### Example Output:
```json
{
  "success": true,
  "channel": {
    "title": "Ali Abdaal",
    "handle": "@aliabdaal",
    "subscribers": 5800000,
    "total_views": 480000000
  },
  "growth_and_cadence": {
    "estimated_cadence": "Weekly (approx. 1 video per week)",
    "avg_recent_views": 850000,
    "view_to_sub_ratio": "14.7%",
    "algorithm_growth_engine": "Subscriber Loyalty Driven"
  },
  "content_strategy_breakdown": {
    "title_formulas": [
      "Numbers & Listicles (e.g. '7 Tips')",
      "Negative Framing (e.g. 'Stop Doing This')",
      "Question Hooks"
    ],
    "top_performing_video": {
      "title": "How to Study for Exams - Spaced Repetition",
      "views": 4200000,
      "duration": "14:22"
    },
    "first_60s_hook_script": "In this video, I'm going to show you the exact active recall system..."
  },
  "monetization_blueprint": {
    "affiliate_links": ["https://amzn.to/...", "https://linktr.ee/..."],
    "newsletters": ["https://aliabdaal.com/newsletter"],
    "courses_communities": ["https://skool.com/..."],
    "sponsor_disclosures": ["Sponsored by Notion", "Sponsored by Skillshare"]
  },
  "audience_unmet_needs_and_flaws": {
    "unanswered_viewer_questions": [{"comment": "How do you do this if you have ADHD?", "like_count": 420}],
    "viewer_content_requests": [{"comment": "Can you do an updated 2026 version for college?", "like_count": 310}]
  },
  "beginner_replication_playbook": {
    "actionable_takeaways": [
      "Model their top title structure (Numbers & Listicles).",
      "Replicate the 60s problem-solution hook.",
      "Target the ADHD / beginner angle that their viewers asked for in comments."
    ]
  }
}
```

---

### `audit_channel_strategy` (Channel Strategy & Playbook Auditor)
Reverse-engineer any YouTube channel's publishing cadence, title formulas, monetization funnel, and opening script hook from their top-performing video.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `channel_id_or_handle` | `string` | *required* | Channel handle (e.g. `"@mkbhd"`, `"@aliabdaal"`), channel ID (`"UC..."`), or username. |
| `sample_videos` | `integer` | `5` | Number of recent uploads to analyze (3 to 15). |

---

### `find_viral_outliers` (Viral Concept Finder)
Identify breakout videos that generated 2.5x to 10x+ more views than a channel's normal average, either within a niche or for a specific creator.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `query` | `string` | *required* | Topic keyword (e.g. `"ai productivity"`) or creator handle (`"@creator"`). |
| `min_multiplier` | `float` | `2.5` | Minimum performance multiplier over channel baseline (e.g. `2.5` = 2.5x). |
| `published_after` | `string` | `None` | RFC 3339 datetime to filter recent breakouts. |
| `max_results` | `integer` | `25` | Number of candidates to evaluate (up to 50). |

---

### `analyze_audience_sentiment` (Pain Points & Idea Mining)
Mine comments on any video to discover audience pain points, objections, unanswered questions, and viewer content requests.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `video_id_or_url` | `string` | *required* | YouTube Video ID or full URL. |
| `max_comments` | `integer` | `100` | Top comments to analyze (up to 100). |

---

### `compare_channels` (Competitor Benchmarking)
Perform head-to-head benchmarking between 2 to 5 competing YouTube channels.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `channel_handles` | `list[string]` | *required* | List of 2 to 5 channel handles (e.g. `["@mkbhd", "@Dave2D"]`) or IDs. |

---

### `extract_shorts_clips` (Repurposing & Chapters)
Automatically generate YouTube chapter timestamps and identify the top 30-60s viral Shorts/Reels clips from transcripts. **No API key required.**

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `video_id_or_url` | `string` | *required* | YouTube Video ID or full URL. |
| `min_duration_seconds` | `integer` | `20` | Minimum clip duration in seconds. |
| `max_duration_seconds` | `integer` | `60` | Maximum clip duration in seconds. |
| `max_clips` | `integer` | `5` | Number of non-overlapping candidate clips to return. |

---

### `blueprint_new_channel` (Beginner Channel Launch Blueprint)
Executes an all-in-one market research study to launch a brand new YouTube channel in any niche. Automatically validates demand, scouts mid-tier model channels (1k–300k subs), identifies viral breakout topics, extracts audience pain points from comments, and outputs a 5-video launch roadmap.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `niche` | `string` | *required* | Target topic / niche (e.g. `"ai tools for creators"`, `"notion workflows"`, `"budget travel"`). |
| `target_audience` | `string` | `None` | Ideal viewer profile (e.g. `"complete beginners"`, `"busy students"`, `"freelancers"`). |
| `region_code` | `string` | `"US"` | Target geographic market code (e.g. `"US"`, `"GB"`, `"DE"`, `"CA"`). |

#### Example Output:
```json
{
  "success": true,
  "niche": "notion workflows",
  "target_audience": "busy students",
  "market_validation": {
    "demand_status": "High",
    "model_channels_found": 5,
    "viral_outliers_identified": 5
  },
  "competitors_to_model": [
    {
      "channel_name": "Student Study Hub",
      "handle": "@studentstudyhub",
      "subscribers": 42000,
      "avg_views_per_video": 28000,
      "url": "https://youtube.com/@studentstudyhub"
    }
  ],
  "audience_unmet_needs": {
    "audience_questions": [{"comment": "How do I sync Notion with Google Calendar?", "like_count": 89}],
    "viewer_video_requests": [{"comment": "Please do a full beginner tutorial for exams!", "like_count": 134}],
    "common_pain_points": [{"comment": "Most templates are way too complicated to actually use.", "like_count": 62}]
  },
  "first_5_videos_to_record": [
    {
      "video_number": 1,
      "inspired_by_outlier": "My Simple Notion Setup for College",
      "suggested_title_framework": "My Simple Notion Setup for College (Beginner's Step-by-Step Guide)",
      "why_this_works": "Proven demand with 5.4x views above channel baseline."
    }
  ],
  "launch_recommendations": {
    "recommended_upload_schedule": "1 to 2 videos per week (consistency > quantity)",
    "recommended_video_length": "8 to 14 minutes (optimal for retention + mid-roll eligibility)",
    "first_30_seconds_rule": "Hook viewers within the first 10 seconds: state the exact problem, show the end result, and promise the solution.",
    "monetization_roadmap": [
      "Stage 1 (0 - 1k subs): Free template lead magnet + affiliate links.",
      "Stage 2 (1k - 10k subs): AdSense + paid template pack.",
      "Stage 3 (10k+ subs): Sponsorships & cohort community."
    ]
  }
}
```

---

### `find_breakout_growth_channels` (Modern Breakout Channel Discovery)
Finds newly created channels (last 6–24 months) that blew up with high subscriber velocity, revealing what's working in today's algorithm.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `niche` | `string` | *required* | Target niche (e.g. `"ai coding"`, `"personal finance"`, `"fitness"`). |
| `max_channel_age_months` | `integer` | `24` | Maximum channel age in months. |
| `min_subscribers` | `integer` | `1000` | Minimum subscriber threshold. |
| `max_subscribers` | `integer` | `300000` | Maximum subscriber threshold. |
| `region_code` | `string` | `"US"` | Country code. |
| `max_results` | `integer` | `10` | Max channels to return. |

---

### `find_content_gaps` (Low-Competition Keyword Opportunities)
Identifies search topics where top rankings are held by outdated videos (2+ years old), signaling easy ranking opportunities for a fresh 2026 video.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `niche_or_topic` | `string` | *required* | Search query or question (e.g. `"how to learn sql for data analysis"`). |
| `max_results` | `integer` | `15` | Results to evaluate. |
| `region_code` | `string` | `"US"` | Country code. |

---

### `generate_retention_script_outline` (Retention-Engineered Script Outline)
Generates an 8-12 minute YouTube video outline engineered for high viewer retention, modeled on competitor transcripts and real viewer comment pain points.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `video_title_or_topic` | `string` | *required* | The video title or topic to outline. |
| `competitor_video_id_or_url` | `string` | `None` | Optional competitor video to model hook and comments from. |
| `target_audience` | `string` | `"Beginners"` | Ideal viewer demographic. |
| `target_duration_minutes` | `integer` | `10` | Video duration in minutes. |

---

### `discover_niche_sponsors` (Active Brand Sponsor Radar)
Scans the top videos in a niche to discover which brands and SaaS companies are actively paying creators for sponsorships, including coupon codes and tracking URLs.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `niche_or_query` | `string` | *required* | Niche topic or keyword (e.g. `"productivity apps"`, `"coding"`). |
| `sample_videos` | `integer` | `20` | Number of top videos to inspect (10 to 30). |
| `region_code` | `string` | `"US"` | Country code. |

---

## 🧠 Built-in Prompts

MCP clients supporting prompts (such as Claude Desktop and Cursor) can trigger automated market research workflows with one click:

1. **`launch_new_channel_prompt(niche, target_audience)`**:
   - Researches the niche, verifies viewer demand, scouts realistic 1k–300k sub competitors, uncovers viral outlier topics, and writes a complete 90-day launch roadmap.
2. **`viral_video_ideas_prompt(niche_or_channel, count)`**:
   - Extracts viral outliers and generates high-converting titles, visual thumbnail concepts, and hook scripts.
3. **`competitor_playbook_prompt(channel_handle)`**:
   - Deconstructs a competitor's upload cadence, monetization strategy, and script hooks from their top videos.

---

## Running Tests

Run the full pytest suite with:

```bash
pytest -v
```

All tests mock Google API and transcript network requests to prevent burning quota during CI/CD.

---

## License

MIT License.
