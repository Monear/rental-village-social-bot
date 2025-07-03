# Rental Village Social Media Bot

This project is an automated social media content generation and management system for Rental Village. It leverages the Model Context Protocol (MCP) and Sanity.io to create a robust and scalable content pipeline.

## Overview

The system is composed of three primary services, orchestrated with Docker Compose:

*   **Sanity Studio:** A headless CMS used to manage all data, including the equipment catalog, content prompts, and generated social media content.
*   **MCP Server:** A FastAPI-based server that exposes the Sanity data through an MCP-compliant interface. This provides a structured and secure way for other services to access the data.
*   **Content Generation Service:** A Python-based service that uses the Gemini API to generate social media content ideas, images, and posts. It fetches data from the MCP Server, generates content, and then saves it back to Sanity and syncs it with Notion for user review.

## Getting Started

### Prerequisites

*   Docker and Docker Compose
*   A `.env` file with the necessary API keys and configuration. See `docker-compose.yml` for the required environment variables.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd rental-village-social-media-bot
    ```

2.  **Create a `.env` file:**
    Create a `.env` file in the project root and populate it with the required environment variables.

3.  **Build and run the services:**
    ```bash
    docker-compose up --build
    ```

This will build the Docker images for each service and start them in the background.

*   **Sanity Studio:** Available at `http://localhost:3333`
*   **MCP Server:** Available at `http://localhost:8000`

### Usage

To generate new social media content, run the content generation service:

```bash
docker-compose run --rm content-generation python src/suggest_content.py --num-ideas 5
```

This will generate 5 new content ideas and add them to Sanity and Notion.