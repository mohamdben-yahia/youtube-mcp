# Pipeline Phase Dependency Map & Tool Call Reference

## Tool Call Sequence Per Phase

This reference documents the exact MCP tool calls made in each phase, their dependencies, and which outputs flow forward.

---

### Phase 1: Market Intelligence
```
compare_channels(channel_identifiers)        → competitor_matrix
audit_channel_strategy(channel_id_or_handle)  → channel_diagnosis (if existing channel)
find_viral_outliers(channel_id_or_handle)     → outlier_topics
analyze_shorts_to_longform_ratio(handle)      → shorts_diagnosis (if existing channel)
analyze_audience_sentiment(video_id)          → pain_points, content_requests
scout_niche_channels(niches, filters)         → creator_watchlist
find_breakout_growth_channels(niche)          → breakout_creators
discover_niche_sponsors(niche_keyword)        → sponsor_roster
```
**Outputs passed forward**: `competitor_matrix`, `outlier_topics`, `pain_points`, `sponsor_roster`

---

### Phase 2: Content Strategy
```
find_content_gaps(niche_or_topic)             → content_gaps  [uses: niche]
classify_traffic_potential(topic_or_title)     → traffic_tags  [uses: content_gaps]
blueprint_new_channel(niche)                  → channel_blueprint
design_binge_playlist(core_topic, count=5)    → binge_roadmap
```
**Outputs passed forward**: `content_gaps`, `traffic_tags`, `binge_roadmap`

---

### Phase 3: Video Production
```
simulate_title_ctr(candidate_titles, niche)   → winning_titles  [uses: binge_roadmap]
generate_thumbnail_concepts(video_title)      → thumbnail_packs [uses: winning_titles]
generate_retention_script_outline(title)      → script_outlines [uses: winning_titles]
predict_retention_dropoffs(script)            → pacing_reports  [uses: script_outlines]
```
**Outputs passed forward**: `winning_titles`, `thumbnail_packs`, `script_outlines`

---

### Phase 4: Upload & Publishing
```
generate_seo_metadata_pack(title, audience)   → seo_packs      [uses: winning_titles]
analyze_optimal_upload_time(niche, tz)        → sweet_spot_windows
```
**Outputs passed forward**: `seo_packs`, `sweet_spot_windows`

---

### Phase 5: Monetization
```
generate_monetization_offers(niche, audience)  → monetization_funnel
discover_niche_sponsors(niche)                → sponsor_roster (from Phase 1, reused)
```
**Outputs passed forward**: `monetization_funnel`, `sponsor_pitches`

---

### Phase 6: Expansion
```
analyze_community_posts(niche, goal)          → community_plan
find_cross_language_opportunities(niche, langs)→ intl_opportunities
```
**Outputs passed forward**: `community_plan`, `intl_opportunities`

---

### Phase 7: Executive Report
```
export_research_report(niche, competitors)    → final_dossier [aggregates ALL prior outputs]
```

---

## Total Tool Calls Per Full Pipeline Run
- **Minimum** (new channel, no competitors): ~18 tool calls
- **Maximum** (existing channel + 5 competitors + 4 languages): ~35 tool calls
- **Estimated YouTube Data API quota consumed**: 150–400 units (well within daily 10,000 unit quota)
