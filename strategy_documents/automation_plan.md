# Rental Village Automation Plan (v2)

## 1. Overview

This document outlines a refined, intelligent automation plan for Rental Village's social media strategy. The workflow is designed to augment human creativity by using AI for ideation and data collection, while keeping humans in the loop for creative production and final approval. The goal is a highly efficient, data-driven content pipeline.

## 2. The Automation & Human Workflow Pipeline

This pipeline details the journey from idea to performance analysis.

**[Step 1: AI-Powered Ideation - AUTOMATED]**
*   **Action:** A Python script (`suggest_content.py`) runs monthly.
*   **Process:** It analyzes seasonal trends and a list of priority equipment to generate a list of content ideas (blog topics, social media hooks).
*   **Output:** These ideas are automatically added to the Notion Calendar with the status "AI Suggestion".

**[Step 2: Content Strategy & Approval - HUMAN EFFORT]**
*   **Action:** The Rental Village team reviews the "AI Suggestion" ideas in Notion.
*   **Process:** They approve, reject, or refine the ideas, aligning them with business goals. Approved ideas are moved to the "Approved for Production" status.

**[Step 3: Creative Production - HUMAN EFFORT]**
*   **Action:** The content creator uses the approved ideas to produce the actual assets.
*   **Process:** Following the `design_guidelines.md`, they create images and videos in Canva using pre-defined templates. The final copy is written.
*   **Output:** The finished creative assets and copy are uploaded to the corresponding entry in Notion, and the status is changed to "Ready for Scheduling".

**[Step 4: Final Vetting & Scheduling - HUMAN EFFORT]**
*   **Action:** A final review of the finished content is conducted.
*   **Process:** Once approved, the post is given a specific "Post Date" in Notion and the status is changed to "Scheduled".

**[Step 5: Content Posting - AUTOMATED]**
*   **Action:** The main Python script (`main.py`) runs daily.
*   **Process:** It queries the Notion database for all entries with the status "Scheduled" and a "Post Date" for the current day.
*   **Output:** The script posts the content and creative to the designated social media platforms and updates the status in Notion to "Posted".

**[Step 6: Performance Tracking - AUTOMATED]**
*   **Action:** A second Python script (`track_performance.py`) runs daily.
*   **Process:** It queries for posts with the "Posted" status. Using the Facebook/Instagram APIs, it fetches key performance metrics (likes, comments, shares, reach) from a few days prior.
*   **Output:** The script updates the Notion entry with these metrics, providing a complete view of performance.

**[Step 7: Reporting & Analysis - HUMAN & AI EFFORT]**
*   **Action:** A third script (`generate_report.py`) runs monthly to draft a performance report.
*   **Process:** The script aggregates all the performance data from Notion. The human team then analyzes this report to inform the strategy for the next content cycle.
*   **Output:** A draft report in Markdown and actionable insights for the next month.

## 3. Technical Stack & Scripts

*   **Notion API:** The central hub for the entire workflow.
*   **Python:** The core language for all automation scripts.
*   **Facebook & Instagram Graph APIs:** For posting content and retrieving performance data.
*   **Canva:** For creative production (manual process).
*   **GitHub Actions:** To schedule and run all Python scripts.

### Python Scripts:
*   `suggest_content.py`: Generates content ideas.
*   `main.py`: Posts scheduled content.
*   `track_performance.py`: Fetches performance metrics.
*   `generate_report.py`: Drafts monthly reports.
