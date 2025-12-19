# Crazy Ones

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)
![Type Checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue)
![License](https://img.shields.io/badge/license-MIT-green)

_Crazy ones_ is a service designed to automate notifications about software updates for Apple devices.

It relies on two key components to perform its task. The first is a GitHub Actions workflow that scrapes the content of the Apple Updates website in the various languages in which it's available.

The second is a Python script that monitors changes in the HTML files within this repository. Using a Telegram bot, it notifies users about new updates while ignoring those that have already been reported

## Setup

### Requirements

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

### Project Structure

```
CrazyOnes/
├── scripts/           # Main Python scripts
│   ├── scrape_apple_updates.py    # Scrapes language URLs
│   ├── monitor_apple_updates.py   # Monitors and scrapes security updates
│   └── utils.py                   # Shared utility functions
├── tests/             # Test files
│   ├── test_scraper.py
│   ├── test_actual_html.py
│   └── test_monitor.py
├── data/              # Generated data (created automatically)
│   ├── language_urls.json         # Language-specific URLs
│   ├── updates_tracking.json      # Content tracking data
│   └── updates/                   # Security updates per language
│       ├── en-us.json
│       ├── es-es.json
│       └── ...
└── requirements.txt
```

### Scraping Apple Updates

The `scrape_apple_updates.py` script fetches the Apple Updates page and extracts all language-specific URLs from the header:

```bash
python -m scripts.scrape_apple_updates
```

This will:
1. Fetch the Apple Updates page (https://support.apple.com/en-us/100100)
2. Parse the HTML to find language-specific URLs
3. Save them to `data/language_urls.json` in the format:
   ```json
   {
     "en-us": "https://support.apple.com/en-us/100100",
     "es-es": "https://support.apple.com/es-es/100100",
     ...
   }
   ```

The script uses a proper User-Agent header to avoid being blocked by Apple's servers.

### Monitoring and Scraping Security Updates

The `monitor_apple_updates.py` script monitors changes in the `data/language_urls.json` file and scrapes the security updates table from each language-specific page:

```bash
python -m scripts.monitor_apple_updates
```

This will:
1. Load the language URLs from `data/language_urls.json`
2. Detect changes in URLs or page content using SHA256 hashing
3. For each language page, extract the security updates table with three columns:
   - **Name**: Update name with URL when available
   - **Target**: Target platform/device
   - **Date**: Release date
4. Save the extracted data to individual JSON files in the `data/updates/` directory (e.g., `data/updates/en-us.json`)
5. Track processed URLs and content hashes in `data/updates_tracking.json` to avoid re-processing unchanged pages

**First run behavior**: Processes all language URLs

**Subsequent runs**: Only processes URLs that have changed or pages whose content has changed

The monitoring system intelligently detects:
- New language URLs added to `data/language_urls.json`
- Modified URLs for existing languages
- Content changes in the security updates tables

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
