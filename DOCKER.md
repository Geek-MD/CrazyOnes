# CrazyOnes

**CrazyOnes** is a Python-based service that automates monitoring and Telegram notifications for Apple security updates.

It continuously monitors Apple's security updates page across all available languages, detects new updates, and notifies subscribed Telegram users.

## Services

Two containers work together:

- **crazyones-monitor** – Runs on a configurable interval (default: every 6 hours) to scrape Apple Updates and detect changes.
- **crazyones-bot** – Runs continuously to handle Telegram user commands and deliver notifications.

## Quick Start

### 1) Prepare environment variables

```bash
cp .env.example .env
```

Edit `.env` and set your values:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
APPLE_UPDATES_URL=https://support.apple.com/en-us/100100
CRAZYONES_INTERVAL=21600
```

> ⚠️ If `TELEGRAM_BOT_TOKEN` is left as the example value, the containers will stop on startup with an error.

### 2) Pull and run

```bash
docker compose up -d
```

### 3) View logs

```bash
docker compose logs -f crazyones-monitor
docker compose logs -f crazyones-bot
```

### 4) Stop

```bash
docker compose down
```

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | ✅ | — | Telegram Bot API token |
| `APPLE_UPDATES_URL` | ❌ | `https://support.apple.com/en-us/100100` | Apple Updates page URL |
| `CRAZYONES_INTERVAL` | ❌ | `21600` | Monitoring interval in seconds (default: 6 hours) |
| `ADMIN_USER_ID` | ❌ | — | Telegram user ID for admin commands |

## Persistent Data

Both containers mount `./data` to `/app/data` for persistent storage of subscriptions and update history.

## Source

GitHub: [https://github.com/Geek-MD/CrazyOnes](https://github.com/Geek-MD/CrazyOnes)
