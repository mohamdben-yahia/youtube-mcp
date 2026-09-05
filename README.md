<div align="center">

# 🎬 YouTube MCP Server

### The Most Powerful YouTube API Server for AI Agents

**33 tools · 3 dynamic resources · 3 prompts · 101+ tests · 100% live YouTube Data API**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![MCP Protocol](https://img.shields.io/badge/MCP-Model_Context_Protocol-blueviolet?style=for-the-badge)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-101%2B_Passed-success?style=for-the-badge)](tests/)
[![Claude Desktop](https://img.shields.io/badge/Claude-Desktop-orange?style=for-the-badge)](https://claude.ai)
[![Cursor](https://img.shields.io/badge/Cursor-IDE-blue?style=for-the-badge)](https://cursor.com)

</div>

---

> **YouTube MCP Server** is a production-ready [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that gives AI assistants — **Claude Desktop**, **Cursor**, **Windsurf**, **Antigravity**, and any MCP-compatible LLM agent — deep, real-time access to **YouTube Data API v3**, **video transcripts**, **audience analytics**, **competitor intelligence**, **SEO metadata generation**, and **creator monetization strategy**.
>
> Built for **YouTube creators**, **content strategists**, **growth agencies**, and **developers** building AI-powered YouTube tools.

---

## ⚡ Why Use This YouTube MCP Server?

### 🛑 The Problem: Why Standard AI & Traditional Tools Fail

1. **LLMs Are Blind to Real-Time YouTube Data**: Large Language Models (Claude, ChatGPT) have knowledge cutoff dates. Without live YouTube access, they cannot analyze what is trending today, identify which competitor videos are currently blowing up, read viewer sentiment in comments, or inspect live thumbnail packaging.
2. **Manual Creator Research Takes 10+ Hours/Week**: Reverse-engineering rival upload cadences, calculating retention drop-off pacing, hunting paying brand sponsors, extracting subtitles, and designing multi-video binge funnels manually is exhausting and error-prone.
3. **Existing YouTube MCP Servers Are Toy Wrappers**: Most open-source tools only wrap 2–3 basic endpoints (`search`, `video_details`) that dump massive raw JSON responses, immediately overflowing your LLM's context window and burning tokens.
4. **Google API Quota Crashes**: The free YouTube Data API limit is only 10,000 units/day (`search.list` costs 100 units). Standard tools crash with `403 QuotaExceeded` after just a few deep queries.

---

### 🚀 The Solution: A Complete Algorithmic Growth Engine for AI

**YouTube MCP Server** transforms any AI assistant into an elite, full-stack YouTube growth director:

* **🧠 Token-Efficient Intelligence**: Every tool strips away API bloat and returns structured, high-signal Markdown payloads engineered specifically for LLM reasoning and minimal context consumption.
* **🛠️ 33 Specialized Creator & Research Tools**: Goes far beyond basic data retrieval. Includes algorithmic publishing heatmaps, WPM pacing retention analyzers, psychological title CTR grading, 3-tier sub-1k monetization funnels, and international arbitrage detectors.
* **🛡️ Quota-Resilient Architecture**:
  * **Multi-Key Pool (`YOUTUBE_API_KEYS`)**: Automatically rotates across multiple Google API keys on 403 errors with zero downtime.
  * **Zero-Quota Public RSS Feed (`get_channel_rss_videos`)**: Pulls recent channel uploads via public Atom feeds with **0 quota consumption** and **requires NO API key**.
  * **Persistent Disk TTL Caching**: Local caching preserves quota across agent sessions.
* **🤖 Turnkey Agent Workflows**: With the included **11 Antigravity Skills** and the master `youtube-full-pipeline` orchestrator, an AI agent can execute an entire 7-phase channel strategy from a single prompt.

---

### 👥 Who Is This For?

| Persona | How They Use This MCP |
| :--- | :--- |
| **🎬 Solo YouTubers & Creators** | Stop guessing video topics. Find proven 2.5x+ viral outliers, generate 7-beat retention scripts modeled on top performers, and craft high-CTR title formulas in seconds. |
| **🏢 Growth Agencies & Strategists** | Deliver institutional-grade channel audit reports, competitor benchmark decks, and 30-day master content calendars to paying clients in 2 minutes instead of 8 hours. |
| **🤖 AI Developers & Agent Builders** | Build autonomous YouTube agents (CrewAI, LangChain, Claude Desktop, Cursor) with a battle-tested, strictly real-data, production-grade MCP server. |
| **💰 Influencer Marketers & Brands** | Scout breakout micro-influencers (1k–50k subs) with 3x+ engagement velocity and discover paying sponsors across any niche. |

---

### 🛡️ Strict Real-Data Guarantee (Zero Fake / Mock Fallbacks)

> [!IMPORTANT]
> **This server operates strictly on 100% authentic, live YouTube data.**
> - **Zero Mock / Synthetic Fallbacks**: Unlike basic demos that return placeholder videos or fabricated statistics, this server connects directly to Google's live YouTube Data API v3, YouTube's official Atom XML feeds, and YouTube's player caption streams.
> - **Transparent Error Handling**: If an API key is invalid or quota is exhausted, the server explicitly returns the real Google error (`401 Unauthorized` or `403 QuotaExceeded`). It **never** silently invents fake videos, channels, or view counts.
> - **100% Verifiable Data**: Every `video_id`, `channel_id`, view count, and spoken transcript segment returned maps directly to authentic, public videos on `https://www.youtube.com`.

---

### 📊 Feature Comparison: YouTube MCP Server vs. Alternatives

| Feature | YouTube MCP Server | Other YouTube Tools |
| :--- | :---: | :---: |
| **MCP-native** (Claude, Cursor, Windsurf, LLM agents) | ✅ | ❌ |
| **33 specialized creator & research tools** | ✅ | 3–5 basic tools |
| **Multi-key quota rotation pool** (`YOUTUBE_API_KEYS`) | ✅ | ❌ (Hard 403 crashes) |
| **Zero-quota public RSS video feed** | ✅ | ❌ |
| **Live YouTube Data API** (real tags, real thumbnails, real comments) | ✅ | Static/mock data |
| **Transcript extraction without API key** | ✅ | Requires OAuth |
| **Competitor reverse engineering** | ✅ | ❌ |
| **Viral outlier detection** (2.5x–10x view spikes) | ✅ | ❌ |
| **SEO metadata pack generation** (titles, tags, chapters) | ✅ | ❌ |
| **Thumbnail concept generator** (with Midjourney/DALL-E prompts) | ✅ | ❌ |
| **Sponsor discovery & pitch architect** | ✅ | ❌ |
| **International cross-language arbitrage** | ✅ | ❌ |
| **Sub-1k subscriber monetization funnels** | ✅ | ❌ |
| **Binge playlist architect** (Session Watch Time optimization) | ✅ | ❌ |
| **11 Antigravity workflow skills** (full auto-pipeline) | ✅ | ❌ |
| **Disk-based quota caching** | ✅ | ❌ |
| **Docker & SSE remote hosting** | ✅ | ❌ |
| **101 automated tests** | ✅ | Untested |

---

## 📋 Table of Contents

- [⚡ Why Use This YouTube MCP Server?](#-why-use-this-youtube-mcp-server)
- [🎯 5-Step Market Research Workflow](#-built-for-new-creators-the-5-step-market-research-workflow)
- [🔍 Features & Tool Suite](#features--tool-suite)
- [📦 Prerequisites](#prerequisites)
- [🚀 Quickstart](#quickstart)
- [⚙️ MCP Client Configuration](#mcp-client-configuration) — Claude Desktop, Cursor, Windsurf, Antigravity
- [📖 Available Tools & Schema](#available-tools--schema) — Full parameter documentation for all 33 tools
- [🌐 Dynamic MCP Resources](#-dynamic-mcp-resources-youtube-uris)
- [🧠 Built-in Prompts](#-built-in-prompts)
- [🐳 Docker & Remote Hosting](#-docker--remote-hosting-server-sent-events)
- [🧪 Running Tests](#-running-tests)
- [📦 Complete Tool Index](#-complete-tool-index-33-mcp-tools)
- [🔌 Compatibility](#-compatibility)
- [🤖 Antigravity Plugin: 11 Skills](#-antigravity-plugin-11-workflow-skills)
- [🏗️ Tech Stack](#️-tech-stack)

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
- **🖼️ High-CTR Thumbnail Concepts (`generate_thumbnail_concepts`)**: Deconstructs contrast and color psychology to output 3 distinct thumbnail visual concepts with ready-to-use Midjourney/DALL-E prompts.
- **🏷️ Complete Upload SEO Pack (`generate_seo_metadata_pack`)**: Generates 3 mobile-optimized titles (<50 chars), timestamped chapter description, top 15 ranked tags, and engagement pinned comment.
- **💰 Niche Sponsor Radar (`discover_niche_sponsors`)**: Scans top videos in any niche to identify active paying brand sponsors, promo codes, tracking links, and sponsorship frequency.
- **📊 Channel Strategy & Playbook Auditor (`audit_channel_strategy`)**: Fast audit of a creator's publishing cadence, title formulas, and monetization funnel.
- **⚔️ Competitor Benchmarking (`compare_channels`)**: Perform head-to-head performance comparisons across 2 to 10 rival channels.
- **💬 Audience Sentiment & Pain-Point Mining (`analyze_audience_sentiment`)**: Mine comments for unanswered questions, viewer content requests, and recurring audience problems.
- **✂️ Video Chapters & Viral Shorts Extractor (`extract_shorts_clips`)**: Generate timestamped chapters and extract top 30-60s punchy Shorts clips from transcripts.
- **🗺️ Channel Launch Blueprint (`blueprint_new_channel`)**: All-in-one market research and 5-video launch roadmap for beginners.
- **📑 Markdown & Notion Report Exporter (`export_research_report`)**: Export an end-to-end market research study and 5-video launch roadmap into an executive-ready `.md` file formatted with tables, competitor rankings, and comment insights.
- **🌐 International Arbitrage Radar (`find_cross_language_opportunities`)**: Spot proven viral English topics with low competition in non-English markets (Spanish, French, German, Portuguese, Arabic, Japanese), providing localized title frameworks and translated hooks.
- **🧪 A/B Title Tester & CTR Predictor (`simulate_title_ctr`)**: Grades candidate titles against psychological click triggers (curiosity gaps, loss aversion, numbers, mobile <50 chars), predicts winning CTR, and generates 3 optimized high-CTR variants.
- **⏰ Upload Timing & Publishing Schedule Optimizer (`analyze_optimal_upload_time`)**: Analyzes competitor publishing days and hours to find low-congestion "Sweet Spot" upload windows before peak viewer activity.
- **📊 Retention Dropoff Predictor & Pacing Analyzer (`predict_retention_dropoffs`)**: Evaluates script/transcript words-per-minute pacing, detects monologue drop-off hazards, and injects timestamped visual pattern interrupts and retention resets.
- **🗳️ Community Tab & Viral Poll Strategy Engine (`analyze_community_posts`)**: Generates high-converting identity polls, video topic voting polls, and discussion drops that get pushed to non-subscribers' home feeds.
- **🔄 Shorts vs Long-Form Funnel Optimizer (`analyze_shorts_to_longform_ratio`)**: Computes competitor Shorts-to-long-form ratios and view disparities to prevent subscriber cannibalization.
- **🌲 Evergreen Search vs Viral Browse Classifier (`classify_traffic_potential`)**: Classifies topics into 3+ year passive search assets vs 14-day viral home feed spikes, estimating RPM and keyword packaging.
- **💎 Day-One Monetization Offer Architect (`generate_monetization_offers`)**: Designs 3 high-converting digital product tiers (Lead Magnet, $29 Template, High-Ticket Service) to monetize with under 1,000 subscribers without AdSense.
- **🔗 Binge-Watching Series & Playlist Architect (`design_binge_playlist`)**: Structures a 4-6 video serialized loop with cliffhanger end-screen bridging scripts to multiply Session Watch Time.
- **⚡ Multi-Key API Quota Rotator (`YOUTUBE_API_KEYS`)**: Load multiple Google Cloud API keys (`key1,key2,key3`). When any key hits a 403 `quotaExceeded` limit, the server automatically rotates to the next key without failing the user's request.
- **📡 Zero-Quota Public RSS Video Feed (`get_channel_rss_videos`)**: Fetches recent channel uploads with **0 API quota units** and **requires NO API key**, using YouTube's public XML Atom feeds.
- **💾 Persistent Quota Caching**: Built-in disk-based caching (`ResponseCache`) with configurable TTL and directory (`YOUTUBE_CACHE_ENABLED`, `YOUTUBE_CACHE_DIR`, `YOUTUBE_CACHE_TTL`) to preserve your 10,000 unit/day Google API quota.

### 🌐 Dynamic MCP Resources (`youtube://` URIs)
Exposes live context documents directly to LLMs:
- **`youtube://trending/{category}`**: Real-time trending videos, rising tags, and keyword analysis for any category.
- **`youtube://channel/{handle}/playbook`**: Complete reverse-engineered strategy report for any creator handle.
- **`youtube://niche/{niche}/blueprint`**: Live 5-video launch roadmap and competitor benchmarks for any topic.

### 🛠️ Core Data & Transcript Tools
- **📹 Video Details (`get_video_details`)**: Clean metadata (views, likes, human-formatted duration, channel info, tags).
- **📝 Transcripts (`get_video_transcript`)**: Fetch full video subtitles **without requiring an API key or OAuth** in `text`, `timestamped`, or `json` formats.
- **📡 Zero-Quota Recent Uploads (`get_channel_rss_videos`)**: Fetch latest uploads via public RSS feed with **zero quota consumption**.
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
- **YouTube API Key (Optional for transcripts & RSS, required for Data API calls)**:
  1. Go to [Google Cloud Console](https://console.cloud.google.com/).
  2. Create a project and enable **YouTube Data API v3**.
  3. Create an API Key under **APIs & Services > Credentials** (or multiple keys for rotation).

---

## Quickstart

### 1. 1-Click Install via Smithery (Easiest)

To automatically install and configure YouTube MCP Server for Claude Desktop via [Smithery](https://smithery.ai):

```bash
npx -y @smithery/cli install youtube-mcp --client claude
```

### 2. Instant Run with `uvx` (No Install Needed)

Run the server directly anywhere in 1 second using `uvx`:

```bash
# Single API Key
export YOUTUBE_API_KEY="your_api_key_here"

# Or Multi-Key Pool (automatic quota failover)
export YOUTUBE_API_KEYS="key_1,key_2,key_3"

uvx youtube-mcp
```

### 3. Install via `pip`

```bash
pip install youtube-mcp
youtube-mcp
```

### 4. Local Development (Clone from Source)

```bash
# Clone and enter directory
git clone https://github.com/mohamdben-yahia/youtube-mcp.git
cd youtube-mcp

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Copy environment template and configure key
cp .env.example .env
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

#### Option A: Direct Execution via `uvx` (Recommended — No clone required)
```json
{
  "mcpServers": {
    "youtube": {
      "command": "uvx",
      "args": ["youtube-mcp"],
      "env": {
        "YOUTUBE_API_KEY": "YOUR_YOUTUBE_API_KEY"
      }
    }
  }
}
```

#### Option B: Local Source / Cloned Repo
```json
{
  "mcpServers": {
    "youtube": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/youtube-mcp",
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
      "command": "uvx",
      "args": ["youtube-mcp"],
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
      "command": "uvx",
      "args": ["youtube-mcp"],
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
Perform head-to-head benchmarking between 2 to 10 competing YouTube channels.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `channel_handles` | `list[string]` | *required* | List of 2 to 10 channel handles (e.g. `["@channel1", "@channel2"]`) or IDs. |

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

### `generate_thumbnail_concepts` (High-CTR Packaging & AI Image Prompts)
Generates 3 distinct thumbnail visual concepts (Curiosity/Anomaly, Threat Avoidance/Mistake, Before-vs-After Split Screen) complete with text overlays, color theory palettes, and ready-to-run prompts for Midjourney / DALL-E / Imagen.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `video_title` | `string` | *required* | Video title or topic (e.g. `"How I Built a $10k/mo Micro-SaaS"`). |
| `target_niche` | `string` | `None` | Optional niche context (e.g. `"saas"`, `"coding"`). |
| `competitor_video_id_or_url` | `string` | `None` | Optional competitor video to evaluate thumbnail benchmarks. |

---

### `generate_seo_metadata_pack` (Complete YouTube Studio Upload Pack)
Generates the complete metadata package: 3 mobile-optimized titles (<50 chars), timestamped chapter description, top 15 ranked search tags, and an engagement-engineered pinned comment.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `topic` | `string` | *required* | Primary topic or draft title. |
| `key_takeaways` | `list[string]` | `None` | Optional list of main points covered. |
| `channel_name` | `string` | `None` | Creator channel name. |
| `affiliate_links` | `list[string]` | `None` | List of affiliate URLs or resource links. |

---

### `export_research_report` (Publication-Ready Markdown / Notion Exporter)
Generates an executive-ready `.md` research report complete with competitor comparison tables, audience pain points, viral reference URLs, and a 5-video launch roadmap, saving it to disk or returning the markdown directly.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `niche` | `string` | *required* | Target niche or topic (e.g. `"ai automation"`, `"personal finance"`). |
| `target_audience` | `string` | `None` | Optional description of target viewers (e.g. `"freelancers"`, `"students"`). |
| `output_file` | `string` | `None` | Custom output file path (defaults to `reports/<niche>_research_report.md`). |
| `region_code` | `string` | `"US"` | Target country code for localized search and metrics. |

---

### `find_cross_language_opportunities` (International Arbitrage Radar)
Identifies proven viral US/English video concepts and checks competition levels in non-English markets (Spanish, French, German, Portuguese, Italian, Arabic, Japanese), providing native translated title frameworks and opening script hooks.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `topic` | `string` | *required* | Core topic in English (e.g. `"notion for students"`, `"ai coding"`). |
| `target_language` | `string` | `"es"` | Target language code (`"es"`, `"fr"`, `"de"`, `"pt"`, `"ar"`, etc.). |
| `target_region` | `string` | `"ES"` | Target country code (`"ES"`, `"MX"`, `"FR"`, `"DE"`, `"BR"`, etc.). |
| `max_results` | `integer` | `5` | Maximum number of candidate arbitrage opportunities to evaluate. |

---

### `simulate_title_ctr` (A/B Title Tester & CTR Predictor)
Grades candidate video titles against YouTube psychological click triggers (curiosity gaps, loss aversion, numbers, power words, and mobile sweet-spots <50 chars), predicts the winning title, and generates 3 optimized variations for each candidate.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `titles` | `list[string]` | *required* | List of 1 to 8 candidate video titles to test against each other. |
| `target_niche` | `string` | `None` | Optional niche context (e.g. `"coding"`, `"finance"`, `"gaming"`). |

---

### `analyze_optimal_upload_time` (Publishing Schedule Optimizer)
Analyzes competitor publishing timestamps across day-of-week and hour-of-day distributions to uncover prime "Sweet Spot" upload windows before peak viewer activity.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `niche_or_channel` | `string` | *required* | Niche topic keyword or competitor channel handle. |
| `sample_size` | `integer` | `25` | Number of recent competitor uploads to sample (10 to 50). |
| `timezone_offset_hours` | `integer` | `0` | Timezone offset from UTC in hours (e.g. `-5` for EST, `+1` for CET). |

---

### `predict_retention_dropoffs` (Retention Dropoff Predictor & Pacing Analyzer)
Evaluates script or transcript words-per-minute (WPM) pacing across 1-minute blocks, flags flat monologue stretches (>45s without visual/audio changes), and injects timestamped retention resets.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `script_or_transcript` | `string` | `None` | Raw text of the draft script or spoken transcript. |
| `video_id_or_url` | `string` | `None` | Optional YouTube Video ID or URL to fetch and evaluate live transcript. |
| `target_duration_minutes` | `integer` | `None` | Optional target video runtime in minutes. |

---

### `analyze_community_posts` (Community Tab & Viral Poll Strategy Engine)
Generates high-converting identity polls, video topic voting polls, knowledge quizzes, and free resource drops that the YouTube algorithm distributes to non-subscribers' home feeds.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `niche_or_channel` | `string` | *required* | Topic, niche, or creator handle (e.g. `"python programming"`). |
| `target_goal` | `string` | `"growth"` | Goal: `"growth"`, `"video_validation"`, or `"audience_loyalty"`. |

---

### `analyze_shorts_to_longform_ratio` (Shorts vs Long-Form Funnel Optimizer)
Computes a channel's publishing ratio, view disparities between Shorts and long-form uploads, and diagnoses whether Shorts are cannibalizing channel watch time.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `channel_id_or_handle` | `string` | *required* | Channel handle (e.g. `'@aliabdaal'`) or Channel ID. |
| `sample_videos` | `integer` | `20` | Number of recent uploads to evaluate (10 to 50). |

---

### `classify_traffic_potential` (Evergreen Search vs Viral Browse Classifier)
Evaluates whether a video concept will succeed via long-tail Evergreen Search (3+ years passive views) or Browse Feature Spikes (home feed viral decay curve), estimating expected RPM and keyword packaging.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `topic_or_title` | `string` | *required* | Candidate video title, topic, or draft concept. |
| `target_niche` | `string` | `None` | Optional niche context (e.g. `"coding"`, `"personal finance"`). |

---

### `generate_monetization_offers` (Day-One Monetization Offer Architect)
Architects 3 high-converting monetization tiers (Free Lead Magnet, $19-$47 Impulse Template, $250-$750 Consulting) for creators with under 1,000 subscribers, with exact description box and spoken CTA scripts.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `niche` | `string` | *required* | Topic or niche (e.g. `"notion productivity"`, `"python coding"`). |
| `target_audience` | `string` | `None` | Target demographic (e.g. `"freelancers"`, `"beginners"`). |
| `main_skill_or_topic` | `string` | `None` | Specific core skill or software. |

---

### `design_binge_playlist` (Binge-Watching Series & Playlist Architect)
Architects a 4-to-6 video interconnected binge-watching series with end-screen cliffhanger scripts and optimized playlist metadata to maximize Session Watch Time.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `core_topic` | `string` | *required* | Overarching learning journey (e.g. `"Build an MCP Server in Python"`). |
| `video_count` | `integer` | `5` | Number of videos in series (3 to 6). |
| `target_audience` | `string` | `None` | Target viewer demographic. |

---

### `get_channel_rss_videos` (Zero-Quota Recent Uploads)
Fetches the latest video uploads from a YouTube channel using the public Atom RSS feed. **Consumes 0 Google Cloud API quota units and requires NO API key.**

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `channel_id` | `string` | *required* | Channel ID (`UC...`) or full channel URL. |
| `max_results` | `integer` | `15` | Maximum recent videos to return (1 to 15). |

---

## 🌐 Dynamic MCP Resources (`youtube://` URIs)

MCP clients can read dynamic live context resources directly:

| Resource URI | Description |
| :--- | :--- |
| `youtube://trending/{category}` | Real-time trending videos, breakout tags, and keywords (e.g. `youtube://trending/tech`). |
| `youtube://channel/{handle}/playbook` | Full reverse-engineered strategy report for any creator (e.g. `youtube://channel/@mkbhd/playbook`). |
| `youtube://niche/{niche}/blueprint` | Live 5-video launch roadmap for any niche (e.g. `youtube://niche/notion/blueprint`). |

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

## 🐳 Docker & Remote Hosting (Server-Sent Events)

Deploy this server remotely on **Railway**, **Fly.io**, **Render**, **DigitalOcean**, or your own server with Docker.

### 🔒 Hosted Security & Authentication (`MCP_AUTH_KEY`)
When hosting over SSE or HTTP on a remote network or public IP, the server **automatically enforces token authentication** to protect your YouTube API quota from unauthorized access:

* **Configured Key**: Set `MCP_AUTH_KEY=your_secret_token` in your `.env` or Docker environment.
* **Auto-Generated Key**: If `MCP_AUTH_KEY` is not set or set to `auto`, the server generates a cryptographically secure 256-bit token (`sec_...`) at startup and displays it in the logs.
* **Health Check Bypass**: Public `/health` and `/healthz` endpoints return `200 OK` without credentials, allowing Docker and load balancer health checks to pass cleanly.

```bash
# Build and run with Docker Compose (auto-secures with MCP_AUTH_KEY)
docker compose up -d

# Or run directly with Docker
docker build -t youtube-mcp .
docker run -d -p 8000:8000 \
  -e YOUTUBE_API_KEY="your_youtube_api_key" \
  -e MCP_AUTH_KEY="your_secret_auth_key" \
  youtube-mcp
```

### Remote MCP Client Configuration
Connect your Claude Desktop, Cursor, or remote agents to your secured instance:

```json
{
  "mcpServers": {
    "youtube-remote": {
      "url": "http://your-server-ip:8000/sse?api_key=your_secret_auth_key",
      "headers": {
        "Authorization": "Bearer your_secret_auth_key"
      }
    }
  }
}
```

---

## 🧪 Running Tests

```bash
# Run the full test suite
pytest -v

# Run with coverage
pytest -v --tb=short
```

All 101 tests mock Google API, RSS, and transcript network requests to prevent burning quota during CI/CD.

---

## 📦 Complete Tool Index (33 MCP Tools)

<details>
<summary><strong>Click to expand the full tool reference table</strong></summary>

| # | Tool Name | Category | Description |
| :-: | :--- | :--- | :--- |
| 1 | `search_videos` | Search | Search YouTube for videos, channels, or playlists with filters |
| 2 | `search_channels` | Search | Direct channel discovery with subscriber counts and stats |
| 3 | `get_video_details` | Data | Retrieve structured metadata for one or more videos |
| 4 | `get_channel_details` | Data | Channel stats, subscriber count, upload playlist ID |
| 5 | `get_playlist_items` | Data | Browse videos within any public playlist |
| 6 | `get_video_comments` | Data | Fetch top-level comments and discussions |
| 7 | `get_video_transcript` | Transcript | Extract subtitles without API key (text, timestamped, JSON) |
| 8 | `get_channel_rss_videos` | Data / Free | Zero-quota recent video uploads via public Atom RSS feed |
| 9 | `scout_niche_channels` | Discovery | Multi-niche creator scouting campaigns |
| 10 | `get_trending_niches` | Discovery | Real-time YouTube trending chart analysis |
| 11 | `find_breakout_growth_channels` | Discovery | Identify newly created high-velocity channels |
| 12 | `find_content_gaps` | Research | Find low-competition keywords with outdated ranking videos |
| 13 | `find_viral_outliers` | Research | Detect 2.5x–10x breakout videos on any channel |
| 14 | `audit_channel_strategy` | Audit | Reverse-engineer upload cadence, title formulas, monetization |
| 15 | `reverse_engineer_channel` | Audit | Complete deep channel reverse engineering |
| 16 | `compare_channels` | Audit | Head-to-head benchmarking of 2–10 rival channels |
| 17 | `analyze_audience_sentiment` | Audience | Mine comments for pain points, questions, and requests |
| 18 | `analyze_shorts_to_longform_ratio` | Audit | Diagnose Shorts-to-longform view cannibalization |
| 19 | `classify_traffic_potential` | Strategy | Classify Evergreen Search vs Browse traffic potential |
| 20 | `simulate_title_ctr` | Packaging | Grade titles against psychological click triggers |
| 21 | `generate_thumbnail_concepts` | Packaging | 3 visual concepts with Midjourney/DALL-E prompts |
| 22 | `generate_seo_metadata_pack` | SEO | Complete upload pack: titles, tags, chapters, description |
| 23 | `generate_retention_script_outline` | Scripting | 7-beat retention script modeled on competitor hooks |
| 24 | `predict_retention_dropoffs` | Scripting | WPM pacing analysis with pattern interrupt injection |
| 25 | `analyze_optimal_upload_time` | Scheduling | Competitor publishing heatmap and Sweet Spot windows |
| 26 | `analyze_community_posts` | Engagement | Viral polls, quizzes, and discussion strategies |
| 27 | `extract_shorts_clips` | Repurposing | Auto-generate chapters and viral 30–60s Shorts clips |
| 28 | `discover_niche_sponsors` | Monetization | Identify active paying brand sponsors in any niche |
| 29 | `generate_monetization_offers` | Monetization | 3-tier funnel for sub-1k subscriber creators |
| 30 | `design_binge_playlist` | Architecture | 4–6 video serialized loop with cliffhanger bridges |
| 31 | `find_cross_language_opportunities` | Expansion | Detect English hits with zero competition abroad |
| 32 | `export_research_report` | Reporting | Export formatted markdown dossier for Notion / clients |
| 33 | `blueprint_new_channel` | Launch | All-in-one market research & 5-video launch roadmap |

</details>

---

## 🔌 Compatibility

YouTube MCP Server works with **any MCP-compatible AI client**:

| Client | Status | Configuration |
| :--- | :---: | :--- |
| **Claude Desktop** (Anthropic) | ✅ Supported | `claude_desktop_config.json` |
| **Cursor IDE** | ✅ Supported | `.cursor/mcp.json` |
| **Windsurf IDE** | ✅ Supported | MCP settings |
| **Antigravity IDE** | ✅ Supported | `.agents/mcp_config.json` |
| **Continue.dev** | ✅ Supported | MCP configuration |
| **Custom LLM Agents** | ✅ Supported | MCP SDK integration |
| **Docker / SSE Remote** | ✅ Supported | `http://host:8000/sse` |

---

## 🤖 Antigravity & Agent Skills: Autonomous YouTube Growth Engine

While the **33 MCP Tools** provide the raw execution layer (YouTube API calls, RSS parsing, transcript analysis), the repository includes **11 Turnkey Agent Skills** in `.agents/skills/` and `.agents/plugins/youtube-creator-suite/`.

These skills act as high-level cognitive blueprints, allowing AI agents (such as Antigravity, Claude, or Cursor) to autonomously chain multiple MCP tools together into complete client-ready deliverables.

| Skill | Slash Command | What It Does |
| :--- | :--- | :--- |
| **Full Auto Pipeline** | `/youtube-full-pipeline` | 🔄 **Chains all 10 skills** across 7 automated phases: market recon → strategy → scripting → SEO → monetization → publishing → executive dossier. |
| **Channel Growth Audit** | `/channel-growth-audit` | Audits an existing channel's retention, Shorts-to-longform ratio, sentiment, and outputs a 90-day turnaround plan. |
| **Viral Video Ideation** | `/viral-video-ideation` | Discovers underserved content gaps, calculates CTR probabilities, and generates counter-positioned thumbnail ideas. |
| **Competitor Intelligence** | `/competitor-intelligence` | Benchmarks 2–5 rival channels head-to-head, identifies top upload formats, and extracts paying brand sponsors. |
| **Channel Launch Architect** | `/channel-launch-architect` | 0-to-1 blueprint: designs 5-video binge playlist loops, 7-beat retention scripts, and SEO upload packs. |
| **Content Repurposing** | `/youtube-content-repurposing` | Transcribes longform videos, generates timestamped chapters, extracts 30–60s viral Shorts clips, and writes community polls. |
| **Sponsor Pitch Architect** | `/sponsor-pitch-architect` | Identifies active sponsors in any vertical, computes CPM rate cards, and writes personalized brand outreach emails. |
| **Publishing Scheduler** | `/algorithmic-publishing-scheduler` | Analyzes competitor upload times, identifies low-competition Sweet Spot windows, and builds a 30-day master calendar. |
| **International Expansion** | `/international-arbitrage-expander` | Uncovers high-performing English videos with zero competition in Spanish/Portuguese/German and drafts localized metadata. |
| **Breakout Creator Scout** | `/breakout-creator-scout` | Discovers micro-creators (1k–50k subs) exhibiting 3x+ engagement velocity for partnership rosters. |
| **Executive Dossier** | `/executive-research-dossier` | Synthesizes all gathered market data into an institutional-grade Markdown or Notion report ready for clients. |

### 🚀 How to Run the Skills

#### In Antigravity IDE
The skills are automatically detected from `.agents/skills/`. Simply type the slash command in chat:
```text
/youtube-full-pipeline niche="ai automation" competitor_handles=["@mreflow", "@aiadvantage"]
```
or audit an existing creator:
```text
/channel-growth-audit channel_handle="@creatorhandle"
```

#### In Cursor / Claude Desktop / Other LLM Agents
Each skill is a self-contained, documented blueprint located in [`.agents/skills/`](file://.agents/skills/). You can pass the markdown file (e.g., [`SKILL.md`](file://.agents/skills/channel-growth-audit/SKILL.md)) directly to any agent as instructions while the YouTube MCP server is connected.


---

## 🏗️ Tech Stack

- **Protocol**: [Model Context Protocol (MCP)](https://modelcontextprotocol.io) via `mcp>=1.2.0`
- **YouTube API**: `google-api-python-client` (YouTube Data API v3)
- **Transcripts**: `youtube-transcript-api` (no API key required)
- **Validation**: `pydantic>=2.0.0`
- **Environment**: `python-dotenv`
- **Testing**: `pytest` + `pytest-asyncio` (101 unit tests for CI isolation)
- **Containerization**: Docker + Docker Compose (SSE remote hosting)
- **CI/CD**: GitHub Actions (Python 3.10–3.13 matrix)

---

## 🌟 Star History

If you find this useful, please ⭐ star the repository — it helps others discover it!

## 🤝 Contributing & Community

We welcome contributions of all kinds! Whether you want to add a new tool, improve documentation, or submit a bug fix:

* 📖 Read our [Contributing Guide](CONTRIBUTING.md) to get started with local development and testing.
* 📜 Check out the [Code of Conduct](CODE_OF_CONDUCT.md) for community guidelines.
* 🔒 Review our [Security Policy](SECURITY.md) to responsibly report vulnerabilities.
* 💡 Have an idea? [Open a Feature Request](https://github.com/mohamdben-yahia/youtube-mcp/issues/new?template=feature_request.md) or join [Discussions](https://github.com/mohamdben-yahia/youtube-mcp/discussions)!

---

## 📄 License

MIT License — free for personal and commercial use.

---

<div align="center">

**Built with ❤️ for YouTube creators, growth agencies, and AI developers**

[Report Bug](../../issues) · [Request Feature](../../issues) · [Discussions](../../discussions)

</div>
