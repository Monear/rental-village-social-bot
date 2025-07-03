# Maintenance Guide

This guide provides instructions for maintaining the Rental Village Social Media Bot.

## Data Backup and Recovery

### Sanity

Sanity.io provides automatic backups of your data. You can also export your data manually from the Sanity Studio or using the Sanity CLI.

**Exporting Data:**

```bash
docker-compose run --rm sanity-studio sanity dataset export
```

**Importing Data:**

```bash
docker-compose run --rm sanity-studio sanity dataset import <path-to-your-data.tar.gz>
```

### Notion

Notion automatically backs up your data. You can also export your data manually from the Notion workspace.

## Updating Dependencies

### Python Dependencies

To update the Python dependencies, modify the `requirements.txt` file and then rebuild the Docker images:

```bash
docker-compose build
```

### Sanity Studio Dependencies

To update the Sanity Studio dependencies, modify the `package.json` file in the `sanity-studio/rental-village` directory and then rebuild the Docker images:

```bash
docker-compose build
```

## Monitoring

### Docker Containers

You can monitor the status of the Docker containers using the following command:

```bash
docker-compose ps
```

### Logs

You can view the logs for each service using the following command:

```bash
docker-compose logs <service-name>
```

For example, to view the logs for the MCP Server:

```bash
docker-compose logs mcp-server
```
