# Rental Village Social Bot: Application Overview

This document provides a technical overview of the Rental Village Social Bot, a content generation system built on Sanity.io and the Model Context Protocol (MCP).

## 1. System Architecture

The application is a containerized system composed of three main services orchestrated by `docker-compose.yml`:

*   **Sanity Studio (`sanity-studio`):** A headless CMS that serves as the central hub for all data, including the equipment catalog, content prompts, generated social content, and business context. It runs on port `3333`.
*   **MCP Server (`mcp-server`):** A FastAPI server that exposes the data from Sanity through an MCP-compliant interface. This provides a structured and secure way for other services to access the data. It runs on port `8000`.
*   **Content Generation (`content-generation`):** A Python service that uses the Gemini API to generate social media content. It is not a long-running service but is instead run on-demand to perform content generation tasks.

## 2. Core Workflow: `src/suggest_content.py`

The content generation process is orchestrated by `src/suggest_content.py`. This script connects to Sanity, generates content with Gemini, and then saves the results back to Sanity and Notion.

### 2.1. Data Retrieval

The script begins by fetching all necessary data from Sanity using GROQ queries:

*   **Content Generation Prompt:** The core prompt for the Gemini API, fetched from the `contentPrompt` schema in Sanity.
*   **Social Media Best Practices:** A document containing strategic guidance for the AI, also fetched from the `contentPrompt` schema.
*   **Business Context:** General information about the business, fetched from the `businessContext` schema.
*   **Existing Notion Ideas:** A list of existing ideas from Notion is also fetched to prevent the generation of duplicate content.

### 2.2. Content Generation

The script then uses the fetched data to construct a detailed prompt for the Gemini API. The `generate_ideas_with_gemini()` function sends this prompt to the Gemini API to generate a specified number of new content ideas.

### 2.3. Data Storage

The newly generated ideas are then processed and saved:

*   **Sanity:** Each new idea is saved as a new document in the `socialContent` schema in Sanity.
*   **Notion:** The idea is also added to a Notion database for user review and approval.
*   **Image Generation:** An image is generated for each idea using the Gemini API, and the image is saved to the `generated_images/` directory.

## 3. Data Management: Sanity Studio

All data for the application is managed through the Sanity Studio. This includes:

*   **Equipment Catalog (`equipment`):** A detailed catalog of all rental equipment.
*   **Content Prompts (`contentPrompt`):** The prompts used to guide the Gemini API.
*   **Social Content (`socialContent`):** The generated social media content.
*   **Business Context (`businessContext`):** General business information.

This centralized approach to data management makes it easy to update and maintain the application's data without needing to modify any code.
