# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current Priority: Bug Fixes and Feature Enhancements

This project requires focused work on several critical issues and feature additions:

### 1. CRITICAL BUG: Notion Platform Field Not Populated

**Issue**: The "Platform" field in Notion is not being populated during content creation, despite the Notion schema showing it exists with options ['Blog', 'Instagram', 'Facebook'].

**Root Cause**: Analysis shows that `src/social_automation/status_monitor.py:175-178` correctly extracts the Platform field, but the content creation flow in the main content generation pipeline doesn't populate this field when creating new Notion entries.

**Files to Fix**:
- `src/utils/notion_helpers.py` - Check `add_idea_to_notion()` function
- `src/suggest_content.py` - Main content generation flow
- Any functions that create new Notion database entries

**Investigation Commands**:
```bash
# Check current Notion database schema
python src/utils/check_notion_db.py

#activate the Virtual Environment:
source venv/bin/activate

# Test content generation and verify Platform field population
python src/suggest_content.py --num-ideas 1

# Check Notion helper functions
grep -r "Platform" src/utils/notion_helpers.py
```

### 2. FEATURE: Enhance Gemini Integration with Google Search

**Goal**: Implement Gemini `google_search` tool integration as shown in the Google AI documentation to enhance content generation with real-time search data and citations.

**Current State**: 
- `src/utils/gemini_helpers.py` has basic Gemini integration using `gemini-1.5-flash`
- No current use of `google_search` tool or grounding metadata
- No citation extraction or web search capabilities

**Implementation Requirements**:
- Add `google_search` tool to Gemini API calls
- Implement citation extraction using `grounding_metadata.grounding_supports`
- Add `add_citations()` function based on the provided example
- Update content generation prompts to leverage search data

**Reference Implementation** (from user request):
```python
def add_citations(response):
    text = response.text
    supports = response.candidates[0].grounding_metadata.grounding_supports
    chunks = response.candidates[0].grounding_metadata.grounding_chunks
    # Implementation details from https://ai.google.dev/gemini-api/docs/google-search
```

### 3. FEATURE: Image Generation Flag (Default Off)

**Issue**: Image generation is unreliable and should be optional with default disabled.

**Current State**:
- `src/utils/enhanced_image_generation.py` - Complex image generation system
- `src/utils/gemini_helpers.py` - Basic image generation functions
- Image generation runs by default during content creation

**Required Changes**:
- Add `--enable-images` flag to `src/suggest_content.py`
- Default behavior: skip image generation
- Update Docker compose commands to include flag when images needed
- Modify content generation flow to check flag before image processing

### 4. FEATURE: Google Search for Equipment Images

**Goal**: Use Google Search (via Gemini tools) to find images matching specific equipment instead of generating them.

**Benefits**:
- More accurate equipment representation
- Faster than AI generation
- Better visual quality for real equipment

**Implementation**:
- Integrate with Gemini `google_search` tool for image search
- Search for "[equipment_name] rental equipment" 
- Filter for appropriate image licenses/usage rights
- Fallback to existing image generation if search fails

## Development Environment Setup

### Container-Based Development
```bash
# Start development environment
docker-compose up -d

# Run content generation (main entry point)
docker-compose exec content-generation python src/suggest_content.py --num-ideas 1

# Test Notion database connection
docker-compose exec content-generation python src/utils/check_notion_db.py

# Run with image generation (when flag implemented)
docker-compose exec content-generation python src/suggest_content.py --num-ideas 1 --enable-images

# Check logs
docker-compose logs -f content-generation
```

### Key Development Commands
```bash
# Build all containers
sudo podman-compose build

# Run content generation service
sudo podman-compose run --rm content-generation python src/suggest_content.py

# Access Sanity Studio
# URL: http://localhost:3333

# Access MCP Server  
# URL: http://localhost:8000

# Test social automation (in VENV)
python tests/run_facebook_automation.py
```

## Architecture Overview

### Core Services
- **Sanity Studio** (localhost:3333): Headless CMS for prompt repo and generation guidelines, business information, equipment catalog and content archive
- **MCP Server** (localhost:8000): FastAPI server exposing Sanity data via Model Context Protocol
- **Content Generation**: Python service using Gemini API for content creation
- **Social Automation**: Automated posting to Facebook with Notion workflow integration

### Main Content Generation Flow
1. `src/suggest_content.py` - Main entry point for content generation
2. `src/utils/content_strategy_engine.py` - Strategic content planning
3. `src/utils/gemini_helpers.py` - Gemini API integration for text generation
4. `src/utils/enhanced_image_generation.py` - Image enhancement and generation
5. `src/utils/notion_helpers.py` - Notion integration for content management
6. `src/utils/sanity_helpers.py` - Sanity CMS integration

### Social Media Automation
- `src/social_automation/scheduler.py` - Main scheduling orchestrator
- `src/social_automation/status_monitor.py` - Notion status monitoring
- `src/social_automation/facebook_poster.py` - Facebook API integration

### Critical Files for Current Issues
- **Notion Platform Bug**: `src/utils/notion_helpers.py`, `src/suggest_content.py`
- **Gemini Search**: `src/utils/gemini_helpers.py`
- **Image Flag**: `src/suggest_content.py`, `src/utils/enhanced_image_generation.py`

## Testing Strategy

### Current Test Coverage
```bash
# Run existing tests in venv
python tests/test_gemini_helpers.py
python tests/test_general.py
python tests/test_check_notion_db.py
python tests/test_main.py
```

### Debug and Validation
```bash
# Validate Notion database schema
python src/utils/check_notion_db.py

# Test Gemini API connectivity
python tests/test_gemini_helpers.py

# Check MCP server data
curl http://localhost:8000/health
```

## Environment Variables Required

Key environment variables (see docker-compose.yml for complete list):
- `GEMINI_API_KEY` - Gemini API key for content generation
- `NOTION_TOKEN` - Notion API token
- `DATABASE_ID` - Notion database ID for content storage
- `SANITY_PROJECT_ID` - Sanity project ID
- `FACEBOOK_PAGE_ACCESS_TOKEN` - Facebook API token for posting

## Implementation Priorities

1. **HIGH**: Fix Notion Platform field population bug
2. **HIGH**: Add image generation flag (default off)  
3. **MEDIUM**: Integrate Gemini google_search tool with citations
4. **MEDIUM**: Implement Google Search for equipment images
5. **LOW**: Performance optimization and error handling improvements

## Code Quality Notes

- All development should occur in containers (no local Python environments)
- Validate Sanity data availability before using in algorithms
- Implement graceful degradation for missing data
- Add comprehensive error handling and logging
- Use environment variables for all configuration (no hardcoded values)

## Current System Status

The codebase represents a sophisticated white-label social media content generation platform with:
- ✅ Containerized architecture with Docker Compose
- ✅ Multi-service design (Sanity, MCP, Content Generation, Social Automation)
- ✅ Advanced content strategy and equipment targeting algorithms  
- ✅ Gemini 2.0 integration for text and image generation
- ✅ Notion workflow integration for content approval
- ✅ Facebook automation with scheduling
- ❌ Platform field population in Notion (BUG)
- ❌ Optional image generation (missing flag)
- ❌ Google Search integration (enhancement needed)