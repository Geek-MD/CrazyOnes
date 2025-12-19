# Changelog

All notable changes to the Crazy Ones - Apple Updates Bot project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Main coordinator script `crazyones.py` as the primary entry point for the application
- Configuration file `config.json` to store default Apple Updates URL and Telegram bot token
- Separate script `scripts/generate_language_names.py` to dynamically generate language names
  - Generates human-readable names from language codes (e.g., "en-us" → "English/USA")
  - Only includes languages that are actually available in Apple Updates
  - Automatically detects and adds new languages when URLs are discovered
  - Preserves existing entries when updating
- Logging system with automatic rotation:
  - All output logged to `crazyones.log`
  - Automatic rotation to keep only 1000 most recent lines
  - Timestamped log entries for tracking
  - Both console and file output
- Command-line argument support in `crazyones.py`:
  - `-t, --token`: **Required** Telegram bot token parameter
  - `-u, --url`: Optional URL argument (uses config.json if not provided)
  - `-v, --version`: Shows current version (0.5.0)
  - `-h, --help`: Shows help message (standard argparse feature)
- Automatic configuration management:
  - Token is saved to config.json when provided
  - URL is saved to config.json when provided
  - Config.json is automatically created/updated on each run
- Comprehensive test suite for new functionality:
  - `tests/test_generate_language_names.py` for language names generation
  - `tests/test_crazyones.py` for coordinator script
  - Tests for logging, rotation, token handling, and configuration
- Type annotations and strict mypy type checking for all new code

### Changed
- Modified `scripts/scrape_apple_updates.py` to automatically call `generate_language_names.py` after scraping
- Language names are now generated dynamically based on scraped URLs instead of being static
- Config.json now stores both URL and Telegram bot token
- Updated documentation (README.md) with:
  - Quick start guide using main coordinator with required token
  - Configuration instructions showing token storage
  - Updated project structure showing new files
  - Detailed usage examples for all scripts
  - Logging behavior description
- Updated CHANGELOG.md with complete feature list
- Added `crazyones.log` to `.gitignore`

### Technical Details
- Language names generator is a separate script to save CPU cycles (can be run independently)
- Main coordinator orchestrates the workflow: scrape → generate names → guide user
- Config-driven approach allows easy customization and reuse of URL and token
- Log rotation ensures log file doesn't grow indefinitely (keeps 1000 most recent lines)
- Token is masked in console output for security (shows as *****)
- Newest log entries always at the end (standard log file behavior)
- Backward compatible with existing scripts and workflows

## [0.5.0] - 2024-12-19

### Added
- New Python module (`scripts/monitor_apple_updates.py`) to monitor and scrape Apple security updates
- New utility module (`scripts/utils.py`) with shared functions to avoid code duplication
- Static reference file `data/language_names.json` with language code to display name mappings
- Language names in readable format (e.g., "en-us": "English/USA", "es-es": "Spanish/Spain")
- Automatic monitoring of `data/language_urls.json` file for changes
- Security updates table extraction from each language-specific page
- Support for extracting three-column table data:
  - Name: Update name with URL when available
  - Target: Target platform/device
  - Date: Release date of the update
- Individual JSON file generation per language in `data/updates/` directory
- Content change detection using SHA256 hashing to avoid re-processing unchanged pages
- Tracking system (`data/updates_tracking.json`) to monitor URL and content changes
- Smart processing logic:
  - First run: processes all available language URLs
  - Subsequent runs: only processes changed or new URLs
- Comprehensive error handling for network requests and parsing
- Progress reporting with visual indicators (✓, ⚠, ⊙, ✗, ➕, 💾)
- Summary statistics for processed languages
- Comprehensive test suite for monitoring module (`tests/test_monitor.py`)
- Organized directory structure:
  - `scripts/` for all Python scripts
  - `tests/` for all test files
  - `data/` for all generated JSON files and outputs
- `DEMO.md` with complete usage examples and workflow documentation

### Changed
- Refactored User-Agent header logic into shared `get_user_agent_headers()` function
- Updated `scripts/scrape_apple_updates.py` to use shared User-Agent function from `scripts/utils.py`
- Updated `scripts/scrape_apple_updates.py` to generate language names JSON automatically
- Moved all scripts to `scripts/` subdirectory for better code organization
- Moved all test files to `tests/` subdirectory for cleaner structure
- Updated all JSON file paths to use `data/` subdirectory
- Updated imports to use proper Python package structure with relative imports
- Updated `.gitignore` to reflect new directory structure

### Features
- Intelligent change detection for language URLs and page content
- Automatic creation of output directory structure
- Preservation of previously extracted data when pages haven't changed
- Full type annotations with strict type checking support
- Robust HTML parsing for Apple security updates table structure
- URL resolution for relative links in update names
- UTF-8 support for all language variants including Arabic, Hebrew, Japanese, Chinese, Korean, etc.
- Timeout handling for network requests (30 seconds)
- Clean separation of concerns with organized directory structure
- Static language names reference file for easy lookup and maintenance

## [0.1.0] - 2024-12-19

### Added
- Initial Python script (`scrape_apple_updates.py`) to scrape Apple Updates page
- Language URL extraction from Apple's security releases page (https://support.apple.com/en-us/100100)
- Support for extracting language-specific URLs from `<link rel="alternate" hreflang="xx-yy">` tags
- JSON output format for storing language codes and their corresponding URLs
- Proper User-Agent header to avoid being blocked by Apple's servers
- Dependencies management with `requirements.txt`:
  - requests >= 2.31.0
  - beautifulsoup4 >= 4.12.0
  - lxml >= 4.9.0
- Test suite with mock HTML (`test_scraper.py`)
- Test suite with actual Apple HTML structure (`test_actual_html.py`)
- `.gitignore` file for Python artifacts and test files
- Comprehensive README.md with setup and usage instructions
- Code quality configuration with `pyproject.toml`:
  - Ruff linter configuration
  - mypy type checker with strict mode
- README badges for Python version, code style, type checking, and license
- Support for 100+ language locales including:
  - Major languages: en-us, es-es, fr-fr, de-de, it-it, ja-jp, zh-cn, pt-br, ko-kr
  - Regional variants: ar-sa, ar-ae, ar-kw, en-gb, en-ca, fr-ca, es-mx, zh-tw, zh-hk
  - And many more regional locales

### Features
- Automatic extraction of all available language URLs from Apple's page
- Clean JSON output with language code as key and full URL as value
- Error handling for network requests
- Fallback to ensure at least the base URL is saved if no languages are found
- Sorted and formatted JSON output for easy reading
- Full type annotations for better code safety
- Strict code quality checks with Ruff and mypy

[0.5.0]: https://github.com/Geek-MD/CrazyOnes/releases/tag/v0.5.0
[0.1.0]: https://github.com/Geek-MD/CrazyOnes/releases/tag/v0.1.0
