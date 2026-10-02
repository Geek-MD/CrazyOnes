# Changelog

All notable changes to CrazyOnes are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-10-02

### Added
- SQLite-backed runtime persistence for languages, localized updates, subscriptions,
  notification blocks, pending jobs, scraping errors, and application state.
- Automatic first-run migration from the legacy runtime JSON files through a
  temporary database with an integrity check before it is published.
- Durable SQLite notification jobs and indexed, per-subscriber delivery updates.

### Changed
- Runtime state now lives in `data/crazyones.db`; `config.json` and translation
  JSON files remain unchanged as configuration and version-controlled resources.
- Successfully migrated runtime JSON files are removed after the SQLite database
  is validated and atomically installed.
- Obsolete updates are retained as inactive history instead of being lost when a
  newly scraped table replaces the current catalog.

### Breaking
- The default runtime storage format and integration boundary changed from JSON
  files to SQLite. External tools that read or write `data/*.json`, per-language
  update files, or trigger files must migrate to the SQLite database/API.
- The automatic migration removes legacy runtime JSON files after successful
  validation, so downgrading to a JSON-only CrazyOnes release requires a backup or
  an explicit SQLite-to-JSON export.

## [1.6.5] - 2026-08-20

### Fixed
- `/force updates` now recovers missing or orphaned confirmed-delivery markers by re-sending a bounded block of the 10 most recent updates instead of silently reporting success with zero deliveries.
- Forced delivery responses now report notified, already-current, recovered, failed, and skipped subscriber counts.

## [1.6.4] - 2026-08-20

### Fixed
- `/force updates` now calculates pending updates from each subscriber's last Telegram-confirmed delivery instead of an operational baseline that may have advanced without sending.
- Notification runs are serialized and subscription files are replaced atomically so concurrent automatic and forced deliveries cannot overwrite newer hashes.

## [1.6.3] - 2026-08-20

### Fixed
- The production daemon now creates a notification trigger after persisting newly detected Apple updates, allowing the bot service to deliver automatic notifications.
- Added coordinator-level regression coverage for monitoring cycles with and without updated languages.

## [1.6.2] - 2026-08-15

### Added
- New administrator-only `/force updates` mode to immediately deliver pending updates to every active subscriber.

### Fixed
- Forced pending deliveries use the automatic notification pipeline, persisting each successful subscriber's notification hash and baseline so later updates continue automatically without duplicate notifications.

## [1.6.1] - 2026-08-15

### Fixed
- Hash only the extracted Apple security-update table so unrelated page changes do not create update triggers.
- Process notification triggers transactionally and retain failed deliveries for automatic retry instead of deleting pending work before Telegram confirms it.

## [1.6.0] - 2026-08-13

### Added
- New administrator-only `/force <name|all> <hash>` command to register a known update hash as the latest update received by one active user, group, or channel, or by every active subscriber.
- `/force` validates its update hash against the locally stored update catalog and accepts subscriber names, usernames, and chat IDs.

## [1.5.1] - 2026-08-12

### Added
- Successful deliveries now persist `last_notified_update_hash`, `last_notified_update_signature`, and `last_notified_at` independently from the notification baseline.
- New subscriptions record `subscribed_at` so future delivery audits have an explicit starting timestamp.

### Fixed
- `/hash subscribers` and `/hash [username]` now recover the latest delivered update hash from legacy `notified_update_blocks`, `last_update_signature`, or `last_update_id` data and persist the recovered hash.
- Subscriber language changes preserve existing delivery metadata instead of replacing the subscription record.
- Historical subscriptions without enough delivery metadata are now reported as having no verifiable delivery record instead of incorrectly stating that no update was delivered.

## [1.5.0] - 2026-08-12

