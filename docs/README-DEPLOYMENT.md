# Rental Village Social Media Bot - Deployment Guide

## Overview

Complete deployment guide for the Rental Village Social Media Bot system, including content generation, social automation, and all supporting services.

## System Architecture

- **Content Generation**: AI-powered content creation using Gemini/Groq APIs
- **Social Automation**: Facebook posting with cron-based scheduling (every 5 minutes)
- **Data Management**: Sanity CMS with MCP server integration
- **Health Monitoring**: HTTP endpoints and comprehensive logging

## Quick Start

### 1. Single Container Deployment

```bash
# Build the container
sudo podman build --network=host -f docker/build/Dockerfile.social -t social-automation:latest .

# Run the container
sudo podman run -d \
  --name social-automation \
  -p 8080:8080 \
  --env-file .env \
  social-automation:latest
```

### 2. Docker Compose Deployment

```bash
# Build and start all services including social automation
sudo podman-compose up -d social-automation

# Or start the entire stack
sudo podman-compose up -d
```

## Monitoring

### Check Container Status
```bash
sudo podman ps
```

### View Live Logs
```bash
sudo podman logs -f social-automation
```

### Health Check
```bash
curl http://localhost:8080/health
```

### Check Cron Status
```bash
sudo podman exec social-automation ps aux | grep cron
```

## Environment Variables Required

```
NOTION_TOKEN=your_notion_token
DATABASE_ID=your_notion_database_id
FACEBOOK_PAGE_ACCESS_TOKEN=your_facebook_page_token
FACEBOOK_PAGE_ID=your_facebook_page_id
```

## How It Works

1. **Cron Schedule**: Runs every 5 minutes (`*/5 * * * *`)
2. **Notion Monitoring**: Queries database for "Ready for Scheduling" status
3. **Facebook Posting**: 
   - Text-only posts: Direct posting
   - Image posts: Upload images then create post/album
   - Scheduled posts: Uses Facebook's scheduled publishing
4. **Status Updates**: Updates Notion status to "Scheduled" or "Posted"
5. **Logging**: All activities logged to `/app/logs/`

## Troubleshooting

### Container Won't Start
- Check environment variables are set correctly
- Verify .env file exists and has proper permissions

### Automation Not Running
- Check cron is running: `sudo podman exec social-automation ps aux | grep cron`
- View logs: `sudo podman logs social-automation`
- Check health endpoint: `curl http://localhost:8080/health`

### Facebook API Errors
- Verify page access token has correct permissions
- Check token hasn't expired
- Ensure page ID matches the token's page

### Network Issues During Build
Use host networking: `sudo podman build --network=host -f docker/build/Dockerfile.social -t social-automation:latest .`

## Production Deployment

For production use:

1. **Use docker-compose** for service orchestration
2. **Set up log rotation** for `/app/logs/`
3. **Monitor health endpoint** with external monitoring
4. **Set restart policy** to `unless-stopped`
5. **Consider using secrets** instead of .env files

## Service Management

```bash
# Stop container
sudo podman stop social-automation

# Start container
sudo podman start social-automation

# Restart container
sudo podman restart social-automation

# Remove container
sudo podman rm social-automation

# View container details
sudo podman inspect social-automation
```

## Architecture Benefits

- ✅ **Lightweight**: Cron-based scheduling vs continuous processes
- ✅ **Reliable**: Container restart policies ensure uptime
- ✅ **Scalable**: Can run multiple instances for different pages/brands
- ✅ **Maintainable**: Clear separation of concerns
- ✅ **Observable**: Health checks and comprehensive logging