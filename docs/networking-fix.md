# Podman Networking Fix for Container Builds

## Problem
Container builds fail during `npm install` with DNS resolution errors due to slirp4netns networking issues.

## Root Cause
- **DNS Resolution Failures**: slirp4netns fails to resolve external DNS queries during builds
- **Network Connectivity Issues**: Known issue with Podman 4.4.3+ affecting npm/yarn operations
- **slirp4netns Limitations**: Default networking backend has compatibility issues with package managers

## Solutions

### Solution 1: DNS Configuration (Recommended)
Use `--dns` flags during container builds to fix DNS resolution.

### Solution 2: Pre-install Dependencies (Fallback)
Install dependencies locally before building containers.

## Usage

### Method 1: DNS Configuration Build
```bash
./scripts/build-containers.sh
```

### Method 2: Pre-install Dependencies Build
```bash
./build-containers-minimal.sh
```

### Manual Build with DNS
```bash
# Studio container
podman build --dns=8.8.8.8 --dns=8.8.4.4 -t rental-village-studio -f docker/build/Dockerfile.studio .

# MCP Server container  
podman build --dns=8.8.8.8 --dns=8.8.4.4 -t rental-village-mcp -f docker/build/Dockerfile.mcp .

# Content Generation container
podman build --dns=8.8.8.8 --dns=8.8.4.4 -t rental-village-content -f docker/build/Dockerfile.content .
```

### Run Containers
```bash
# Use normal networking for runtime (slirp4netns works fine for running containers)
podman-compose up -d
```

## Key Points
1. **Build-time networking**: Use `--network host` for builds
2. **Runtime networking**: Use default slirp4netns for running containers
3. **DNS resolution**: Host network bypasses container DNS issues
4. **Package managers**: npm/yarn work correctly with host networking

## Alternative Solutions
If `--network host` doesn't work:
1. Install aardvark-dns and podman-dnsname packages
2. Use pasta networking backend instead of slirp4netns
3. Configure custom DNS servers in containers.conf

## Files Modified
- `Dockerfile.studio`: Optimized for proper dependency installation
- `build-containers.sh`: Automated build script with network host flag
- `docs/networking-fix.md`: This documentation