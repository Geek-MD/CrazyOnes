# CrazyOnes

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)
![Type Checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**CrazyOnes** is a Python-based service designed to automate monitoring and notifications about Apple security updates.

The system continuously monitors Apple's security updates page across all available languages, detecting new updates and tracking changes automatically. It consists of two independent services that work together:

1. **Monitoring Service** - Runs every 6 hours to scrape and detect new updates
2. **Bot Service** - Runs continuously to handle user commands and send notifications

## Key Features

- 🔄 **Dual-service architecture** - Monitoring and bot run as independent systemd services
- 🔔 **Smart notifications** - Users receive only new updates they haven't seen before
- 🌍 **Multi-language support** - monitors all language versions of Apple Updates
- 🔍 **Smart change detection** - only processes new or changed information
- 📊 **Integrated workflow**:
  1. Monitoring service scrapes Apple Updates and detects changes
  2. Creates trigger files when new updates are found
  3. Bot service detects trigger and sends notifications to subscribers
  4. Tracks sent updates per user to avoid duplicates
- 🔐 **Token validation** ensures Telegram bot token is properly configured
- 💾 **Persistent data** stored locally in JSON files
- ⚙️ **Easy setup** with configuration wizard and systemd service support
- 🥧 **Raspberry Pi compatible** - perfect for running on Raspberry Pi devices

## Architecture (v1.0.0)

CrazyOnes v1.0.0 introduces a new dual-service architecture:

- **crazyones.service** - Monitoring service that scrapes Apple Updates every 6 hours
- **crazyones-bot.service** - Telegram bot service that runs continuously

Both services run independently and communicate through trigger files. When the monitoring service detects new updates, it creates a trigger file that the bot service picks up and processes.

## Usage

### Quick Start

After installation, the simplest way to start using CrazyOnes is:

```bash
# Run the configuration wizard (first time setup)
python crazyones.py

# Or manually specify token and run once
python crazyones.py --token YOUR_BOT_TOKEN

# Run in daemon mode (continuous monitoring)
python crazyones.py --token YOUR_BOT_TOKEN --daemon
```

### Running as a Service (Recommended)

**v1.0.0 introduces a dual-service architecture** that runs the monitoring and bot as separate systemd services. This is the recommended way to run CrazyOnes in production.

The configuration wizard will install both services:

```bash
# Run the configuration wizard
python crazyones.py
# or
python crazyones.py --config
```

Once installed, you have two services:

```bash
# Monitoring service (checks for updates every 6 hours)
sudo systemctl status crazyones          # Check status
sudo systemctl stop crazyones            # Stop service
sudo systemctl restart crazyones         # Restart service
sudo journalctl -u crazyones -f          # View logs

# Bot service (runs continuously)
sudo systemctl status crazyones-bot      # Check status
sudo systemctl stop crazyones-bot        # Stop service
sudo systemctl restart crazyones-bot     # Restart service
sudo journalctl -u crazyones-bot -f      # View logs
```

Both services will:
- Start automatically on system boot
- Restart automatically if they crash
- Run independently without blocking each other

### Daemon Mode (Manual Running)

You can also run the monitoring service manually in daemon mode:

```bash
# Run as daemon with default 6-hour interval (4x per day)
python crazyones.py --token YOUR_BOT_TOKEN --daemon

# Run as daemon with custom interval (e.g., every 3 hours)
python crazyones.py --token YOUR_BOT_TOKEN --daemon --interval 10800

# Run as daemon with custom URL
python crazyones.py --token YOUR_BOT_TOKEN --url https://support.apple.com/es-es/100100 --daemon
```

**Note:** In v1.0.0, the bot runs as a separate service. To run the bot manually, use:

```bash
# Run bot service manually (requires config.json with token)
python -m scripts.bot_service
```

### How It Works (v1.0.0)

The monitoring and notification system works as follows:

1. **Monitoring service** scrapes language URLs from Apple Updates page
2. **Monitoring service** detects security updates from each language URL
3. If new updates are found, creates a trigger file (`data/new_updates_trigger.json`)
4. **Bot service** checks for trigger files every 30 seconds
5. **Bot service** reads trigger and sends notifications to subscribers
6. Only sends updates that users haven't received before (tracked by update ID)
7. Users can also manually request latest updates using `/updates` command

**Telegram Bot Features:**
- Users can subscribe by sending `/start` to the bot
- Select their preferred Apple Updates language
- **Automatic UI language detection** - bot interface adapts to user's selected language
- **157 languages supported** - full translation system with JSON-based string management
- **Two ways to receive updates:**
  1. **Automatic notifications** - Receive new updates as they're detected (only unseen updates)
  2. **Manual request** - Use `/updates` command to get the latest 10 updates anytime
- Notifications are formatted in the user's selected language
- Users can unsubscribe anytime by sending `/stop`
- Automatically unsubscribes when bot is removed from channels/groups
- **Update tracking** - System remembers which updates were sent to each user to avoid duplicates

**Supported Languages:**
The bot supports 157 languages with automatic interface translation:
- **English variants**: en-us, en-gb, en-au, en-ca, en-in, and 50+ more
- **Spanish variants**: es-es, es-mx, es-ar, es-cl, and 15+ more
- **French variants**: fr-fr, fr-ca, fr-be, fr-ch, and 10+ more
- **Arabic variants**: ar-ae, ar-sa, ar-eg, and 10+ more
- **Chinese variants**: zh-cn, zh-tw, zh-hk, zh-sg, zh-mo
- **German, Italian, Japanese, Korean, Portuguese, Russian**, and many more

When a user selects their Apple Updates language preference, the bot automatically:
- Displays all messages in that language (if translation available)
- Fallback to English for languages without full translations
- Maintains consistent user experience across all commands

**Bot Commands:**
- `/start` - Subscribe to Apple Updates notifications and select language
- `/stop` - Unsubscribe and stop receiving notifications
- `/updates` - Show last 10 updates in your subscribed language
- `/updates [tag]` - Show last 10 updates filtered by tag (e.g., `/updates ios`)
- `/language` - List all available languages
- `/language [code]` - Show updates for a specific language (e.g., `/language en-us`)
- `/about` - Information about this bot
- `/help` - Show all available commands and usage information

**Fuzzy Matching (Smart Suggestions):**
The bot includes intelligent fuzzy matching to help users when they make typos:

- **Command suggestions**: If you type an invalid command, the bot suggests the correct one
  - Example: `/languages` → "Did you mean `/language`?"
  - Example: `/updat` → "Did you mean `/updates`?"
  - Example: `/halp` → "Did you mean `/help`?"

- **Tag suggestions**: When filtering updates by tag, typos are automatically matched to valid OS names
  - Example: `/updates mangos` → suggests "macos"
  - Example: `/updates visinos` → suggests "visionos"
  - Example: `/updates ioss` → suggests "ios"
  - Uses word-boundary regex to extract OS names (iOS, macOS, visionOS, watchOS, tvOS, iPadOS) from update names

Press `Ctrl+C` to stop the daemon gracefully.

#### One-Time Execution

For a single monitoring cycle without daemon mode:

```bash
# Single execution with token (uses URL from config.json)
python crazyones.py --token YOUR_BOT_TOKEN

# Single execution with specific URL
python crazyones.py --token YOUR_BOT_TOKEN --url https://support.apple.com/es-es/100100

# Short form
python crazyones.py -t YOUR_BOT_TOKEN -u https://support.apple.com/fr-fr/100100

# Show version
python crazyones.py --version

# Show help
python crazyones.py --help
```

The one-time execution will:
1. Validate the Telegram bot token
2. Save the token and URL to config.json for future use
3. Scrape the Apple Updates page for language-specific URLs (with smart merging)
4. Monitor security updates from each language URL
5. Generate/update language names based on discovered URLs
6. Log all activity to crazyones.log (automatically rotated to keep 1000 most recent lines)
7. Exit after completing the cycle

**Note**: For production use, especially on Raspberry Pi or servers, it's recommended to use daemon mode or the systemd service instead of running individual scripts.

### Configuration

The `config.json` file stores your Telegram bot token and default Apple Updates URL:

```json
{
  "version": "X.Y.Z",
  "apple_updates_url": "https://support.apple.com/en-us/100100",
  "telegram_bot_token": "YOUR_TELEGRAM_BOT_TOKEN_HERE"
}
```

This file is automatically created/updated when you run:
- The configuration wizard: `python crazyones.py --config`
- crazyones.py with the `--token` and `--url` parameters

The configuration persists across runs, so you only need to set it up once.

### Advanced: Individual Scripts (Development Only)

**Note**: The individual scripts are now integrated into the main workflow when using `crazyones.py` with or without `--daemon`.

**Quick Summary of Execution Order:**
1. **First**: `scrape_apple_updates.py` - Downloads language URLs from Apple
2. **Second**: `monitor_apple_updates.py` - Scrapes security updates for each language
3. **Optional**: `generate_language_names.py` - Auto-run by scrape script

These commands are primarily for development and testing purposes.

### Testing

To test the scraper logic without making actual HTTP requests:

```bash
# Test language URL extraction
python -m tests.test_scraper

# Test with actual Apple HTML structure
python -m tests.test_actual_html

# Test the monitoring and scraping module
python -m tests.test_monitor
```

## Code Quality

This project follows strict code quality standards:

- **Linting**: [Ruff](https://docs.astral.sh/ruff/) for fast Python linting
- **Type Checking**: [mypy](https://mypy-lang.org/) with strict mode enabled
- **Formatting**: Ruff formatter for consistent code style

To check code quality:

```bash
# Run linter
ruff check scripts/*.py tests/*.py

# Run type checker
mypy scripts/*.py --strict

# Auto-format code
ruff format scripts/*.py tests/*.py
```
