# Crazy Ones

_Crazy ones_ is a service designed to automate notifications about software updates for Apple devices.

It relies on two key components to perform its task. The first is a GitHub Actions workflow that scrapes the content of the Apple Updates website in the various languages in which it's available.

The second is a Python script that monitors changes in the HTML files within this repository. Using a Telegram bot, it notifies users about new updates while ignoring those that have already been reported

## Setup

### Requirements

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

### Scraping Apple Updates

The `scrape_apple_updates.py` script fetches the Apple Updates page and extracts all language-specific URLs from the header:

```bash
python scrape_apple_updates.py
```

This will:
1. Fetch the Apple Updates page (https://support.apple.com/en-us/100100)
2. Parse the HTML to find language-specific URLs
3. Save them to `language_urls.json` in the format:
   ```json
   {
     "en-us": "https://support.apple.com/en-us/100100",
     "es-es": "https://support.apple.com/es-es/100100",
     ...
   }
   ```

The script uses a proper User-Agent header to avoid being blocked by Apple's servers.

### Testing

To test the scraper logic without making actual HTTP requests:

```bash
python test_scraper.py
```
