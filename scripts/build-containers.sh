#!/bin/bash
# Build containers with DNS configuration to fix networking issues

set -e

echo "Building Rental Village Social Bot containers with DNS configuration..."

# Studio container
echo "Building Sanity Studio container..."
podman build --dns=8.8.8.8 --dns=8.8.4.4 -t rental-village-studio -f docker/build/Dockerfile.studio .

# MCP Server container
echo "Building MCP Server container..."
podman build --dns=8.8.8.8 --dns=8.8.4.4 -t rental-village-mcp -f docker/build/Dockerfile.mcp .

# Content Generation container
echo "Building Content Generation container..."
podman build --dns=8.8.8.8 --dns=8.8.4.4 -t rental-village-content -f docker/build/Dockerfile.content .

# Social Automation container
echo "Building Social Automation container..."
podman build --dns=8.8.8.8 --dns=8.8.4.4 -t rental-village-social -f docker/build/Dockerfile.social .

echo "All containers built successfully!"
echo "Use 'podman-compose up -d' to start the services."