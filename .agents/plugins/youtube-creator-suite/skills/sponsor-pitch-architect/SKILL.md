---
name: sponsor-pitch-architect
description: >-
  Discover active brand sponsors in any YouTube niche, calculate data-backed rate cards
  (CPM & flat rate), design custom creative integration concepts, and generate high-converting sponsor pitch emails.
---

# Sponsor Pitch Architect Skill

Use this workflow to turn YouTube views into high-paying brand sponsorships, whether for a creator seeking sponsors or an agency pitching brands on behalf of creators.

## Prerequisites & Required Inputs
- `niche_keyword`: Target vertical (e.g. `'developer tools'`, `'cybersecurity'`, `'personal finance'`).
- `channel_id_or_handle`: (Optional) Creator's channel to customize the rate card and pitch metrics.

---

## Step-by-Step Workflow

### Step 1: Discover Active Brand Sponsors
Call `discover_niche_sponsors`:
```json
{
  "niche_keyword": "developer tools",
  "max_videos_to_scan": 25
}
```
**Interpretation**:
- Inspect the returned list of brands actively sponsoring creators in this niche.
- Extract competitor discount codes, tracking links (e.g., `brand.com/creator`), and the exact products being promoted.

### Step 2: Extract Creator Metrics & View Stability
If a creator channel is provided, call `audit_channel_strategy`:
```json
{
  "channel_id_or_handle": "@techcreator"
}
```
**Interpretation**:
- Calculate median 30-day views (excluding viral outliers) to establish a realistic guaranteed impression baseline.
- Note the audience demographic and existing affiliate relationships.

### Step 3: Compute Data-Backed Rate Card
Use the standard YouTube sponsorship formula:
$$\text{Base Flat Rate} = \left(\frac{\text{Estimated Median Views}}{1,000}\right) \times \text{Niche CPM}$$

**Niche CPM Benchmarks**:
| Niche | Standard CPM (60s Mid-Roll) | Dedicated Video CPM |
| :--- | :--- | :--- |
| **Finance / Crypto / Real Estate** | $40 – $75 | $120 – $200 |
| **B2B / Tech / Dev Tools** | $35 – $60 | $100 – $150 |
| **Health / Fitness / Productivity** | $25 – $40 | $70 – $110 |
| **Gaming / Entertainment** | $15 – $25 | $45 – $70 |

*Include package discounts (e.g., 3-video package = 15% discount).*

### Step 4: Architect 2 Custom Creative Integration Angles
Do not propose generic "read a script" ads. Brands pay 3x more for organic integrations:
1. **The Problem-Agitation-Solution Integration**: Frame the brand's tool as the natural fix to the video's central pain point.
2. **The Behind-The-Scenes Workflow Integration**: Show real-time usage of the brand's software in the creator's daily workflow.

### Step 5: Generate the High-Converting Cold Pitch Email
Draft a personalized cold outreach email targeted at the brand's Marketing Manager / Head of Creator Partnerships:
- **Subject**: Quick idea for [Brand Name] + [Creator Channel Name] (e.g., *Quick idea for Supabase + 45k backend devs*)
- **Hook**: Reference a specific recent campaign or feature launch of the brand.
- **Audience Proof**: Concrete demographic alignment and average watch duration.
- **Creative Angle**: Tease the specific video topic and integration concept.
- **Call to Action**: Low-friction next step (e.g., *"Would you be open to a 5-minute chat next Tuesday?"*).

---

## Output Verification Checklist
- [ ] At least 3 verified niche sponsors identified with active promo URLs.
- [ ] Rate card calculated with both single mid-roll and 3-video package options.
- [ ] Creative integration seamlessly ties into the creator's editorial theme.
- [ ] Pitch email is under 175 words with zero generic fluff.
