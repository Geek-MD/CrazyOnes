# Changelog

All notable changes to the Crazy Ones - Apple Updates Bot project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.11.2] - 2024-12-23

### Fixed
- **Fuzzy tag matching** for `/updates` command now works correctly with misspelled OS names
  - Fixed logic to extract OS names (iOS, macOS, visionOS, watchOS, tvOS, iPadOS) from update names
  - "mangos" now suggests "macos", "visinos" suggests "visionos", etc.
  - Lowered cutoff threshold to 0.5 for better matching of typos
  - Searches OS names instead of target descriptions for more accurate suggestions

### Added
- **Fuzzy command matching** for mistyped bot commands
  - Suggests correct command when user types similar but invalid command
  - Examples: "/languages" suggests "/language", "/updat" suggests "/updates"
  - Provides helpful error message when no similar command is found

## [0.9.3] - 2024-12-23

### Changed
- **Default monitoring interval** reduced from 12 hours to 6 hours (4x per day)
  - Daemon mode now checks for updates 4 times daily by default
  - `--interval` default changed from 43200 to 21600 seconds
  - Systemd service updated to use 6-hour interval
- **Comprehensive language-country code mappings** expanded to 115 codes
  - Added 54 missing language-country combinations
  - Fixed issue where codes like "ar-om" were generated as "Ar/OM" instead of "Arabic/Oman"
  - Organized by language family with clear inline comments
  - Added Norwegian variant explanation (Bokmål, Nynorsk, generic)

### Documentation
- Updated README.md to reflect 6-hour default interval
- Updated all examples to show 4x per day monitoring
- Updated help text and argument descriptions

## [0.8.0] - 2024-12-19

### Added
- **`--log` flag** to view last 100 lines of log file without requiring token
  - Shows log tail with total line count
  - Useful for quick status checks inside container
  - Can be used alongside --help and --version without starting execution
- **Automatic instance management** with PID file tracking
  - Detects and stops existing instances automatically
  - Graceful process replacement when starting with new parameters
  - No manual stopping required - just run with new parameters
  - Seamless experience inside Docker container
- **Docker Hub publishing support**
  - Added version labels to Dockerfile (0.8.0)
  - Added image tag to compose.yml (geekmd/crazyones:0.8.0)
  - Created DOCKER_HUB.md with manual publishing instructions
  - GitHub Actions workflow for automated multi-platform builds
  - Support for linux/arm/v7, linux/amd64, and linux/arm64

### Changed
- **Token parameter is now optional** for informational commands
  - `--log`, `--version`, `-v`, `--help`, `-h` don't require `--token`
  - These flags are self-contained and don't affect running processes
- **Version bumped to 0.8.0** across all files
  - crazyones.py, pyproject.toml, config.json updated
  - Reflects significant new features added

### Documentation
- Added comprehensive container management guide in README
- Created DOCKER_HUB.md with publishing workflow
- Documented automatic instance replacement behavior
- Added examples for running with different parameters inside container

### Technical Details
- PID file management functions for process tracking
- `show_log_tail()` function for log viewing
- Enhanced argument parsing with optional token requirement
- GitHub Actions workflow with QEMU and Buildx for multi-platform support

## [0.7.0] - 2024-12-19

### Added
- **Docker containerization support** for easy deployment on Raspberry Pi 3B
  - Alpine Linux-based Dockerfile optimized for ARM architecture
  - `compose.yml` for Docker Compose deployment
  - `docker-entrypoint.sh` with comprehensive token validation
  - `.env.example` file with all configuration options documented
- **Daemon mode** for continuous monitoring (runs 2x per day by default)
  - `--daemon` flag for continuous execution
  - `--interval` flag for custom check intervals (default: 43200 seconds = 12 hours)
  - Graceful shutdown with SIGINT/SIGTERM signal handlers
  - Thread-safe shutdown mechanism using `threading.Event`
  - Efficient waiting with `threading.Event.wait()` instead of sleep loops
- **Integrated security updates monitoring** in main workflow
  - Automatic execution of both scraping and monitoring in each cycle
  - First run: parses all information from all language URLs
  - Subsequent runs: only updates changed information
  - Content hash tracking to detect changes
- **Smart URL merging** in `scripts/scrape_apple_updates.py`
  - Incremental updates: only add/remove/update changed URLs
  - Clear change reporting (added, removed, updated, unchanged)
  - First-time detection with full initial load
  - Optimized performance with lazy calculations
- **Comprehensive documentation**
  - `DOCKER.md` with detailed Docker deployment guide
  - Updated `README.md` with Docker quick start
  - Instructions for Raspberry Pi 3B deployment
  - Configuration examples and troubleshooting

### Changed
- **Token is now required** via command-line argument for security
- **Telegram bot token validation** in both entrypoint script and Python code
  - Format validation (bot_id:auth_token pattern)
  - Placeholder detection with clear error messages
  - Prevents container startup with invalid tokens
- Token and URL are automatically saved to `config.json` when provided
- Imports moved to module level for better performance
- Optimized change detection calculations in scraping logic
- Updated version to 0.7.0 across all files

### Technical Details
- Alpine Linux chosen for minimal footprint (~5MB base) and ARM support
- Daemon mode uses threading.Event for efficient, interruptible waits
- Thread-safe signal handling without race conditions
- Volume mounts for persistent data (data/, logs, config)
- Automatic restart policy with `unless-stopped`
- Module-level imports prevent repeated overhead in daemon loop
- Proper argument quoting in shell scripts to prevent injection
- Zero security vulnerabilities (CodeQL verified)

### Docker Configuration
- **TELEGRAM_BOT_TOKEN**: Required, validated before startup
- **APPLE_UPDATES_URL**: Optional, defaults to en-us version
- **CHECK_INTERVAL**: Optional, defaults to 43200 seconds (12 hours)
- Persistent volumes: `./data`, `./config.json`, `./crazyones.log`

### Breaking Changes
- Token parameter (`-t` / `--token`) is now required for all executions
- Interactive token confirmation only in non-daemon mode

## [0.6.0] - 2024-12-19

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

[0.8.0]: https://github.com/Geek-MD/CrazyOnes/releases/tag/v0.8.0
[0.7.0]: https://github.com/Geek-MD/CrazyOnes/releases/tag/v0.7.0
[0.5.0]: https://github.com/Geek-MD/CrazyOnes/releases/tag/v0.5.0
[0.1.0]: https://github.com/Geek-MD/CrazyOnes/releases/tag/v0.1.0
