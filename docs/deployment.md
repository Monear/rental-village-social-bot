# Deployment Guide

This guide provides instructions for deploying the Rental Village Social Media Bot.

## Prerequisites

*   Docker and Docker Compose
*   A `.env` file with the necessary API keys and configuration.

## Environment Variables

Create a `.env` file in the project root with the following variables:

```
# Notion
NOTION_API_KEY=<your-notion-api-key>
NOTION_DATABASE_ID=<your-notion-database-id>

# Gemini
GEMINI_API_KEY=<your-gemini-api-key>

# Sanity
SANITY_PROJECT_ID=<your-sanity-project-id>
SANITY_DATASET=<your-sanity-dataset>
SANITY_API_TOKEN=<your-sanity-api-token>
```

## Deployment Steps

1.  **Build the Docker images:**
    ```bash
    docker-compose build
    ```

2.  **Start the services:**
    ```bash
    docker-compose up -d
    ```

This will start the Sanity Studio and MCP Server in the background.

*   **Sanity Studio:** `http://localhost:3333`
*   **MCP Server:** `http://localhost:8000`

## Running the Content Generation Service

To generate new social media content, run the `content-generation` service:

```bash
docker-compose run --rm content-generation python src/suggest_content.py --num-ideas 5
```

## Troubleshooting

*   **Environment Variables:** Ensure that the `.env` file is correctly formatted and contains all the required variables.
*   **Docker:** Make sure that Docker and Docker Compose are installed and running correctly.
*   **Ports:** Check that ports `3333` and `8000` are not already in use.
