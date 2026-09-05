---
name: algorithmic-publishing-scheduler
description: >-
  Analyze competitor upload timings, determine low-competition Sweet Spot windows,
  balance Shorts-to-longform publishing ratios, and build a 30-day algorithmic master content calendar.
---

# Algorithmic Publishing Scheduler Skill

Use this workflow to establish an optimal, data-backed publishing cadence that maximizes Day 1 algorithmic velocity, avoids Shorts watch-time cannibalization, and primes subscriber feeds.

## Prerequisites & Required Inputs
- `niche_or_channel`: Topic keyword (e.g. `'ai automation'`, `'personal finance'`) or creator handle.
- `timezone_offset_hours`: Creator's local timezone offset from UTC (e.g. `-5` for EST, `+1` for CET).
- `channel_handle`: (Optional) Creator handle to audit their current Shorts-to-longform ratio.

---

## Step-by-Step Workflow

### Step 1: Discover the Competitor Upload Heatmap
Call `analyze_optimal_upload_time`:
```json
{
  "niche_or_channel": "ai automation",
  "sample_size": 30,
  "timezone_offset_hours": -5
}
```
**Interpretation**:
- Identify peak upload days (when competitors flood the feed).
- Locate the **Sweet Spot Window**: 1 to 2 hours before the target audience's peak browsing hours, while competitor publishing volume is low.
- Target the algorithmic indexing lag: Upload videos as Unlisted 2–4 hours before going Public so YouTube can complete 4K processing, speech-to-text indexing, and automatic copyright checks.

### Step 2: Audit Shorts vs. Long-Form Cadence Balance
If a creator handle is provided, call `analyze_shorts_to_longform_ratio`:
```json
{
  "channel_id_or_handle": "@techcreator",
  "sample_videos": 25
}
```
**Interpretation**:
- If Shorts-to-longform ratio is `> 3.0:1` and Longform average views are lagging, the channel is suffering from audience cannibalization.
- Adjust the cadence to the **Golden Mix**: 1 Long-Form Video : 2–3 Supporting Shorts (acting as teasers with Related Video links).

### Step 3: Plan Community Tab Priming Sequences
Call `analyze_community_posts`:
```json
{
  "niche_or_channel": "ai automation",
  "target_goal": "growth"
}
```
**Interpretation**:
- YouTube pushes Community Tab polls into the home feeds of non-subscribers.
- Schedule polls 48 hours prior to the main upload to re-awaken latent subscribers and test topic interest.

### Step 4: Construct the 30-Day Master Editorial Calendar
Assemble a weekly recurring sprint:
- **Tuesday 11:00 AM EST**: Community Tab Interactive Poll (Topic validation / curiosity trigger)
- **Thursday 2:00 PM EST**: Main Long-Form Video Release (Engineered hook & binge playlist card)
- **Friday 12:00 PM EST**: Community Tab Pinned Discussion / Free Resource Drop
- **Saturday 10:00 AM EST**: Cutout Short #1 (Highlight moment linking to Long-Form)
- **Monday 5:00 PM EST**: Cutout Short #2 (Controversial takeaway / debate hook)

---

## Output Verification Checklist
- [ ] Upload windows calculated in creator's local timezone.
- [ ] 2–4 hour pre-processing unlisted window factored into the schedule.
- [ ] Shorts-to-longform publishing ratio calibrated to prevent audience dilution.
- [ ] Community tab touchpoints scheduled between video releases.
