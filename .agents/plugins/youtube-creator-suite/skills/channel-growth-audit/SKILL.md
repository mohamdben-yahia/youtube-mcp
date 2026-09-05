---
name: channel-growth-audit
description: >-
  Audit a YouTube creator's channel strategy, Shorts-to-longform conversion ratio,
  viewer sentiment, retention dropoffs, and deliver a data-backed 90-day turnaround plan.
---

# Channel Growth Audit Skill

Use this workflow to conduct a comprehensive diagnostic audit of any YouTube channel, identifying performance bottlenecks, audience fatigue points, and algorithmic optimization opportunities.

## Procedure

### 1. Reverse-Engineer Channel Cadence & Strategy
Call `audit_channel_strategy`:
- Pass `channel_id_or_handle` (e.g. `'@mkbhd'` or `'UC...'`).
- Review the channel's upload cadence, title formulas, opening 60-second hook transcript analysis, and existing monetization funnel links.

### 2. Identify Viral Outliers & Proof of Concept
Call `find_viral_outliers`:
- Pass `channel_id_or_handle` and `outlier_threshold=2.0`.
- Identify topics that achieved 2.5x to 10x the channel's median view count. These reveal what the broader algorithm actually wants from this creator.

### 3. Diagnose Shorts vs. Long-Form Balance
Call `analyze_shorts_to_longform_ratio`:
- Evaluate whether Shorts are driving subscribers who fail to watch long-form content (cannibalization).
- Note view disparities and the recommended publishing cadence.

### 4. Mine Audience Sentiment & Unmet Needs
Call `analyze_audience_sentiment`:
- Pass top-performing or recent video IDs.
- Extract recurring viewer questions, technical confusions, and content requests to build the upcoming content calendar.

### 5. Evaluate Pacing & Retention Dropoffs
Call `predict_retention_dropoffs`:
- Pass the video URL or script of an underperforming video to pinpoint flat monologue zones (>45 seconds without pattern interrupts) and WPM pacing issues.

### 6. Deliver the Audit Report
Synthesize the findings into an actionable 90-day growth plan:
1. **Algorithmic Diagnosis**: Identify if views are limited by low CTR, poor 60s retention, or Shorts cannibalization.
2. **Double-Down Topics**: The 3 themes proven by viral outliers.
3. **Pacing Fixes**: Pattern interrupt guidelines for future videos.
4. **Publishing Cadence**: Specific day/hour recommendations using `analyze_optimal_upload_time`.
