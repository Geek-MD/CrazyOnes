# Crazy Ones

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)
![Type Checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue)
![License](https://img.shields.io/badge/license-MIT-green)

_Crazy Ones_ is a Docker-based service designed to automate monitoring and notifications about Apple security updates.

The system continuously monitors Apple's security updates page across all available languages, detecting new updates and tracking changes automatically. It runs as a daemon checking for updates twice daily (every 12 hours by default).

## Key Features

- 🐳 **Docker-based deployment** optimized for Raspberry Pi 3B (ARM architecture)
- 🔄 **Automatic monitoring** runs continuously in daemon mode (2x per day by default)
- 🌍 **Multi-language support** - monitors all language versions of Apple Updates
- 🔍 **Smart change detection** - only processes new or changed information
- 📊 **Integrated workflow**:
  1. Scrapes language URLs from Apple Updates page
  2. Monitors security updates from each language URL
  3. Tracks changes using SHA256 hashing
  4. Saves data incrementally (smart merging)
- 🔐 **Token validation** ensures Telegram bot token is properly configured
- 💾 **Persistent data** with volume mounts for configuration and logs

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

### Docker Setup (Recommended)

The easiest way to run CrazyOnes is using Docker. **Multi-platform support** is included - works on Raspberry Pi (ARM), x86-64 PCs, and more.

#### Supported Platforms

The Docker images automatically work on:
- 🥧 **Raspberry Pi 2B, 3B, 3B+, Zero 2 W, Zero W** (ARM 32-bit)
- 🥧 **Raspberry Pi 4, 5, 400** (ARM 32/64-bit)
- 💻 **x86-64 PCs** (Windows/WSL2, macOS Intel, Linux)

Docker automatically selects the correct image for your hardware.

**Note:** Raspberry Pi 1 and Zero (1st gen) are not supported due to ARMv6 architecture.

#### Prerequisites

- Docker and Docker Compose installed on your system
- A Telegram bot token (get one from [@BotFather](https://t.me/botfather))

#### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/Geek-MD/CrazyOnes.git
   cd CrazyOnes
   ```

2. Create your `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file and replace `YOUR_TELEGRAM_BOT_TOKEN_HERE` with your actual Telegram bot token:
   ```bash
   nano .env  # or use your preferred editor
   ```

   The `.env` file should look like:
   ```env
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
   APPLE_UPDATES_URL=https://support.apple.com/en-us/100100
   CHECK_INTERVAL=43200
   ```

4. Build and run the container:
   ```bash
   docker compose up -d
   ```

5. Check the logs:
   ```bash
   docker compose logs -f
   ```

#### Important Notes

- **The token is required**: If you don't replace the placeholder token in the `.env` file, the container will exit with an error.
- **Token validation**: The entrypoint script validates the token format before starting the application.
- **Apple Updates URL is optional**: If not specified, it defaults to the English (US) version.
- **Check interval**: Default is 43200 seconds (12 hours), which means the system checks for updates **twice per day**.
- **Data persistence**: The `data/` directory, log files, and `config.json` are mounted as volumes for persistence.
- **Automatic integrated monitoring**: The system runs in daemon mode and automatically:
  1. **Scrapes language URLs** from Apple Updates page
  2. **Monitors each language URL** for security updates
  3. **Saves new/updated information** incrementally (smart merging)
  4. **Tracks changes** to avoid reprocessing unchanged data
  5. **Repeats every 12 hours** (or custom interval set in CHECK_INTERVAL)

#### Docker Commands

```bash
# Stop the container
docker compose down

# View logs
docker compose logs -f crazyones

# Restart the container
docker compose restart

# Rebuild the image after changes
docker compose up -d --build
```

#### Advanced Container Management

##### Accessing the Container Shell

To access the running container's shell for debugging or manual operations:

```bash
# Access the container shell
docker compose exec crazyones sh
```

Once inside the container, you can:
- **View log tail**: `python crazyones.py --log` (shows last 100 lines)
- View full log: `cat /app/crazyones.log`
- Check running processes: `ps aux`
- View configuration: `cat /app/config.json`
- Check data directory: `ls -la /app/data`
- Check version: `python crazyones.py --version`

##### Quick Log Viewing

View the last 100 lines of the log without entering the container:

```bash
# From outside the container
docker compose exec crazyones python crazyones.py --log

# Or view the mounted log file directly
tail -100 crazyones.log
```

The `--log` flag is useful for quick status checks and doesn't require a token or affect running processes.

##### Stopping the Daemon Process

The daemon process inside the container responds to signals and will shutdown gracefully. You have several options:

**Option 1: Stop the entire container** (recommended)
```bash
docker compose down
```

**Option 2: Restart the container** (applies new .env settings)
```bash
docker compose restart
```

**Option 3: Stop daemon from inside the container**

If you're inside the container shell, you can stop the daemon process:
```bash
# Find the Python process
ps aux | grep python

# Send SIGTERM signal (graceful shutdown)
kill -TERM <PID>

# Or use SIGINT (Ctrl+C equivalent)
kill -INT <PID>
```

The daemon will finish its current monitoring cycle before stopping.

##### Running with Different Parameters

To run the container with different parameters:

1. **Update the .env file** with your new parameters:
   ```bash
   nano .env
   # Change APPLE_UPDATES_URL, CHECK_INTERVAL, etc.
   ```

2. **Restart the container** to apply changes:
   ```bash
   docker compose restart
   ```

**Example**: Change check interval to 6 hours:
```bash
# Edit .env
CHECK_INTERVAL=21600

# Restart container
docker compose restart
```

##### Manual Execution Inside Container

The application automatically detects and replaces any existing instance when you start a new one. This makes it simple to run with different parameters:

```bash
# Access container shell
docker compose exec crazyones sh

# Run with new parameters - automatically replaces existing instance
python crazyones.py -t $TELEGRAM_BOT_TOKEN -u https://support.apple.com/es-es/100100 --daemon

# Or run one-time execution with different URL
python crazyones.py -t $TELEGRAM_BOT_TOKEN -u https://support.apple.com/fr-fr/100100

# Or change check interval to 6 hours
python crazyones.py -t $TELEGRAM_BOT_TOKEN --daemon --interval 21600

# Exit the container
exit
```

**How it works:**
- When you start crazyones, it automatically detects any existing instance
- The existing instance is gracefully stopped (finishes current cycle)
- The new instance starts with your specified parameters
- No manual stopping required - just run with new parameters

**Examples:**

```bash
# Switch from 12-hour to 6-hour checks
docker compose exec crazyones python crazyones.py -t $TELEGRAM_BOT_TOKEN --daemon --interval 21600

# Change to Spanish Apple Updates page
docker compose exec crazyones python crazyones.py -t $TELEGRAM_BOT_TOKEN -u https://support.apple.com/es-es/100100 --daemon

# Run a quick one-time check
docker compose exec crazyones python crazyones.py -t $TELEGRAM_BOT_TOKEN
```

**Note**: After manual changes, restarting the container will revert to the original .env parameters:
```bash
docker compose restart
```

### Manual Setup (Without Docker)

If you prefer to run CrazyOnes without Docker:

#### Requirements

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

### Project Structure

```
CrazyOnes/
├── crazyones.py        # Main coordinator script (entry point)
├── config.json         # Configuration file with default Apple Updates URL
├── Dockerfile          # Docker image definition
├── compose.yml         # Docker Compose configuration
├── docker-entrypoint.sh # Container entrypoint script
├── .env.example        # Example environment variables file
├── scripts/            # Main Python scripts
│   ├── scrape_apple_updates.py       # Scrapes language URLs
│   ├── generate_language_names.py    # Generates language names dynamically
│   ├── monitor_apple_updates.py      # Monitors and scrapes security updates
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
└── requirements.txt
```

## Usage

### Docker Usage (Recommended)

The recommended way to run CrazyOnes is using Docker (see [Docker Setup](#docker-setup-recommended-for-raspberry-pi-3b) above). The container runs in daemon mode and automatically performs monitoring cycles every 12 hours.

Once running, the system operates autonomously:
- Monitors Apple security updates across all languages
- Detects and processes only new or changed information
- Logs all activity to `crazyones.log`
- All data is persisted in mounted volumes

### Manual Execution (Without Docker)

For development or manual execution, you can run CrazyOnes directly with Python.

#### Daemon Mode (Continuous Monitoring)

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

Press `Ctrl+C` to stop the daemon gracefully.

#### One-Time Execution

For a single monitoring cycle without daemon mode:

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

**Note**: For production use, especially on Raspberry Pi, it's recommended to use Docker with daemon mode instead of running individual scripts.

### Configuration

The `config.json` file stores your Telegram bot token and default Apple Updates URL:

```json
{
  "version": "0.7.0",
  "apple_updates_url": "https://support.apple.com/en-us/100100",
  "telegram_bot_token": "YOUR_TELEGRAM_BOT_TOKEN_HERE"
}
```

This file is automatically created/updated when you run crazyones.py with the `--token` and `--url` parameters.

In Docker deployments, the configuration is managed through environment variables (`.env` file) and automatically saved to `config.json` for persistence.

### Advanced: Individual Scripts (Development Only)

**Note**: The following individual scripts are now integrated into the main workflow when using `crazyones.py` with or without `--daemon`. These commands are primarily for development and testing purposes.

#### Scraping Apple Updates

The `scrape_apple_updates.py` script fetches the Apple Updates page and extracts all language-specific URLs:

```bash
python -m scripts.scrape_apple_updates
```

This script is automatically executed as part of the monitoring cycle in `crazyones.py`.

#### Monitoring Security Updates

The `monitor_apple_updates.py` script monitors security updates from each language URL:

```bash
python -m scripts.monitor_apple_updates
```

This script is also automatically executed as part of the monitoring cycle in `crazyones.py`.

**For production use, always use the integrated workflow via `crazyones.py` or Docker.**

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
