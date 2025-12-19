# Demo: How to Use CrazyOnes v0.2.0

## Step 1: Scrape Language URLs

First, run the scraper to get all language-specific URLs:

```bash
python -m scripts.scrape_apple_updates
```

This creates `data/language_urls.json` with all available language versions.

## Step 2: Monitor and Scrape Security Updates

Then, run the monitor to scrape security updates from each language:

```bash
python -m scripts.monitor_apple_updates
```

This will:
- Read `data/language_urls.json`
- On first run: process ALL language URLs
- Extract the security updates table from each page
- Save results to `data/updates/en-us.json`, `data/updates/es-es.json`, etc.
- Create `data/updates_tracking.json` to track content changes

## Step 3: Subsequent Runs

Run the monitor again:

```bash
python -m scripts.monitor_apple_updates
```

This time it will:
- Only process pages that have changed (detected via SHA256 hash)
- Skip unchanged pages (you'll see "⊙ No content changes detected")
- Only fetch and process new or modified content

## Output Structure

```
data/
├── language_urls.json           # All language URLs
├── updates_tracking.json        # Tracking data (URLs + hashes)
└── updates/                     # Security updates per language
    ├── en-us.json
    ├── es-es.json
    ├── fr-fr.json
    └── ...
```

## Example Output JSON

Each `data/updates/{lang}.json` file contains:

```json
[
  {
    "name": "iOS 17.2 and iPadOS 17.2",
    "url": "https://support.apple.com/HT213530",
    "target": "iPhone XS and later, iPad Pro 12.9-inch 2nd generation and later",
    "date": "11 Dec 2023"
  },
  {
    "name": "macOS Sonoma 14.2",
    "url": "https://support.apple.com/HT213531",
    "target": "macOS Sonoma",
    "date": "11 Dec 2023"
  }
]
```

## Testing

Run the test suite to verify everything works:

```bash
# Test language URL extraction
python -m tests.test_scraper

# Test actual HTML parsing
python -m tests.test_actual_html

# Test monitor functionality
python -m tests.test_monitor
```
