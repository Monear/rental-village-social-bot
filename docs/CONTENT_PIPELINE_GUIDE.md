# Content Pipeline Guide

> How the AI-powered marketing automation system works in practice

## Overview: The Real Workflow

**Key Insight:** This system's strength is **generating large volumes of content quickly**. AI handles the 0→1 phase (getting something on the page), then humans do quick polish.

**Total Time:** ~1 hour for 10 posts (vs. 20-40 hours manual)

---

## The Pipeline

### 1. AI Generation (10-15 minutes for 10 posts)

**What happens:**
- System analyzes equipment catalog from Sanity CMS
- Gemini AI generates complete posts with:
  - Headlines
  - Body text (platform-optimized)
  - Hashtags
  - Equipment details
- Content saved to Sanity + synced to Notion

**Command:**
```bash
docker-compose run --rm content-generation python src/suggest_content.py --num-ideas 10
```

**Output:**
- 10 complete content drafts in Notion
- Each with status: "To Review"
- Ready for human polish

**Files:**
- `src/suggest_content.py` - Main generator
- `src/utils/content_strategy_engine.py` - Strategic planning
- `src/utils/gemini_helpers.py` - AI text generation

---

### 2. Human Review & Polish (30-60 minutes)

**What happens in Notion:**
1. Marketing team opens Notion database
2. Reviews AI-generated text
3. Makes quick edits:
   - Adjust tone/wording
   - Add specific details
   - Refine CTAs
4. Adds images:
   - Find stock photos
   - Create graphics in Canva
   - Upload to Notion entry
5. Sets status: "To Review" → "Scheduled"
6. Sets publish date/time

**Notion Workflow:**
```
Status Flow:
📝 To Review → ✅ Approved → 📅 Scheduled → ✅ Published
```

**Why it's fast:**
- AI already wrote the draft (hardest part done)
- Just polish, don't create from scratch
- Batch review 10 posts in one session
- Images are the main time investment

---

### 3. Automated Publishing (< 1 minute per post)

**What happens:**
- Scheduler runs every 15 minutes
- Checks Notion for posts with:
  - Status = "Scheduled"
  - Publish time ≤ now
- Uploads image to Facebook
- Creates post with text
- Updates Notion: "Scheduled" → "Published"

**Files:**
- `src/social_automation/scheduler.py` - Main orchestrator
- `src/social_automation/facebook_poster.py` - Facebook API

**Result:** Zero manual publishing effort

---

## Time Breakdown

### Traditional Manual Process
```
Brainstorming: 4 hrs
Writing copy: 10 hrs (1 hr × 10 posts)
Finding/creating images: 10 hrs (1 hr × 10 posts)
Scheduling/publishing: 3 hrs

Total: ~27 hours for 10 posts
```

### AI-Powered Process
```
AI Generation: 10-15 min
Human Review & Polish: 30-60 min
  - Text edits: 10-15 min (1-2 min per post)
  - Image creation: 20-45 min (2-5 min per post in Canva)
Auto-Publishing: 0 min (automatic)

Total: ~1 hour for 10 posts
```

**Time Reduction: 96%** (27 hrs → 1 hr)

---

## Real Workflow Example

### Monday Morning: Content Generation

**9:00 AM - Run AI Generation:**
```bash
docker-compose run --rm content-generation python src/suggest_content.py --num-ideas 10
```

**9:15 AM - Results:**
- 10 content ideas in Notion
- Each with complete text, hashtags, equipment details
- Status: "To Review"

---

### Monday Afternoon: Human Polish

**2:00 PM - Marketing Team Reviews:**

**Post 1: "Spring Lawn Care Tips"**
- ✅ AI text looks good, minor tone adjustment
- 🎨 Create graphic in Canva (5 min): lawn equipment + seasonal colors
- ✅ Upload image, set status to "Scheduled" for Wednesday 10 AM

