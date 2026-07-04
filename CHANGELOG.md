# Changelog

All notable changes to CrazyOnes are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.5] - 2026-07-04

### Added
- Administrator user ID can now be configured via the `ADMIN_USER_ID` environment variable (Docker) or the `admin_user_id` field in `config.json`.
- New `/rebuild` command reserved exclusively for the administrator. It forces a full re-scrape of the Apple Updates page and regenerates all language-specific `data/updates/<lang>.json` files.
- `/rebuild` is shown in `/help` only when the requester is the configured administrator; all other users receive the standard unknown-command response so the command's existence is not disclosed.
- New translation keys: `help_commands_admin`, `help_rebuild`, `rebuild_started`, `rebuild_success`, and `rebuild_error` added to `strings.json` and `en-us.json`.

## [1.3.0] - 2026-07-03

### Added
- Automatic security-update notification flow now uses a stable content signature per update to reliably detect and deliver only truly new updates to subscribed users.

### Changed
- Subscription records now persist `last_update_signature` as the primary marker for new-update delivery, with backward-compatible migration from legacy `last_update_id`.

## [1.2.2] - 2026-07-03

### Fixed
- `/version` command was reporting stale version `1.1.1` due to outdated hardcoded values in `Dockerfile` and `docker-entrypoint.sh`.

## [1.2.1] - 2026-07-03

### Changed
- Translation lookup now falls back by base language (for example, `es-cl` uses `es-es` when locale-specific strings are incomplete), improving Spanish help and updates coverage.
- Help command entries are now rendered in plain command format (without italicized command names), including `/version`.
- `pyproject.toml` is now the single source of truth for the version number. `crazyones.py` resolves the version at runtime via `importlib.metadata` instead of a hardcoded string.
- Docker publish workflow now reads the version from `pyproject.toml` (via `tomllib`) instead of `config.json`, making the release process independent of user configuration files.

### Fixed
- Update name extraction for rows without links now ignores extra helper/CVE text in the same table cell.
- `/version` command and `--version` CLI flag were reporting the stale `1.1.1` version string after the v1.2.0 and v1.2.1 releases.

## [1.2.0] - 2026-07-03

### Added
- `/version` command to report the currently running bot version.
- Subscriber database extended to track the last notified version per installation, enabling automatic version-announcement messages.
- On bot startup, when a new version is detected, all active subscribers receive a notification in their registered language summarising the release highlights.
- New translation keys: `version_message`, `help_version`, `version_notification_header`, `version_notification_body`, and `version_changes` added to all 158 language files.

### Changed
- Help text updated to include `/version` in the command list.
- `VALID_COMMANDS` extended with `"version"` so fuzzy matching covers the new command.

## [1.1.1] - 2026-07-02

### Fixed
- `AttributeError: 'Namespace' object has no attribute 'bot'` in `main()` caused by a stale reference to a removed `--bot` argument that prevented the monitor container from starting.
- Docker healthcheck replaced `pgrep` (unavailable in `python:slim`) with a PID-file check (`kill -0`) so the monitor container is correctly reported as healthy.

## [1.1.0] - 2026-07-01

### Added
- Docker container support with a production-ready `Dockerfile`.
- `docker-compose.yml` with dedicated monitor and bot services.
- `.env.example` template for container configuration.

### Changed
- Container startup now generates `config.json` from environment variables.
- Docker startup halts when it detects the example Telegram token and reports the issue in terminal output and logs.

## [1.0.0] - 2025-12-29

### Added
- Dual-service architecture with an independent monitoring service and bot service.
- Automatic notification flow driven by trigger files between both services.
- Dedicated `scripts/bot_service.py` runtime for continuous bot execution.

### Changed
- Production setup now centers on separate systemd services for monitoring and bot delivery.
- Documentation was updated to reflect the new architecture and operating model.

### Fixed
- Follow-up code review issues after the service split.

## [0.17.2] - 2025-12-27

### Changed
- Removed emoticons and bullet-heavy text from the bot interface and translations.
- Regenerated translation files from the shared strings template for consistency.

### Fixed
- Header and language text formatting in Telegram messages.
- Test coverage for Telegram markdown formatting and command error handling.

## [0.17.1] - 2025-12-26

### Fixed
- Help command bullet formatting.
- Robustness of updates header formatting and language list rendering.
- Unknown-command message formatting.

## [0.17.0] - 2025-12-26

### Fixed
- Unknown-command formatting in Telegram responses.
- Updates header formatting in the bot output.
- Ruff and mypy compliance issues introduced by the formatting work.

## [0.16.0] - 2025-12-26

### Changed
- Removed markdown-specific formatting from all 158 translation files.
- Standardized translated strings to keep bot output consistent across locales.

## [0.15.2] - 2025-12-26

### Fixed
- Language list truncation by splitting long output into two variables before sending it.

## [0.15.1] - 2025-12-26

