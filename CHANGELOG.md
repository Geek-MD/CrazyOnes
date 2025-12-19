# Changelog

All notable changes to the Crazy Ones - Apple Updates Bot project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