**Post 2: "Equipment Spotlight: Rototiller"**
- ✏️ Edit: Add specific model details
- 🎨 Find stock photo of rototiller (2 min)
- ✅ Set status to "Scheduled" for Friday 2 PM

**Post 3-10: Similar process...**

**3:00 PM - Done:**
- 10 posts reviewed and scheduled
- Total time: 1 hour
- Posts will auto-publish over next 2 weeks

---

### Auto-Publishing (Ongoing)

**Wednesday 10:00 AM:**
- Scheduler detects "Spring Lawn Care Tips" ready to publish
- Uploads image to Facebook
- Creates post with AI-generated text (with human edits)
- Updates Notion: "Scheduled" → "Published"
- Total time: Automatic

---

## Key Benefits

### Speed: 0→1 Phase Automated
- **AI writes the draft** - Hardest part done in minutes
- **Humans polish** - 1-2 minutes of text edits per post
- **Images are main work** - But Canva makes it fast

### Consistency
- AI maintains brand voice
- Strategic content planning (equipment focus, seasonal themes)
- Platform optimization (character limits, hashtags)

### Scalability
- Generate 50 posts as easily as 10
- Same 10-15 minutes for AI generation
- Human time scales linearly (but still 10x faster than manual)

---

## Common Workflows

### Weekly Content Batch
```bash
# Monday: Generate week's content (7 posts)
docker-compose run --rm content-generation python src/suggest_content.py --num-ideas 7

# Result: 7 drafts in Notion, ready for review
# Time: 10 minutes
```

**Human work:** 30-45 min to polish all 7 posts

---

### Monthly Campaign
```bash
# Generate 20 posts for holiday season
docker-compose run --rm content-generation python src/suggest_content.py --num-ideas 20

# Result: 20 drafts covering equipment categories, seasonal themes
# Time: 15 minutes
```

**Human work:** 1-2 hours to review and add images for all 20

---

## What Makes This Work

### 1. Strategic Content Planning
The AI doesn't generate random content. It uses:
- Equipment catalog (what's available to rent)
- Content pillars (educational, promotional, seasonal, safety)
- Seasonal context (spring lawn care, winter equipment)
- Business strategy (high-margin equipment, underutilized items)

**Result:** Every post has business rationale

---

### 2. Platform Optimization
AI knows platform specs:
- Facebook: Longer text, engagement-focused
- Instagram: Shorter, hashtag-heavy
- Blog: Long-form, SEO-optimized

**Result:** No manual reformatting

---

### 3. Notion as Control Center
- **Single source of truth** for all content
- **Status tracking** (To Review → Scheduled → Published)
- **Team collaboration** (comments, assignments)
- **Scheduling** (set publish dates)

**Result:** Organized workflow, audit trail

---

## Troubleshooting

### AI Text Needs Heavy Editing
**Symptom:** AI-generated text requires major rewrites

**Solution:**
- Update prompts in Sanity CMS (add examples, adjust tone)
- Provide more business context in equipment catalog
- Check that Sanity CMS is accessible and data is up to date

**Files to adjust:**
- Sanity CMS: Prompt templates
- `src/utils/gemini_helpers.py`: System prompts

---

### Publishing Failures
**Symptom:** Posts not publishing to Facebook

**Solution:**
1. Check Facebook token: `curl "https://graph.facebook.com/me?access_token=TOKEN"`
2. Review logs: `docker-compose logs social-automation`
3. Verify Notion status is "Scheduled" (not "Approved")

---

### Content Quality Issues
**Symptom:** AI content is off-brand or generic

**Fix:** The system learns from examples. Add better examples to Sanity CMS:
- Brand voice guidelines
- Sample posts (high-quality)
- Equipment descriptions (detailed)

---

## Next Steps

Want to dive deeper?

- **[README.md](../README.md)** - System overview and setup
- **[CLAUDE.md](../CLAUDE.md)** - Development guide
- **[assets/screenshots/](../assets/screenshots/)** - See actual Notion workflow, AI output, published posts

**Ready to run?** Follow installation steps in README.md
