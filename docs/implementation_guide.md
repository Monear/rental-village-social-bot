# Rental Village Social Bot: Implementation Guide

## 1. System Overview

This document provides a technical overview of the Rental Village Social Media Automation system. The system is a collection of Python scripts designed to automate the social media content lifecycle, from ideation to performance reporting.

The core philosophy is **human-in-the-loop automation**. AI is used to handle repetitive and data-intensive tasks like generating content ideas and finding image assets, while humans are responsible for final approval, creative production, and strategic direction.

The entire workflow is orchestrated through a central **Notion Database**, which acts as the single source of truth for all content.

### Key Technologies
*   **Backend:** Python 3.10
*   **Orchestration Hub:** Notion API
*   **AI Content Generation:** Google Gemini API
*   **Image Asset Sourcing:** Pexels API
*   **Environment:** Docker / Podman for containerization
*   **Dependencies:** `notion-client`, `google-generativeai`, `pexels-api-py`, `python-dotenv`

## 2. System Architecture & Workflow

The system follows the workflow outlined in `strategy_documents/automation_plan.md`.

1.  **AI Ideation (`suggest_content.py`):** A user runs this script, optionally providing input text. The script uses the Gemini API to generate a specified number of content ideas (title, body, keywords) based on the rules in `strategy_documents/content_guidelines.md`.
2.  **Image Search (`suggest_content.py`):** For each idea, the script uses the generated keywords to search the Pexels API for relevant, high-quality stock photos.
3.  **Database Population (`suggest_content.py`):** The script creates a new page in the Notion database for each idea. It populates the `Name` (title), `Copy` (body), `Status` ("AI Suggestion"), `Content Pillar`, and `Post Date` fields. A list of URLs for the found images is placed in the `Suggested Images` field.
4.  **Human Review (Manual):** The social media manager reviews the "AI Suggestion" items in Notion. They select the best image, refine the copy, and move the status to "Approved for Production".
5.  **Posting (Future Work - `main.py`):** A script will query for "Scheduled" posts and publish them to the relevant social media platforms.
6.  **Performance Tracking (Future Work - `track_performance.py`):** A script will query for "Posted" content and use social media APIs to fetch performance metrics, updating the corresponding fields in Notion.
7.  **Reporting (`generate_report.py`):** A script aggregates performance data from Notion for a given month and generates a draft performance report in Markdown.

## 3. Core Components & Scripts

All scripts are located in the `src/` directory.

### `suggest_content.py`
*   **Purpose:** The primary script for generating new content ideas.
*   **Execution:** `python src/suggest_content.py`
*   **Arguments:**
    *   `--num-ideas [INTEGER]`: Specifies the number of ideas to generate (default: 3).
    *   `--input-text "[STRING]"`: Optional text to provide the AI with specific inspiration.
*   **Functionality:**
    1.  Reads the `content_guidelines.md` to create a prompt for the Gemini API.
    2.  Generates a JSON object containing ideas, each with a title, body, pillar, and image keywords.
    3.  Uses the keywords to search the Pexels API for image URLs.
    4.  Creates a new page in the Notion database for each idea, populating it with the generated content and a list of suggested image URLs.

### `track_performance.py`
*   **Purpose:** To automatically update Notion with social media engagement metrics.
*   **Status:** **Placeholder.** Currently uses randomly generated data.
*   **Functionality:**
    1.  Queries the Notion database for posts with a "Posted" status that have not yet been updated.
    2.  (Placeholder) Simulates calling Facebook/Instagram APIs to get likes, comments, and reach.
    3.  Updates the Notion page with these metrics.

### `generate_report.py`
*   **Purpose:** To create a monthly performance summary.
*   **Functionality:**
    1.  Queries the Notion database for all posts within the current month that have performance data.
    2.  Aggregates total likes, comments, and reach.
    3.  Generates a Markdown file (`monthly_report_YYYY-MM.md`) in the `strategy_documents` directory with a summary and a list of top-performing posts.

### `main.py`
*   **Purpose:** To post approved content to social media platforms.
*   **Status:** **Placeholder.** This script contains the basic logic but does not yet have a real implementation for posting to social media APIs.

### `utils/check_notion_db.py`
*   **Purpose:** A utility script for developers to inspect the schema of the connected Notion database.
*   **Execution:** `python src/utils/check_notion_db.py`
*   **Functionality:** Prints a formatted list of all properties in the database, including their name, type, and options (for `select` properties). This is useful for debugging property name mismatches.

## 4. Configuration & Setup

### a. Environment Variables
All API keys and configuration IDs are managed in a `.env` file in the project root. This file should **never** be committed to version control.

```
# .env file

# Notion API Credentials
NOTION_API_KEY="secret_..."
NOTION_DATABASE_ID="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Google Gemini API Key
GEMINI_API_KEY="AIza..."

# Pexels API Key
PEXELS_API_KEY="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# (Optional - for future use)
FACEBOOK_API_TOKEN="..."
INSTAGRAM_API_TOKEN="..."
```

### b. Dependencies
All required Python packages are listed in `requirements.txt`. They can be installed via pip:
`pip install -r requirements.txt`

### c. Containerized Environment
The project uses a `Dockerfile` to create a consistent and reproducible environment for running the scripts.

*   **Building the Image:**
    ```bash
    podman build -t rental-village-bot .
    ```
*   **Running a Script:** Scripts are run inside the container, with the `.env` file passed securely.
    ```bash
    # Example for suggest_content.py
    podman run --rm --env-file .env rental-village-bot python src/suggest_content.py --num-ideas 2
    ```
