---
name: executive-research-dossier
description: >-
  Synthesize competitive intelligence, viral outliers, monetization mechanics, and strategic roadmaps
  into institutional-grade Markdown or Notion research reports for clients, creators, and executives.
---

# Executive Research Dossier Skill

Use this workflow to compile comprehensive, high-stakes YouTube market research reports suitable for corporate leadership, creator management agencies, private equity investors, or enterprise clients.

## Prerequisites & Required Inputs
- `niche_or_topic`: Vertical or market segment (e.g. `'fintech creator economy'`, `'cloud computing tutorials'`).
- `competitor_handles`: 2 to 5 primary market players to benchmark.
- `output_format`: Preferred export format (`"markdown"`, `"notion"`).

---

## Step-by-Step Workflow

### Step 1: Execute Competitive Benchmarking & Outlier Mining
1. Call `compare_channels` across the key market leaders.
2. Call `find_viral_outliers` on the fastest-growing competitor to determine top view-generating angles.
3. Call `discover_niche_sponsors` to catalog active corporate spenders.
4. Call `find_content_gaps` to highlight unexploited search keywords.

### Step 2: Call the Report Exporter Engine
Call `export_research_report`:
```json
{
  "niche_or_topic": "cloud computing tutorials",
  "competitor_channels": ["@freecodecamp", "@networkchuck"],
  "format": "markdown"
}
```
**Interpretation**:
- Generates a fully formatted dossier complete with executive summary, competitor comparison matrix, monetization funnel analysis, and strategic 5-video production roadmap.

### Step 3: Enrich with Tactical Recommendations
Augment the report with specific strategic deliverables:
1. **Executive Summary**: 3-bullet bottom line on market maturity, CPM landscape, and white-space opportunity.
2. **Competitive Landscape Table**: Benchmark subscribers, 30-day views, upload velocity, and primary revenue engines.
3. **The 90-Day Go-To-Market Roadmap**:
   - Phase 1 (Days 1–30): Algorithmic binge loop establishment.
   - Phase 2 (Days 31–60): Search-intent domination (content gaps).
   - Phase 3 (Days 61–90): Sponsor monetization & digital product launch.

---

## Output Verification Checklist
- [ ] Complete Markdown structure with clean tables and callout blocks.
- [ ] Metrics verified against live YouTube Data API numbers.
- [ ] Direct commercial recommendations included (monetization, sponsorships, pricing).
- [ ] Clear 90-day action plan with milestones.
