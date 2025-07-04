# Rental Village Social Media Bot - Complete Documentation

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Deployment](#deployment)
- [Maintenance](#maintenance)
- [Troubleshooting](#troubleshooting)
- [Container Commands](#container-commands)

## Overview

The **Rental Village Social Media Bot** is an automated content generation system for equipment rental businesses. It combines AI-powered content creation with equipment data integration to generate engaging social media posts.

### Key Features
- **AI Content Generation**: Uses Gemini/Groq APIs for intelligent content creation
- **Equipment Integration**: Sanity CMS with organized equipment catalog
- **Image Generation**: Automated image creation with safety validation
- **Social Media Automation**: Automated Facebook posting with Notion workflow
- **MCP Server**: FastMCP framework for tool integration

### Tech Stack
- **Backend**: Python 3.11
- **Orchestration**: Docker Compose / Podman
- **CMS**: Sanity.io
- **AI APIs**: Google Gemini, Groq
- **Social Platform**: Facebook Graph API
- **Task Management**: Notion API

## Architecture

### System Components

The application consists of four main containerized services:

1. **Sanity Studio (`sanity-studio`)**: Headless CMS for data management
   - Port: 3333
   - Purpose: Equipment catalog, content prompts, business context
   
2. **MCP Server (`mcp-server`)**: FastAPI server with MCP-compliant interface
   - Port: 8000
   - Purpose: Secure data access layer for other services
   
3. **Content Generation (`content-generation`)**: AI-powered content creation
   - Purpose: Generate social media content using Gemini API
   - Storage: Saves to Sanity and syncs with Notion
   
4. **Social Automation (`social-automation`)**: Facebook posting automation
   - Port: 8080 (health check)
   - Purpose: Monitor Notion → Post to Facebook → Update status

### Data Flow

```
Sanity Studio → MCP Server → Content Generation → Notion → Social Automation → Facebook
```

### Core Workflow

1. **Data Management**: All data managed through Sanity Studio
2. **Content Generation**: `suggest_content.py` generates ideas using Gemini API
3. **Review Process**: Content reviewed and approved in Notion
4. **Social Posting**: Automated Facebook posting with status tracking

## Quick Start

### Prerequisites
- Docker/Podman and Docker Compose
- Required API keys (see Environment Variables)

### Environment Setup

Create a `.env` file in the project root:

```env
# Notion Integration
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_notion_database_id
NOTION_TOKEN=your_notion_token
DATABASE_ID=your_database_id

# AI Services
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key

# Sanity CMS
SANITY_PROJECT_ID=your_sanity_project_id
SANITY_DATASET=your_sanity_dataset
SANITY_API_TOKEN=your_sanity_api_token

# Facebook API
FACEBOOK_PAGE_ACCESS_TOKEN=your_facebook_page_token
FACEBOOK_PAGE_ID=your_facebook_page_id
```

### Starting the System

```bash
# Build all containers
docker-compose build

# Start core services
docker-compose up -d sanity-studio mcp-server

# Generate content (on-demand)
docker-compose run --rm content-generation python src/suggest_content.py --num-ideas 5

# Start social automation
docker-compose up -d social-automation
```

## Deployment

### Production Deployment

For production use:

1. **Service Orchestration**: Use docker-compose for all services
2. **Log Management**: Set up log rotation for `/app/logs/`
3. **Health Monitoring**: Monitor health endpoint at port 8080
4. **Restart Policies**: Use `unless-stopped` for critical services
5. **Security**: Use secrets management instead of .env files

### Container Build Issues (Podman)

If you encounter networking issues during builds:

```bash
# Use DNS configuration for builds
podman build --dns=8.8.8.8 --dns=8.8.4.4 -t service-name -f Dockerfile .

# Or use host networking
podman build --network=host -t service-name -f Dockerfile .
```

### Single Container Deployment

```bash
# Social automation only
podman build --network=host -f docker/build/Dockerfile.social -t social-automation:latest .
podman run -d \
  --name social-automation \
  -p 8080:8080 \
  --env-file .env \
  social-automation:latest
```

## Maintenance

### Data Backup

#### Sanity Data
```bash
# Export data
docker-compose run --rm sanity-studio sanity dataset export

# Import data
docker-compose run --rm sanity-studio sanity dataset import <path-to-data.tar.gz>
```

#### Notion Data
Notion automatically backs up data. Manual export available from workspace.

### Dependency Updates

#### Python Dependencies
```bash
# Update requirements.txt, then rebuild
docker-compose build
```

#### Sanity Studio Dependencies
```bash
# Update package.json in sanity-studio/rental-village/, then rebuild
docker-compose build
```

### Monitoring

#### Container Status
```bash
docker-compose ps
```

#### Service Logs
```bash
# View logs for specific service
docker-compose logs <service-name>

# Follow live logs
docker-compose logs -f <service-name>
```

#### Health Checks
```bash
# Social automation health
curl http://localhost:8080/health

# Check cron status
docker exec social-automation ps aux | grep cron
```

## Troubleshooting

### Common Issues

#### Container Won't Start
- Verify all environment variables are set
- Check .env file exists and has proper permissions
- Ensure required ports are not in use

#### Content Generation Issues
- Verify API keys are valid and have proper permissions
- Check Sanity connection and data availability
- Review logs for specific error messages

#### Social Automation Problems
- Verify Facebook page access token permissions
- Check token hasn't expired
- Ensure page ID matches the token's page
- Monitor cron job execution

#### Network Issues
- Use `--network=host` for builds if DNS issues occur
- Check firewall settings for required ports
- Verify container networking configuration

### Service Recovery

```bash
# Stop and restart service
docker-compose restart <service-name>

# Rebuild and restart
docker-compose build <service-name>
docker-compose up -d <service-name>

# Check service status
docker-compose ps
docker-compose logs <service-name>
```

## Container Commands

### Building Services
```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build <service-name>
```

### Managing Services
```bash
# Start all services in background
docker-compose up -d

# Start specific service
docker-compose up -d <service-name>

# Stop all services
docker-compose down

# Stop specific service
docker-compose stop <service-name>
```

### Running Commands
```bash
# Run one-off command
docker-compose run --rm <service-name> <command>

# Examples
docker-compose run --rm content-generation python src/suggest_content.py --num-ideas 3
docker-compose run --rm sanity-studio sanity dataset export
```

### Debugging
```bash
# View logs
docker-compose logs <service-name>

# Follow live logs
docker-compose logs -f <service-name>

# Execute command in running container
docker-compose exec <service-name> <command>

# Open shell in running container
docker-compose exec <service-name> /bin/bash
```

## Key Files

- `docker-compose.yml`: Service orchestration
- `src/suggest_content.py`: Main content generation engine
- `src/social_automation/`: Facebook automation modules
- `src/utils/sanity_helpers.py`: Equipment data management
- `src/utils/notion_helpers.py`: Notion integration
- `sanity-studio/rental-village/`: Sanity CMS configuration

## Support

For issues and questions:
- Check logs first: `docker-compose logs <service-name>`
- Review environment variable configuration
- Verify API key permissions and expiration
- Check networking and firewall settings