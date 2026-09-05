---
name: competitor-intelligence
description: >-
  Reverse engineer competitor YouTube channels, benchmark multiple rivals head-to-head,
  discover paying brand sponsors, and identify cross-language international arbitrage opportunities.
---

# Competitor Intelligence Skill

Use this workflow to conduct deep competitive reconnaissance in any YouTube vertical, discovering untapped sponsor budgets, proven monetization funnels, and unserved international markets.

## Procedure

### 1. Reverse-Engineer the Category Leader
Call `reverse_engineer_channel`:
- Pass `channel_id_or_handle` of the dominant competitor.
- Analyze their subscriber conversion velocity, publishing frequency, viral outlier topics, description funnel links, and opening retention hook.

### 2. Head-to-Head Competitor Benchmarking
Call `compare_channels`:
- Pass 2 to 5 rival channel handles or IDs in `channel_identifiers`.
- Benchmark engagement rates, view-to-subscriber ratios, upload frequencies, and find which creator is growing fastest relative to their size.

### 3. Discover Paying Brand Sponsors
Call `discover_niche_sponsors`:
- Pass `niche_keyword` or `competitor_channel_id`.
- Extract verified brand sponsors who are actively spending marketing budget in this niche, complete with discount codes and landing page URLs.
- Build an outreach pitch list of verified niche sponsors.

### 4. Cross-Language Content Arbitrage
Call `find_cross_language_opportunities`:
- Pass `topic_or_niche` and `target_languages` (e.g. `["es", "pt", "de", "fr"]`).
- Identify proven viral English video formats with massive view counts that have near-zero competition in other high-GDP language markets.

### 5. Compile Executive Intelligence Brief
Deliver a structured competitor intelligence dossier:
- **Competitor Funnel Architecture**: How rivals monetize (courses, sponsors, affiliate tools).
- **Active Sponsor Database**: Brands actively sponsoring creators in this niche.
- **Vulnerability Matrix**: Where competitors are weak (outdated videos, low comment response, monotonous pacing).
- **International Expansion Angles**: Top translated opportunities ready for immediate capture.
