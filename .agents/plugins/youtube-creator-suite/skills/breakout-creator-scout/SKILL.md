---
name: breakout-creator-scout
description: >-
  Scout emerging breakout YouTube channels, identify high-growth micro-influencers (1k–50k subs)
  with 3x+ engagement velocity, filter out dormant accounts, and construct influencer partnership rosters.
---

# Breakout Creator Scout Skill

Use this workflow to scout emerging high-velocity YouTube creators for agency representation, influencer marketing campaigns, talent acquisition, or competitive trend spotting before they reach mainstream scale.

## Prerequisites & Required Inputs
- `niches`: List of vertical keywords (e.g. `["ai agents", "devops tutorials", "solopreneur"]`).
- `min_subscribers`: Minimum threshold (e.g. `1000` to avoid dead/brand-new channels).
- `max_subscribers`: Maximum threshold (e.g. `50000` for cost-effective micro-influencer pricing).
- `region_code`: (Optional) Geographic target (e.g. `"US"`, `"GB"`, `"DE"`).

---

## Step-by-Step Workflow

### Step 1: Run Multi-Niche Creator Campaign Scouting
Call `scout_niche_channels`:
```json
{
  "niches": ["ai agents", "python automation"],
  "min_subscribers": 2000,
  "max_subscribers": 45000,
  "min_videos": 5,
  "region_code": "US"
}
```
**Interpretation**:
- Filters out inactive channels with $<5$ uploads.
- Evaluates subscriber counts, channel handles, custom URLs, and total video inventory.

### Step 2: Detect Breakout Velocity Outliers
Call `find_breakout_growth_channels`:
```json
{
  "niche": "ai agents",
  "max_channel_age_months": 12,
  "min_subscriber_count": 2000
}
```
**Interpretation**:
- Identifies channels created within the last 6 to 12 months that have outpaced 95% of incumbents.
- Calculates **Views-Per-Subscriber Velocity**:
  $$\text{Velocity Multiplier} = \frac{\text{Average Video Views}}{\text{Total Subscribers}}$$
  A velocity multiplier $> 1.5\times$ indicates the channel has captured algorithmic browse momentum and is being promoted outside its subscriber base.

### Step 3: Deep-Audit Potential Creator Partnerships
For top shortlisted candidates, call `audit_channel_strategy`:
- Check comment responsiveness and audience sentiment.
- Review recent sponsors or affiliate links in descriptions to verify commercial receptivity.

### Step 4: Assemble the Influencer Roster Dossier
Compile shortlisted creators into a standardized partnership table:
| Channel | Handle | Subscribers | Median Views | Velocity Score | Commercial Fit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **AgentCraft** | `@agentcraft` | 18,400 | 29,200 | $1.58\times$ (Breakout) | High (Dev tools) |

---

## Output Verification Checklist
- [ ] Only active channels with regular publishing within the last 60 days included.
- [ ] Channels meet both subscriber floor and ceiling criteria.
- [ ] Views-per-subscriber velocity calculated to eliminate inflated dead subscriber bases.
- [ ] Verified channel URLs and contact avenues documented.
