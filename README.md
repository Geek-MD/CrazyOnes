# Crazy Ones

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)
![Type Checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue)
![License](https://img.shields.io/badge/license-MIT-green)

_Crazy Ones_ is a Python-based service designed to automate monitoring and notifications about Apple security updates.

The system continuously monitors Apple's security updates page across all available languages, detecting new updates and tracking changes automatically. It runs as a daemon checking for updates twice daily (every 12 hours by default).

## Key Features

- 🔄 **Automatic monitoring** runs continuously in daemon mode (2x per day by default)
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

## How It Works

CrazyOnes operates in a continuous monitoring cycle:

1. **Initialization**: Validates Telegram bot token and loads configuration
2. **Language URL Discovery**: 
   - Scrapes Apple Updates page to find all available language versions
   - Uses smart merging to detect added/removed/updated language URLs
   - Saves to `data/language_urls.json`
3. **Security Updates Monitoring**:
   - Fetches security updates from each language-specific page
   - Extracts update details (name, target device, release date)
   - Computes content hashes to detect changes
   - First run: processes all languages
   - Subsequent runs: only processes changed content
4. **Data Persistence**:
   - Saves updates to individual JSON files per language (`data/updates/en-us.json`, etc.)
   - Tracks processed URLs in `data/updates_tracking.json`
   - Logs all activity to `crazyones.log`
5. **Continuous Operation** (Daemon Mode):
   - Waits for configured interval (default: 12 hours)
   - Repeats the cycle
   - Gracefully handles shutdown signals

All configuration (token, URL) is automatically saved to `config.json` for persistence across restarts.

## Setup

### Prerequisites

- **Python 3.10 or higher** installed on your system
- A **Telegram bot token** (get one from [@BotFather](https://t.me/botfather))
- Internet connection for monitoring Apple updates

### Installation

#### Quick Setup (Automated)

The easiest way to set up CrazyOnes is using the automated setup script:

```bash
# Clone the repository
git clone https://github.com/Geek-MD/CrazyOnes.git
cd CrazyOnes

# Run the setup script
bash setup.sh
```

The setup script will:
1. Check if Python 3.10+ is installed
2. Verify pip is available
3. Let you choose between system-wide or virtual environment installation
4. Install all required dependencies from `requirements.txt`
5. Optionally run the configuration wizard

#### Manual Setup

If you prefer to install dependencies manually:

**Step 1: Clone the Repository**

```bash
git clone https://github.com/Geek-MD/CrazyOnes.git
cd CrazyOnes
```

**Step 2: Install Python Dependencies**

Choose one of the following methods:

**Option A: Using pip (recommended for most users)**

```bash
pip install -r requirements.txt
```

**Option B: Using pip with virtual environment (recommended for development)**

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Option C: On Debian/Ubuntu/Raspberry Pi OS**

```bash
# Install Python and pip if not already installed
sudo apt update
sudo apt install python3 python3-pip

# Install dependencies
pip install -r requirements.txt
```

**Option D: On Fedora/RHEL/CentOS**

```bash
# Install Python and pip if not already installed
sudo dnf install python3 python3-pip

# Install dependencies
pip install -r requirements.txt
```

**Step 3: Run the Configuration Wizard**

The easiest way to set up CrazyOnes is using the configuration wizard:

```bash
python crazyones.py
```

Or explicitly:

```bash
python crazyones.py --config
```

The wizard will:
1. Prompt you for your Telegram bot token
2. Ask for the Apple Updates URL (optional, defaults to English US version)
3. Save your configuration to `config.json`
4. Optionally install a systemd service for automatic startup

**Note**: The systemd service installation requires sudo privileges and is only available on Linux systems with systemd (like most modern Linux distributions and Raspberry Pi OS).

**Step 4: Verify Installation**

Check if everything is working:

```bash
# Check version
python crazyones.py --version

# View help
python crazyones.py --help
```

### Project Structure

```
CrazyOnes/
├── crazyones.py        # Main coordinator script (entry point)
├── setup.sh            # Automated setup script for dependencies
├── config.json         # Configuration file with bot token and Apple Updates URL
├── requirements.txt    # Python dependencies
├── pyproject.toml      # Project metadata and tool configuration
├── scripts/            # Main Python scripts
│   ├── scrape_apple_updates.py       # Scrapes language URLs
│   ├── generate_language_names.py    # Generates language names dynamically
│   ├── monitor_apple_updates.py      # Monitors and scrapes security updates
│   ├── telegram_bot.py               # Telegram bot implementation
│   └── utils.py                      # Shared utility functions
├── tests/              # Test files
│   ├── test_scraper.py
│   ├── test_actual_html.py
│   ├── test_monitor.py
│   ├── test_generate_language_names.py
│   └── test_crazyones.py
├── data/               # Generated data (created automatically)
│   ├── language_urls.json         # Language-specific URLs
│   ├── language_names.json        # Human-readable language names (dynamic)
│   ├── updates_tracking.json      # Content tracking data
│   └── updates/                   # Security updates per language
│       ├── en-us.json
│       ├── es-es.json
│       └── ...
└── crazyones.log       # Application log file
```

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
# Run as daemon with default 12-hour interval (2x per day)
python crazyones.py --token YOUR_BOT_TOKEN --daemon

# Run as daemon with Telegram bot enabled
python crazyones.py --token YOUR_BOT_TOKEN --daemon --bot

# Run as daemon with custom interval (e.g., every 6 hours)
python crazyones.py --token YOUR_BOT_TOKEN --daemon --interval 21600

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
- First-time subscribers receive the 10 most recent updates
- Subsequently, only new updates are sent
- Notifications are formatted in the user's selected language (English or Spanish)
- Users can unsubscribe anytime by sending `/stop`
- Automatically unsubscribes when bot is removed from channels/groups

**Bot Commands:**
- `/start` - Subscribe to Apple Updates notifications and select language
- `/stop` - Unsubscribe and stop receiving notifications

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
  "version": "0.9.0",
  "apple_updates_url": "https://support.apple.com/en-us/100100",
  "telegram_bot_token": "YOUR_TELEGRAM_BOT_TOKEN_HERE"
}
```

This file is automatically created/updated when you run:
- The configuration wizard: `python crazyones.py --config`
- crazyones.py with the `--token` and `--url` parameters

The configuration persists across runs, so you only need to set it up once.

### Advanced: Individual Scripts (Development Only)

**Note**: The following individual scripts are now integrated into the main workflow when using `crazyones.py` with or without `--daemon`. These commands are primarily for development and testing purposes.

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
