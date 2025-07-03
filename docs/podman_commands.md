# Docker Compose Commands

This document outlines common Docker Compose commands for managing the Rental Village Social Bot services.

## Building Images

To build the Docker images for all services, run the following command from the project root:

```bash
docker-compose build
```

## Starting and Stopping Services

To start all services in detached mode:

```bash
docker-compose up -d
```

To stop all services:

```bash
docker-compose down
```

## Running One-Off Commands

To run a one-off command in a service container, use `docker-compose run`. For example, to run the content generation script:

```bash
docker-compose run --rm content-generation python src/suggest_content.py --num-ideas 5
```

## Viewing Logs

To view the logs for a specific service:

```bash
docker-compose logs <service-name>
```

For example, to view the logs for the `mcp-server`:

```bash
docker-compose logs mcp-server
```
