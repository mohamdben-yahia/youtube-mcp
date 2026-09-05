---
name: international-arbitrage-expander
description: >-
  Identify high-performing English YouTube videos with massive search demand but zero competition
  in non-English international markets, generate localized titles/tags, and design multi-language dubbing expansion plans.
---

# International Arbitrage Expander Skill

Use this workflow to exploit YouTube's massive geographic content gaps by identifying proven English video concepts and localizing them into high-GDP non-English languages (Spanish, Portuguese, German, French, Japanese).

## Prerequisites & Required Inputs
- `topic_or_niche`: Topic keyword (e.g. `'personal finance'`, `'home workout'`, `'python automation'`).
- `target_languages`: List of ISO 639-1 language codes (e.g. `["es", "pt", "de", "fr"]`).
- `source_video_id`: (Optional) Existing English video to evaluate for localization.

---

## Step-by-Step Workflow

### Step 1: Scan Cross-Language Search Gaps
Call `find_cross_language_opportunities`:
```json
{
  "topic_or_niche": "python automation tutorial",
  "target_languages": ["es", "pt", "de", "fr"]
}
```
**Interpretation**:
- Evaluates the **Language Arbitrage Ratio**:
  $$\text{Arbitrage Ratio} = \frac{\text{English Market Views}}{\text{Localized Native Market Competition}}$$
- Flag topics with Arbitrage Ratio $> 5.0\times$. This signals that Spanish or Portuguese viewers are actively searching for the topic but are forced to watch English videos due to a lack of high-quality native content.

### Step 2: Extract Proven Script Blueprint
If a successful English video is available, call `get_video_transcript`:
```json
{
  "video_id": "vid_english_hit",
  "format": "timestamped"
}
```
**Interpretation**:
- Capture the pacing and structural beats that drove millions of views in English.
- Identify cultural references that require localization (e.g., replacing 401(k) with local pension equivalents or US bank names with local banks).

### Step 3: Localize Titles & Keywords
Call `generate_seo_metadata_pack`:
- Generate native localized title formulas using local psychological triggers.
- For Spanish (`es`): Focus on direct outcomes (*"Cómo automatizar..."* or *"Deja de perder el tiempo..."*).
- For German (`de`): Emphasize precision and efficiency (*"Schritt für Schritt Anleitung..."*).

### Step 4: Multi-Language Audio Track vs. Dedicated Channel Strategy
Decide the deployment method:
1. **YouTube Multi-Language Audio (MLA)**:
   - *Best for*: Established channels with $>100\text{k}$ subscribers.
   - Allows uploading Spanish/Portuguese audio tracks directly onto the original video file. All global views aggregate onto the same video, boosting platform-wide recommendation.
2. **Dedicated Localized Satellite Channel** (e.g., *MrBeast en Español* style):
   - *Best for*: Highly visual tutorials, voice-over animations, or niche-specific affiliate products tailored to a specific country.

---

## Output Verification Checklist
- [ ] At least 3 target languages evaluated with comparative view benchmarks.
- [ ] Cultural substitutions identified for region-specific concepts.
- [ ] Native localized titles, descriptions, and tags generated.
- [ ] Strategic recommendation: Multi-Language Audio vs. Satellite Channel.
