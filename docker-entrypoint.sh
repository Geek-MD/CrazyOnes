#!/usr/bin/env bash
set -euo pipefail

APP_HOME="${CRAZYONES_APP_HOME:-/app}"
LOG_FILE="${CRAZYONES_LOG_FILE:-${APP_HOME}/crazyones.log}"
EXAMPLE_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890"
TOKEN="${TELEGRAM_BOT_TOKEN:-}"
APPLE_UPDATES_URL="${APPLE_UPDATES_URL:-https://support.apple.com/en-us/100100}"
CRAZYONES_VERSION="${CRAZYONES_VERSION:-1.2.2}"

mkdir -p "${APP_HOME}/data"
touch "${LOG_FILE}"

log_and_tui() {
    local message="$1"
    echo "${message}" | tee -a "${LOG_FILE}"
}

if [[ -z "${TOKEN}" ]]; then
    log_and_tui "ERROR: TELEGRAM_BOT_TOKEN is not configured."
    log_and_tui "Set a valid token in .env before starting Docker."
    exit 1
fi

if [[ "${TOKEN}" == "${EXAMPLE_TOKEN}" ]]; then
    log_and_tui "ERROR: Example token detected in TELEGRAM_BOT_TOKEN."
    log_and_tui "Installation stopped for safety."
    log_and_tui "Update .env with your real token and run docker compose up again."
    exit 1
fi

cat > "${APP_HOME}/config.json" <<EOF
{
  "version": "${CRAZYONES_VERSION}",
  "apple_updates_url": "${APPLE_UPDATES_URL}",
  "telegram_bot_token": "${TOKEN}"
}
EOF

# The monitor service runs `python crazyones.py` and needs --token.
# The bot service (`python -m scripts.bot_service`) reads token from config.json.
if [[ $# -ge 2 && "$1" == "python" && "$2" == "crazyones.py" ]]; then
    has_token_arg=false
    for arg in "$@"; do
        if [[ "${arg}" == "--token" ]]; then
            has_token_arg=true
            break
        fi
    done
    if [[ "${has_token_arg}" == "false" ]]; then
        set -- "$@" --token "${TOKEN}"
    fi
fi

exec "$@"
