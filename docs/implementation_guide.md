# Rental Village Social Bot: Implementation Guide

## 1. System Overview

This document provides a technical guide for the Rental Village Social Media Bot. The system is built on a containerized architecture using Docker Compose, with Sanity.io as the central data store and a suite of Python scripts for content generation.

### Key Technologies
*   **Backend:** Python 3.10
*   **Orchestration:** Docker Compose
*   **Data Management:** Sanity.io
*   **AI Content Generation:** Google Gemini API
*   **Dependencies:** See `requirements.txt` and `sanity-studio/rental-village/package.json`

## 2. System Architecture & Workflow

The system is composed of three main services defined in `docker-compose.yml`:

1.  **`sanity-studio`:** The Sanity.io Studio, which provides a web-based interface for managing all application data.
2.  **`mcp-server`:** A FastAPI server that exposes the Sanity data through a Model Context Protocol (MCP) compliant API.
3.  **`content-generation`:** A service that runs the Python scripts for generating social media content.

The general workflow is as follows:

1.  **Data Management:** All data, including the equipment catalog, content prompts, and business context, is managed in the Sanity Studio.
2.  **Content Generation:** The `suggest_content.py` script is run to generate new content ideas. This script fetches data from the `mcp-server`, uses the Gemini API to generate content, and then saves the new content back to Sanity and syncs it with Notion.
3.  **Review and Approval:** The generated content is reviewed and approved in Notion.

## 3. Core Components & Scripts

### `docker-compose.yml`

This file is the heart of the application, orchestrating all the services. It defines the build process, port mappings, volumes, and environment variables for each service.

### `src/suggest_content.py`

*   **Purpose:** The primary script for generating new content ideas.
*   **Execution:**
    ```bash
    docker-compose run --rm content-generation python src/suggest_content.py --num-ideas 5
    ```

### `src/utils/sanity_migration.py`

*   **Purpose:** A script for migrating data from the `mcp_rental_catalog_enhanced.json` file to Sanity.
*   **Execution:**
    ```bash
    docker-compose run --rm content-generation python src/utils/sanity_migration.py
    ```

## 4. Configuration & Setup

### a. Environment Variables

All API keys and configuration IDs are managed in a `.env` file in the project root. See `docs/deployment.md` for a list of the required variables.

### b. Dependencies

All dependencies are managed by Docker Compose. The Python dependencies are listed in `requirements.txt`, and the Sanity Studio dependencies are in `sanity-studio/rental-village/package.json`.

### c. Containerized Environment

The entire application is designed to be run in a containerized environment using Docker Compose.

*   **Building the Images:**
    ```bash
    docker-compose build
    ```

*   **Starting the Services:**
    ```bash
    docker-compose up -d
    ```

*   **Running a Script:**
    ```bash
    docker-compose run --rm content-generation <command>
    ```