### Changed
- Unified project branding in documentation and user-facing text as `CrazyOnes`.

## [0.15.0] - 2025-12-26

### Fixed
- Language list footer formatting in Telegram responses.

## [0.14.0] - 2025-12-25

### Fixed
- `/language` command formatting so language codes render correctly alongside descriptive text.

## [0.13.0] - 2025-12-24

### Added
- Complete translation structure for all 158 supported languages.

### Changed
- Expanded localization assets and updated documentation around multilingual support.

## [0.12.0] - 2025-12-24

### Changed
- Improved README content and synchronized code quality expectations with the current codebase.

### Fixed
- Ruff and mypy issues across the project.

## [0.11.2] - 2025-12-23

### Added
- Command suggestion support for mistyped bot commands.
- Additional fuzzy matching improvements for tag searches.

### Changed
- Completed missing language-country mappings in `language_names.json`.
- Updated README and changelog to reflect the expanded bot command set.

### Fixed
- OS extraction and command parsing around fuzzy matching.

## [0.11.1] - 2025-12-23

### Fixed
- `/updates` tag filtering so searches also match update names.
- Alphabetical sorting for listed languages.

## [0.11.0] - 2025-12-23

### Added
- `/updates` command with optional tag filtering.
- `/help` command.
- `/language` command to list languages and fetch language-specific updates.
- User preference storage with default language and active subscription tracking.

### Changed
- Improved validation and error messages for language-related bot commands.

## [0.10.0] - 2025-12-23

### Added
- `/about` command for bot information.
- Standalone bot execution improvements and supporting documentation.
- URL content hashing optimization with tests and documentation.

## [0.9.3] - 2025-12-23

### Changed
- Reduced the default monitoring interval from 12 hours to 6 hours.
- Sorted generated JSON output for languages and update identifiers.

### Added
- Hidden `--once` execution parameter.
- More complete language-country mappings.

## [0.9.2] - 2025-12-22

### Added
- Interactive configuration routine and systemd service generation.
- Automated setup script for dependency installation.
- Date parsing and stable ID generation for update records.

### Changed
- Replaced the Docker-focused setup with manual and systemd-based installation guidance.
- Fixed path resolution and relative imports for manual script execution.

### Fixed
- Security and error handling issues in the configuration flow.
- Ruff and mypy compliance across the scripts.

## [0.9.1] - 2025-12-20

### Added
- `/stop` command and automatic unsubscribe when the bot is removed.
- Better workflow support for extracting the app version from `config.json`.

### Changed
- Docker publishing workflow and documentation updates for the then-current deployment model.

### Fixed
- Container initialization and configuration edge cases.

## [0.9.0] - 2025-12-20

### Added
- Telegram bot module with subscriptions and language selection.
- Multilingual notifications integrated into `crazyones.py`.
- Per-user update tracking to avoid duplicate deliveries.

### Changed
- Bot integration was moved into a separate thread inside the coordinator workflow.
- Documentation was extended for Raspberry Pi and multi-platform usage.

## [0.8.0] - 2025-12-19

### Added
- `--log` flag.
- GitHub Actions workflow for Docker Hub publishing.

### Changed
- Automatic replacement of an already running daemon instance.
- README and daemon/container management documentation updates.

## [0.7.0] - 2025-12-19

### Added
- Docker containerization for Raspberry Pi deployments.
- Daemon mode for continuous monitoring.
- Integrated monitoring cycle that combines scraping and update detection.
- Comprehensive changelog for the project.

### Changed
- Telegram token handling was tightened and validated.
- URL merging and change detection became more efficient.

## [0.6.0] - 2025-12-19

### Added
- Main coordinator entry point `crazyones.py`.
- `config.json` to persist the default Apple Updates URL and Telegram token.
- `generate_language_names.py` to build display names dynamically.
- Logging with rotation and command-line arguments for the coordinator.
- Tests for configuration, logging, and language name generation.

### Changed
- Scraping now triggers language-name generation automatically.
- Documentation was updated around the new coordinator workflow.

## [0.5.0] - 2025-12-19

### Added
- `monitor_apple_updates.py` for scraping Apple security updates.
- Shared utilities module and structured data outputs in `data/updates/`.
- Content-hash tracking and per-language update exports.
- Dedicated monitoring test suite.

### Changed
- Repository layout was reorganized into `scripts/`, `tests/`, and `data/`.
- Scraping started generating language names automatically.

## [0.2.0] - 2025-12-19

### Added
- First monitoring module for Apple security updates.
- Refactored structure with clearer directories for code, tests, and generated data.

### Changed
- Project organization was reshaped beyond the initial language URL scraper.

## [0.1.0] - 2025-12-19

### Added
- Initial Python scraper for Apple's language-specific update URLs.
- JSON export of discovered locale URLs.
- Basic test coverage, dependency management, and README documentation.
- Ruff and mypy project configuration.