### Added
- New administrator-only `/hash` command. Without arguments it shows the 10 latest updates and appends each update's stable SHA-256 hash.
- `/hash subscribers` lists every active user, channel, and group with the hash of the latest update delivered to it.
- `/hash [username]` reports the matching user, channel, or group and its latest delivered update hash; chat IDs are also accepted and legacy subscription markers remain supported.
- Subscriber records now retain known chat names and usernames so administrator reports can identify their recipients, with live Telegram lookup as a fallback.

### Changed
- Administrator help and README documentation now describe all `/hash` variants.

## [1.4.3] - 2026-08-08

### Added
- Per-language SHA-256 update-block tracking in `data/update_blocks.json`, with a per-subscriber history of the exact blocks successfully delivered.

### Fixed
- Automatic notifications now compare each subscriber's previous language block with the current block and send only updates that have not already been recorded.
- New `/start` subscriptions persist their initial notification baseline only after Telegram accepts all 10 recent updates, preventing failed deliveries from being marked as sent.
- Existing subscriptions using `last_update_signature` or `last_update_id` remain compatible with the new block-based tracking.

## [1.4.2] - 2026-07-14

### Added
- Telegram administrator notifications for Apple Updates webscraping errors, including source, timestamp, error message, and diagnostic context.

### Changed
- Scraping error trigger creation is shared through the common utilities module to avoid duplicated notification code.

## [1.4.1] - 2026-07-14

### Fixed
- New subscribers now automatically receive the 10 most recent security updates on `/start`.
- The subscription baseline is persisted after the initial delivery so future automatic notifications only send newer updates.

## [1.4.0] - 2026-07-07

### Added
- New `/subscribers` command exclusive to the configured administrator. It reports the total number of active subscribers and a breakdown by chat type: individual users (private chats), channels, and groups/supergroups.
- `/subscribers` is listed in `/help` only when the requester is the configured administrator; all other users receive the standard unknown-command response.
- New translation keys: `help_subscribers`, `subscribers_title`, `subscribers_active_total`, `subscribers_breakdown`, `subscribers_users`, `subscribers_channels`, and `subscribers_groups` added to `strings.json`, `en-us.json`, and `es-es.json`.

### Changed
- Subscription records now persist a `chat_type` field (e.g., `private`, `group`, `supergroup`, `channel`) so subscriber counts are classified accurately. Existing records without this field fall back to a sign-based heuristic (positive chat ID → user, negative → group).

## [1.3.8] - 2026-07-07

### Fixed
- All 108 non-English locale files (previously identical copies of `strings.json`) are now fully translated into their respective native languages. Affected language families include Arabic, German, French, Italian, Dutch, Portuguese (PT and BR), Russian, Japanese, Korean, Simplified/Traditional Chinese, Thai, Vietnamese, Indonesian, Malay, Turkish, Hebrew, Greek, and all major European languages.
- Regional locale variants now correctly inherit from their canonical base locale (for example, `de-at`, `de-ch`, `de-li`, `de-lu` inherit from `de-de.json`; all `ar-*` locales from `ar-sa.json`; `zh-hk`/`zh-mo` from `zh-tw.json`; `zh-sg` from `zh-cn.json`).

## [1.3.7] - 2026-07-07

### Fixed
- `/help`, `/about`, `/version verbose`, `/language`, and `/updates` commands now respond in the user's configured language instead of always falling back to English. The Spanish (`es-es`) translation file has been fully translated, which automatically applies to all Spanish regional locales (`es-cl`, `es-ar`, `es-mx`, etc.) via the existing base-language fallback mechanism.

## [1.3.6] - 2026-07-04

### Added
- `/version verbose` argument: displays the latest release notes (parsed from `CHANGELOG.md`) and a clickable link to the full changelog on GitHub.

### Changed
- `help_version` string updated to document the new `verbose` argument.
- `version_changes` string updated to reflect current release highlights instead of the stale v1.2.0 content.

### Fixed
- Automatic version-announcement notifications on bot startup are now disabled. Users can view release notes on demand via `/version verbose`.

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
