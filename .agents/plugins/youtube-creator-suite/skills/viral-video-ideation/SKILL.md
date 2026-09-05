---
name: viral-video-ideation
description: >-
  Discover underserved content gaps, simulate title CTR with psychological triggers,
  generate counter-positioned thumbnail concepts, and classify search vs. browse traffic potential.
---

# Viral Video Ideation & Packaging Skill

Use this workflow to transform a raw topic or video idea into a high-CTR, algorithm-optimized concept before any filming or scripting begins.

## Procedure

### 1. Detect Content Gaps in the Niche
Call `find_content_gaps`:
- Pass `niche_or_topic` (e.g. `'personal finance'`, `'python web scraping'`).
- Identify ranking videos that are over 2 years old or low resolution. These represent keywords with high viewer intent where modern content can easily outrank incumbents.

### 2. Classify Traffic Potential (Search vs. Browse)
Call `classify_traffic_potential`:
- Pass candidate topics or draft titles.
- Determine whether the video targets **Evergreen Search** (steady multi-year utility, higher RPM) or **Algorithmic Browse** (fast velocity, curiosity-driven).
- Adapt the title and packaging based on the longevity and traffic category.

### 3. Simulate and Optimize Title CTR
Call `simulate_title_ctr`:
- Pass 3 to 5 candidate titles for the chosen topic.
- Evaluate the candidates against psychological triggers (Curiosity Gap, High Stakes, Specificity, Contrast, Speed to Outcome).
- Select the winning title and refine based on the algorithmic grading score.

### 4. Engineer Counter-Positioning Thumbnails
Call `generate_thumbnail_concepts`:
- Pass the winning `video_title` and `niche_context`.
- Review the analyzed competitor thumbnails to ensure the new concepts stand out visually in the feed.
- Provide 3 distinct concepts:
  - Concept A: Visual Metaphor / Shocking Contrast
  - Concept B: High Emotion Human Element
  - Concept C: Minimalist Bold Statement
- Include exact Midjourney / DALL-E image generation prompts.

### 5. Final Packaging Checklist
Deliver the final validated package:
- Target Traffic Type: Evergreen Search or Browse Spike.
- Selected Title (Graded CTR > 80/100).
- Recommended Thumbnail Visual Concept & Overlay Text (under 4 words).
- Midjourney / DALL-E prompt for thumbnail asset generation.
