# Changelog

All notable changes to the Crazy Ones - Apple Updates Bot project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.1.0]: https://github.com/Geek-MD/CrazyOnes/releases/tag/v0.1.0
