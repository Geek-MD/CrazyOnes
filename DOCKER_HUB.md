# Publishing to Docker Hub

This guide explains how to build and publish CrazyOnes Docker images to Docker Hub.

## Prerequisites

1. **Docker Hub Account**: Create a free account at [hub.docker.com](https://hub.docker.com)
2. **GitHub Repository Secrets**: Required for automated builds
   - `DOCKERHUB_USERNAME`: Your Docker Hub username
   - `DOCKERHUB_TOKEN`: Docker Hub access token (create at hub.docker.com → Account Settings → Security)

## Automated Publishing (GitHub Actions)

### Setup GitHub Secrets

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:
   - Name: `DOCKERHUB_USERNAME`, Value: your Docker Hub username
   - Name: `DOCKERHUB_TOKEN`, Value: your Docker Hub access token

### Publishing Process

The workflow is configured for **manual execution only** via GitHub Actions.

#### Steps to Publish:

1. **Go to Actions tab** in your GitHub repository
2. Click on **"Build and Publish Docker Image"** workflow
3. Click **"Run workflow"** button
4. Fill in the required information:
   - **Version tag**: Enter the version (e.g., `0.8.0`)
   - **Also tag as latest**: Check if this should be the latest version
5. Click **"Run workflow"** to start the build

#### What the Workflow Does:

1. ✅ Checks out the repository code
2. ✅ Sets up QEMU for multi-platform builds
3. ✅ Sets up Docker Buildx
4. ✅ Logs into Docker Hub using your credentials
5. ✅ Builds images for:
   - `linux/arm/v7` (Raspberry Pi 3B - primary target)
   - `linux/amd64` (x86-64 systems)
   - `linux/arm64` (Raspberry Pi 4, 5)
6. ✅ Pushes to Docker Hub with specified tags
7. ✅ Updates Docker Hub repository description

#### Example:

If you run the workflow with:
- Version: `0.8.0`
- Latest: `true` ✓

The following images will be published:
- `geekmd/crazyones:0.8.0`
- `geekmd/crazyones:latest`

## Manual Publishing Process (Alternative)

If you prefer to build and push manually from your local machine:

### 1. Login to Docker Hub

```bash
docker login
# Enter your Docker Hub username and password
```

### 2. Build Multi-Platform Image

```bash
# Create builder if not exists
docker buildx create --name crazyones-builder --use
docker buildx inspect --bootstrap

# Build and push for multiple platforms
docker buildx build \
  --platform linux/arm/v7,linux/amd64,linux/arm64 \
  --tag geekmd/crazyones:0.8.0 \
  --tag geekmd/crazyones:latest \
  --push \
  .
```

### 3. Verify the Image

```bash
# Check the image on Docker Hub
docker manifest inspect geekmd/crazyones:0.8.0

# Pull and test the image
docker pull geekmd/crazyones:0.8.0
```

## Version Tagging Strategy

We use semantic versioning with the following tags:

- `geekmd/crazyones:0.8.0` - Specific version (recommended for production)
- `geekmd/crazyones:0.8` - Minor version
- `geekmd/crazyones:latest` - Latest stable release
- `geekmd/crazyones:dev` - Development builds (future)

### Creating a New Release

When releasing a new version:

1. **Update version** in all files:
   - `crazyones.py` (`__version__`)
   - `pyproject.toml` (`version`)
   - `config.json` (`version`)
   - `Dockerfile` (`LABEL version`)
   - `compose.yml` (`image` tag)

2. **Build and push** with version tags:

```bash
# Replace X.Y.Z with your version number
VERSION="0.8.0"

docker buildx build \
  --platform linux/arm/v7,linux/amd64 \
  --tag geekmd/crazyones:${VERSION} \
  --tag geekmd/crazyones:0.8 \
  --tag geekmd/crazyones:latest \
  --push \
  .
```

3. **Create Git tag** and release:

```bash
git tag -a v0.8.0 -m "Release version 0.8.0"
git push origin v0.8.0
```

## Using Published Images

Users can now pull and use the image directly from Docker Hub:

### Option 1: Using Docker Compose (Recommended)

Update `compose.yml` to use the published image:

```yaml
services:
  crazyones:
    image: geekmd/crazyones:0.8.0  # Or :latest
    # Remove 'build: .' line
    container_name: crazyones
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - APPLE_UPDATES_URL=${APPLE_UPDATES_URL:-https://support.apple.com/en-us/100100}
      - CHECK_INTERVAL=${CHECK_INTERVAL:-43200}
    volumes:
      - ./data:/app/data
      - ./crazyones.log:/app/crazyones.log
      - ./config.json:/app/config.json
    restart: unless-stopped
```

Then run:
```bash
docker compose pull
docker compose up -d
```

### Option 2: Using Docker Run

```bash
docker run -d \
  --name crazyones \
  --restart unless-stopped \
  -e TELEGRAM_BOT_TOKEN="your_token_here" \
  -e APPLE_UPDATES_URL="https://support.apple.com/en-us/100100" \
  -e CHECK_INTERVAL=43200 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/crazyones.log:/app/crazyones.log \
  -v $(pwd)/config.json:/app/config.json \
  geekmd/crazyones:0.8.0
```

## Platform Support

The image is built for the following platforms:

- **linux/arm/v7**: Raspberry Pi 3B, 3B+, Zero 2 W (primary target)
- **linux/amd64**: x86-64 systems (for development/testing)

Future support may include:
- **linux/arm64**: Raspberry Pi 4, 5 (ARM64)

## Automated Publishing (Future)

For automated builds and publishing, we can set up:

### GitHub Actions Workflow

Create `.github/workflows/docker-publish.yml`:

```yaml
name: Publish Docker Image

on:
  push:
    tags:
      - 'v*'
  release:
    types: [published]

jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: geekmd/crazyones
          tags: |
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=semver,pattern={{major}}
            type=raw,value=latest,enable={{is_default_branch}}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/arm/v7,linux/amd64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
```

### Required GitHub Secrets

Add to your repository settings → Secrets and variables → Actions:

- `DOCKERHUB_USERNAME`: Your Docker Hub username
- `DOCKERHUB_TOKEN`: Docker Hub access token (create at hub.docker.com → Account Settings → Security)

## Docker Hub Repository Settings

### Description

```
CrazyOnes - Apple Security Updates Monitoring System

Automated monitoring and notifications for Apple security updates across all languages. 
Optimized for Raspberry Pi 3B with ARM32v7 architecture.

Features:
- Docker-based deployment
- Daemon mode with configurable intervals
- Multi-language support
- Smart change detection
- Automatic instance management

GitHub: https://github.com/Geek-MD/CrazyOnes
```

### README Content

The Docker Hub README should include:
- Quick start guide
- Environment variables
- Volume mounts
- Platform support
- Links to full documentation

## Troubleshooting

### Build Issues

If buildx fails:
```bash
# Remove and recreate builder
docker buildx rm crazyones-builder
docker buildx create --name crazyones-builder --use
docker buildx inspect --bootstrap
```

### Multi-platform Support

To check available platforms:
```bash
docker buildx ls
```

### Image Size

Check image sizes:
```bash
docker buildx imagetools inspect geekmd/crazyones:0.8.0
```

## Best Practices

1. **Always test locally** before pushing to Docker Hub
2. **Use specific version tags** in production (not `latest`)
3. **Update CHANGELOG.md** with each release
4. **Test on actual Raspberry Pi 3B** before releasing
5. **Keep security in mind** - don't include secrets in the image

## Support

For issues or questions:
- GitHub Issues: https://github.com/Geek-MD/CrazyOnes/issues
- Docker Hub: https://hub.docker.com/r/geekmd/crazyones
