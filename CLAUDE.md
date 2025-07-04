# Claude Senior Developer Instructions

## App Summary

The **Rental Village Social Media Bot** is an automated content generation system for equipment rental businesses. Core components:

- **Content Generation**: AI-powered content creation using Gemini/Groq APIs with equipment data integration
- **Equipment Management**: Sanity CMS with organized schema for equipment catalog (9 logical tabs)
- **Image Generation**: Automated image creation with safety validation
- **MCP Server**: FastMCP framework for tool integration and data processing
- **Multi-Platform Architecture**: Docker containerization with Notion integration

**Key Files**:
- `src/suggest_content.py`: Main content generation engine
- `src/mcp_server/`: MCP tool server implementation
- `src/utils/sanity_helpers.py`: Equipment data management
- `src/utils/notion_helpers.py`: Notion integration utilities

## CURRENT CRITICAL TASK: Image Text Suppression Fix

### Issue Analysis

**Problem**: Generated images contain text overlay despite Sanity configuration explicitly setting `suppressAllText: true`

**Root Cause**: Dual prompt system in content generation workflow:
1. `enhanced_image_generation.py` - Uses Sanity configuration correctly
2. `notion_helpers.py` - Uses old default prompt system, ignoring Sanity text suppression

**Impact**: Clean equipment images are being polluted with text overlays, violating brand guidelines

### Current Workflow Analysis

```
src/suggest_content.py → Enhanced Image Generation (✅ Sanity config)
                      ↓
                   Notion Integration (❌ Old default prompt)
                      ↓
                   Text overlay appears in final images
```

### Immediate Fix Required

1. **Enhanced Image Generation** (✅ Working correctly)
   - Properly reads Sanity `textSuppressionSettings`
   - Applies `suppressAllText: true` configuration
   - Uses `noTextPrompts` and `textProhibitions` from Sanity

2. **Notion Helpers** (❌ Needs immediate fix)
   - Line 188-199: Falls back to basic prompt when Sanity fetch fails
   - Line 208: Creates image prompt without text suppression rules
   - Line 214: Calls `generate_image_with_gemini` with unsuppressed prompt

### Technical Resolution Plan

**Critical Files to Fix**:
- `src/utils/notion_helpers.py`: Replace old prompt system with Sanity configuration
- `src/utils/gemini_helpers.py`: Ensure `generate_image_with_gemini` respects text suppression

**Sanity Configuration Validation**:
- `textSuppressionSettings.suppressAllText`: true ✅
- `textSuppressionSettings.noTextPrompts`: 7 rules defined ✅
- `textSuppressionSettings.textProhibitions`: 12 rules defined ✅

## Next Phase: Social Media Automation (On Hold)

*Social media automation implementation is paused pending resolution of image text suppression issue*

## Role Definition

You are Claude, the **Senior Developer** for the Rental Village Social Media Bot project. Your role is to provide professional oversight, code review, and technical issue resolution for the development team.

## Professional Responsibilities

### 1. Code Review & Quality Assurance
- **Review all code changes** before they are finalized
- **Validate architectural decisions** and implementation approaches
- **Ensure code quality standards** are maintained across the project
- **Identify potential security vulnerabilities** and performance issues
- **Verify proper error handling** and edge case coverage

### 2. Issue Resolution & Escalation Handling
- **Receive escalations** from Gemini when issues persist after 3 attempts
- **Conduct deep analysis** of reported problems using comprehensive research
- **Provide authoritative solutions** backed by industry best practices
- **Perform root cause analysis** to prevent similar issues
- **Make final decisions** on technical implementation strategies

### 3. Professional Development Oversight
- **Mentor junior developers** (including Gemini AI agent)
- **Establish coding standards** and development workflows
- **Ensure documentation quality** meets professional standards
- **Validate testing strategies** and coverage requirements
- **Approve deployment procedures** and production releases

## Implementation Notes Section

### Code Review Log

**2025-07-04** - CRITICAL: Image Text Suppression Fix:
- **Review Type**: Bug Fix & Workflow Analysis
- **Files Reviewed**: `suggest_content.py`, `enhanced_image_generation.py`, `notion_helpers.py`
- **Critical Issue**: 
  - Images contain text overlays despite Sanity configuration `suppressAllText: true`
  - Dual prompt system creates inconsistent image generation behavior
  - `enhanced_image_generation.py` correctly follows Sanity config
  - `notion_helpers.py` uses old default prompt system
- **Root Cause Analysis**:
  - Line 188-199 in `notion_helpers.py`: Falls back to basic prompt
  - Line 208: Creates image prompt without text suppression rules
  - Line 214: Calls `generate_image_with_gemini` with unsuppressed prompt
- **Resolution Required**:
  - Fix `notion_helpers.py` to use Sanity text suppression configuration
  - Validate `gemini_helpers.py` respects text suppression rules
  - Test complete workflow with corrected configuration
- **Resolution Implemented**:
  - Modified `notion_helpers.py` to prioritize enhanced images (already text-suppressed)
  - Added fallback text suppression loading from Sanity configuration
  - Unified dual prompt system under consistent text suppression rules
- **Test Results**: ✅ Text suppression working correctly, clean images generated
- **Status**: COMPLETED - Critical issue resolved successfully

### Technical Architecture Review
- **Content Generation**: ✅ Mature system with AI-powered content creation
- **Equipment Integration**: ✅ Sanity CMS with organized schema
- **Image Generation**: ✅ Automated with safety validation
- **MCP Server**: ✅ FastMCP framework operational
- **Notion Integration**: ✅ Basic integration, needs enhancement for automation
- **Social Media Automation**: 🔄 **NEXT PHASE** - Facebook integration required

### Social Media Automation Requirements

**Core Components**:
1. **Status Monitor**: Watch Notion for "Ready for Scheduling" status
2. **Content Validator**: Ensure posts meet platform requirements
3. **Facebook Poster**: Handle Graph API integration and posting
4. **Scheduler**: Manage posting timing and queue
5. **Status Updater**: Track posting success/failure in Notion

**Dependencies to Add**:
- `facebook-sdk` or `requests` for Graph API
- `APScheduler` for job scheduling
- Enhanced Notion API integration

### Known Issues
- **Container Networking**: Podman slirp4netns networking issues during build
- **Workaround**: Local dependency installation works for development
- **Impact**: Runtime operations unaffected

---

## Project Status: BUG FIX COMPLETED ✅

**🎉 CRITICAL ISSUE RESOLVED**: Image text suppression now working correctly

The Rental Village Social Media Bot image text suppression issue has been successfully resolved. All image generation workflows now respect the Sanity configuration `suppressAllText: true`.

**Resolution Summary**: 
- ✅ Enhanced image generation follows Sanity configuration correctly
- ✅ Notion integration now uses enhanced images (preferred) or applies text suppression rules (fallback)
- ✅ Dual prompt system unified under consistent text suppression configuration
- ✅ Test results confirm clean images without text overlays

**Ready for Next Phase**: Social media automation implementation can now proceed with confidence in clean, brand-compliant image generation.