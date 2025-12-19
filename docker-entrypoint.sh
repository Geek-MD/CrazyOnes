#!/bin/sh
set -e

# Function to log messages with timestamp
log() {
    echo "[$(date +'%Y/%m/%d %H:%M:%S')] $1"
}

log "Starting CrazyOnes container..."

# Validate TELEGRAM_BOT_TOKEN environment variable
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    log "ERROR: TELEGRAM_BOT_TOKEN environment variable is not set!"
    log "Please set TELEGRAM_BOT_TOKEN in your .env file before running the container."
    exit 1
fi

# Check if token is still the placeholder
if [ "$TELEGRAM_BOT_TOKEN" = "YOUR_TELEGRAM_BOT_TOKEN_HERE" ]; then
    log "ERROR: TELEGRAM_BOT_TOKEN is still set to the placeholder value!"
    log "Please replace 'YOUR_TELEGRAM_BOT_TOKEN_HERE' with your actual Telegram bot token in the .env file."
    exit 1
fi

# Validate token format (basic check)
# Telegram bot tokens have format: <bot_id>:<auth_token>
if ! echo "$TELEGRAM_BOT_TOKEN" | grep -qE '^[0-9]{8,10}:[A-Za-z0-9_-]{35,}$'; then
    log "ERROR: TELEGRAM_BOT_TOKEN has invalid format!"
    log "Expected format: <bot_id>:<auth_token>"
    log "  - bot_id: 8-10 digits"
    log "  - auth_token: 35+ alphanumeric characters (can include - and _)"
    log "Example: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890"
    exit 1
fi

log "Token validation passed."

# Build command arguments
CMD_ARGS="-t $TELEGRAM_BOT_TOKEN --daemon"

# Add URL if provided
if [ -n "$APPLE_UPDATES_URL" ]; then
    log "Using Apple Updates URL: $APPLE_UPDATES_URL"
    CMD_ARGS="$CMD_ARGS -u $APPLE_UPDATES_URL"
else
    log "No Apple Updates URL provided, using default from config.json"
fi

# Add custom interval if provided
if [ -n "$CHECK_INTERVAL" ]; then
    log "Using custom check interval: $CHECK_INTERVAL seconds"
    CMD_ARGS="$CMD_ARGS --interval $CHECK_INTERVAL"
else
    log "Using default check interval: 43200 seconds (12 hours, 2 times per day)"
fi

# Run the main application
log "Starting CrazyOnes application..."
exec python crazyones.py $CMD_ARGS
