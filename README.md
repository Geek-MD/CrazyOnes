# CrazyOnes

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)
![Type Checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**CrazyOnes** is a Python-based service designed to automate monitoring and notifications about Apple security updates.

The system continuously monitors Apple's security updates page across all available languages, detecting new updates and tracking changes automatically. It runs as a daemon checking for updates four times daily (every 6 hours by default).

## Key Features

- 🔄 **Automatic monitoring** runs continuously in daemon mode (4x per day by default)
- 🌍 **Multi-language support** - monitors all language versions of Apple Updates
- 🔍 **Smart change detection** - only processes new or changed information
- 📊 **Integrated workflow**:
  1. Scrapes language URLs from Apple Updates page
  2. Monitors security updates from each language URL
  3. Tracks changes using SHA256 hashing
  4. Saves data incrementally (smart merging)
- 🔐 **Token validation** ensures Telegram bot token is properly configured
- 💾 **Persistent data** stored locally in JSON files
- ⚙️ **Easy setup** with configuration wizard and systemd service support
- 🥧 **Raspberry Pi compatible** - perfect for running on Raspberry Pi devices

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

### Running as a Service

If you used the configuration wizard, CrazyOnes can be installed as a systemd service (Linux only):

```bash
# Check service status
sudo systemctl status crazyones

# View service logs
sudo journalctl -u crazyones -f

# Stop the service
sudo systemctl stop crazyones

# Restart the service
sudo systemctl restart crazyones

# Disable auto-start on boot
sudo systemctl disable crazyones
```

### Daemon Mode (Continuous Monitoring)

Run CrazyOnes in daemon mode for continuous monitoring:

```bash
# Run as daemon with default 6-hour interval (4x per day)
python crazyones.py --token YOUR_BOT_TOKEN --daemon

# Run as daemon with Telegram bot enabled
python crazyones.py --token YOUR_BOT_TOKEN --daemon --bot

# Run as daemon with custom interval (e.g., every 3 hours)
python crazyones.py --token YOUR_BOT_TOKEN --daemon --interval 10800

# Run as daemon with custom URL
python crazyones.py --token YOUR_BOT_TOKEN --url https://support.apple.com/es-es/100100 --daemon

# Run with bot and custom interval
python crazyones.py --token YOUR_BOT_TOKEN --daemon --bot --interval 21600
```

In daemon mode, the system will:
1. Scrape language URLs from Apple Updates page
2. Monitor security updates from each language URL
3. Save all changes to JSON files
4. Send notifications to Telegram subscribers (if --bot is enabled)
5. Wait for the specified interval
6. Repeat the cycle indefinitely

**Telegram Bot Features:**
- Users can subscribe by sending `/start` to the bot
- Select their preferred Apple Updates language
- **Automatic UI language detection** - bot interface adapts to user's selected language
- **157 languages supported** - full translation system with JSON-based string management
- First-time subscribers receive the 10 most recent updates
- Subsequently, only new updates are sent
- Notifications are formatted in the user's selected language
- Users can unsubscribe anytime by sending `/stop`
- Automatically unsubscribes when bot is removed from channels/groups

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
