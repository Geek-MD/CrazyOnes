#!/usr/bin/env bash
set -euo pipefail

APP_HOME="${CRAZYONES_APP_HOME:-/app}"
LOG_FILE="${CRAZYONES_LOG_FILE:-${APP_HOME}/crazyones.log}"
EXAMPLE_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890"
TOKEN="${TELEGRAM_BOT_TOKEN:-}"
APPLE_UPDATES_URL="${APPLE_UPDATES_URL:-https://support.apple.com/en-us/100100}"
CRAZYONES_VERSION="${CRAZYONES_VERSION:-1.1.0}"

mkdir -p "${APP_HOME}/data"
touch "${LOG_FILE}"

log_and_tui() {
    local message="$1"
    echo "${message}" | tee -a "${LOG_FILE}"
}

if [[ -z "${TOKEN}" ]]; then
    log_and_tui "ERROR: TELEGRAM_BOT_TOKEN no está configurado."
    log_and_tui "Configura un token válido en el archivo .env antes de iniciar Docker."
    exit 1
fi

if [[ "${TOKEN}" == "${EXAMPLE_TOKEN}" ]]; then
    log_and_tui "ERROR: Se detectó el token de ejemplo en TELEGRAM_BOT_TOKEN."
    log_and_tui "La instalación se detiene por seguridad."
    log_and_tui "Edita el archivo .env con tu token real y vuelve a ejecutar docker compose up."
    exit 1
fi

cat > "${APP_HOME}/config.json" <<EOF
{
  "version": "${CRAZYONES_VERSION}",
  "apple_updates_url": "${APPLE_UPDATES_URL}",
  "telegram_bot_token": "${TOKEN}"
}
EOF

exec "$@"
