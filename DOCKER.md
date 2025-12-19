# Docker Deployment Guide for CrazyOnes

This guide provides detailed instructions for deploying CrazyOnes using Docker, with specific considerations for Raspberry Pi 3B.

## Overview

CrazyOnes can run inside a Docker container, making deployment simple and consistent across different platforms. The Docker setup is optimized for ARM architecture, specifically for Raspberry Pi 3B.

## Architecture Choices

### Base Image: Alpine Linux

We use `python:3.10-alpine` as the base image for several reasons:

1. **Lightweight**: Alpine Linux is minimal (~5MB base image), perfect for resource-constrained devices like Raspberry Pi
2. **ARM Compatible**: Full support for ARM32v7 architecture (Raspberry Pi 3B)
3. **Secure**: Minimal attack surface due to fewer packages
4. **Fast**: Smaller images mean faster downloads and deployments

### System Dependencies

The Dockerfile includes the following system packages required for Python dependencies:

- `gcc`, `musl-dev`, `linux-headers`: C compiler and headers for building Python packages
- `libffi-dev`: Required for cryptographic operations
- `libxml2-dev`, `libxslt-dev`: Required for the `lxml` package (used by BeautifulSoup)

## Configuration

### Environment Variables

The application is configured via environment variables defined in the `.env` file:

#### TELEGRAM_BOT_TOKEN (Required)

Your Telegram bot token obtained from [@BotFather](https://t.me/botfather).

- **Format**: `<bot_id>:<auth_token>`
- **Example**: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890`
- **Validation**: The entrypoint script validates the token format before starting

**Important**: You **must** replace the placeholder value. The container will exit with an error if:
- The token is not set
- The token is still `YOUR_TELEGRAM_BOT_TOKEN_HERE`
- The token format is invalid

#### APPLE_UPDATES_URL (Optional)

The Apple Updates page URL to scrape.

- **Default**: `https://support.apple.com/en-us/100100`
- **Examples**:
  - Spanish: `https://support.apple.com/es-es/100100`
  - French: `https://support.apple.com/fr-fr/100100`
  - German: `https://support.apple.com/de-de/100100`

If not specified, the application uses the default English (US) URL or the URL saved in `config.json`.

### How Configuration Works

1. **Docker Compose** reads variables from `.env` file
2. **Entrypoint script** (`docker-entrypoint.sh`) validates the token and passes both variables as command-line arguments to `crazyones.py`
3. **crazyones.py** receives the arguments and **saves them to `config.json`** for persistence
4. On subsequent runs, if no new values are provided, the application uses values from `config.json`

This means:
- Configuration is persistent across container restarts
- You can update the token/URL by modifying `.env` and restarting the container
- The `config.json` file is mounted as a volume, preserving your settings

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Geek-MD/CrazyOnes.git
cd CrazyOnes
```

### 2. Create Configuration File

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your preferred editor:

```bash
nano .env
# or
vim .env
# or
code .env
```

Replace the placeholder token with your actual Telegram bot token:

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
APPLE_UPDATES_URL=https://support.apple.com/en-us/100100
```

### 3. Build and Start the Container

```bash
docker compose up -d
```

This command will:
1. Build the Docker image (first time only)
2. Create and start the container in detached mode
3. Configure automatic restart on failure

### 4. Verify the Container is Running

```bash
docker compose ps
```

You should see the `crazyones` container with status "Up".

### 5. View Logs

```bash
# Follow logs in real-time
docker compose logs -f

# View last 100 lines
docker compose logs --tail=100

# View logs for specific service
docker compose logs crazyones
```

## Common Operations

### Stop the Container

```bash
docker compose down
```

### Restart the Container

```bash
docker compose restart
```

### Update Configuration

1. Edit `.env` file with new values
2. Restart the container:
   ```bash
   docker compose restart
   ```

The new values will be saved to `config.json` automatically.

### Rebuild the Image

If you modify the Dockerfile or application code:

```bash
docker compose up -d --build
```

### View Container Status

```bash
docker compose ps
```

### Access Container Shell

```bash
docker compose exec crazyones sh
```

## Data Persistence

The following directories and files are mounted as volumes for persistence:

- `./data:/app/data` - Scraped data and language information
- `./crazyones.log:/app/crazyones.log` - Application logs
- `./config.json:/app/config.json` - Configuration file

This means your data survives container restarts and updates.

## Troubleshooting

### Container Exits Immediately

Check the logs to see the error:

```bash
docker compose logs
```

Common issues:

1. **Token not configured**: Make sure you replaced `YOUR_TELEGRAM_BOT_TOKEN_HERE` in `.env`
2. **Invalid token format**: Verify your token matches the format `XXXXXXXXX:XXXXXXXXXXX`
3. **Network issues**: Ensure your Raspberry Pi has internet access

### Token Validation Failed

If you see an error about invalid token format:

```
ERROR: TELEGRAM_BOT_TOKEN has invalid format!
```

Verify your token:
- Has 8-10 digits before the colon
- Has at least 35 characters after the colon
- Contains only alphanumeric characters, hyphens, and underscores

### Build Fails on Raspberry Pi

If the build fails with package installation errors:

1. Ensure your Raspberry Pi has internet access
2. Update package lists:
   ```bash
   docker system prune -a
   docker compose build --no-cache
   ```

### Container Uses Too Much Memory

Alpine Linux is already minimal, but you can limit memory usage:

Edit `compose.yml` and add:

```yaml
services:
  crazyones:
    # ... existing configuration ...
    mem_limit: 512m
    memswap_limit: 512m
```

## Raspberry Pi 3B Specific Notes

### Performance

- The Raspberry Pi 3B has 1GB RAM and a quad-core ARM Cortex-A53 processor
- Alpine Linux is lightweight enough to run smoothly on this hardware
- Expect the initial build to take 5-10 minutes on Raspberry Pi 3B
- Subsequent starts are nearly instant (seconds)

### Storage

- Ensure you have at least 500MB free space for the Docker image
- The `data/` directory will grow over time as updates are tracked
- Consider using an SD card with at least 8GB capacity

### Network

- The container requires internet access to:
  - Download packages during build
  - Scrape Apple Updates pages
  - Send Telegram notifications
- Ensure your Raspberry Pi has a stable network connection

## Security Considerations

1. **Never commit `.env` file**: The `.gitignore` file already excludes it
2. **Protect your token**: Don't share your Telegram bot token publicly
3. **Keep Docker updated**: Regularly update Docker on your Raspberry Pi
4. **Review logs**: Check logs periodically for any suspicious activity

## Advanced Configuration

### Running on a Schedule

To run CrazyOnes on a schedule instead of continuously, modify `compose.yml`:

```yaml
services:
  crazyones:
    # ... existing configuration ...
    restart: "no"  # Don't auto-restart
```

Then set up a cron job on the host:

```bash
# Edit crontab
crontab -e

# Run every hour
0 * * * * cd /path/to/CrazyOnes && docker compose up
```

### Custom Dockerfile

If you need to customize the Dockerfile:

1. Modify the `Dockerfile`
2. Rebuild with `docker compose up -d --build`

### Using Docker Hub Image

If you want to push the image to Docker Hub for easier deployment:

```bash
# Build for ARM
docker buildx build --platform linux/arm/v7 -t yourusername/crazyones:latest .

# Push to Docker Hub
docker push yourusername/crazyones:latest
```

Then update `compose.yml` to use the image instead of building:

```yaml
services:
  crazyones:
    image: yourusername/crazyones:latest
    # Remove 'build: .' line
```

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/Geek-MD/CrazyOnes).
