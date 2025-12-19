#!/usr/bin/env python3
"""
Script to scrape Apple Updates page and extract language-specific URLs.

This script fetches the Apple Updates page and extracts all language-specific
URLs from the header, saving them to a JSON file.
"""

import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def fetch_apple_updates_page(url):
    """
    Fetch the Apple Updates page with proper User-Agent to avoid blocking.
    
    Args:
        url: The URL of the Apple Updates page
        
    Returns:
        The HTML content of the page
        
    Raises:
        requests.RequestException: If the request fails
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.text


def extract_language_urls(html_content, base_url):
    """
    Extract language-specific URLs from the HTML header.
    
    Args:
        html_content: The HTML content to parse
        base_url: The base URL to resolve relative URLs
        
    Returns:
        Dictionary mapping language codes to their URLs
    """
    soup = BeautifulSoup(html_content, 'lxml')
    language_urls = {}
    
    # Look for language selector in the header
    # Apple typically uses <a> tags with hreflang or data-locale attributes
    # or links in a language selector dropdown
    
    # Method 1: Try to find links with hreflang attribute
    for link in soup.find_all('a', href=True):
        if 'hreflang' in link.attrs:
            lang_code = link['hreflang']
            url = urljoin(base_url, link['href'])
            language_urls[lang_code] = url
    
    # Method 2: Try to find links in the header that point to different locales
    # Apple URLs typically have pattern like /en-us/, /es-es/, etc.
    if not language_urls:
        header = soup.find('header')
        if header:
            for link in header.find_all('a', href=True):
                href = link['href']
                # Check if the URL contains a locale pattern
                if '/support.apple.com/' in href or href.startswith('/'):
                    # Extract locale from URL path
                    parts = urlparse(href).path.strip('/').split('/')
                    if len(parts) > 0 and '-' in parts[0] and len(parts[0]) == 5:
                        locale = parts[0]
                        url = urljoin(base_url, href)
                        language_urls[locale] = url
    
    # Method 3: Look for locale selector elements (common in Apple sites)
    if not language_urls:
        # Look for elements with data-locale or similar attributes
        for element in soup.find_all(attrs={'data-locale': True}):
            locale = element['data-locale']
            if element.name == 'a' and element.get('href'):
                url = urljoin(base_url, element['href'])
                language_urls[locale] = url
    
    # Method 4: Look for link tags with alternate language versions
    if not language_urls:
        for link_tag in soup.find_all('link', rel='alternate'):
            if link_tag.get('hreflang'):
                lang_code = link_tag['hreflang']
                url = urljoin(base_url, link_tag['href'])
                language_urls[lang_code] = url
    
    return language_urls


def save_language_urls_to_json(language_urls, output_file='language_urls.json'):
    """
    Save language URLs to a JSON file.
    
    Args:
        language_urls: Dictionary mapping language codes to URLs
        output_file: Path to the output JSON file
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(language_urls, f, indent=2, ensure_ascii=False)
    
    print(f"Language URLs saved to {output_file}")
    print(f"Found {len(language_urls)} language versions:")
    for lang, url in sorted(language_urls.items()):
        print(f"  {lang}: {url}")


def main():
    """Main function to orchestrate the scraping process."""
    apple_updates_url = 'https://support.apple.com/en-us/100100'
    
    print(f"Fetching Apple Updates page: {apple_updates_url}")
    html_content = fetch_apple_updates_page(apple_updates_url)
    
    print("Extracting language-specific URLs...")
    language_urls = extract_language_urls(html_content, apple_updates_url)
    
    if not language_urls:
        print("Warning: No language URLs found. The page structure might have changed.")
        # Add the current URL as a fallback
        language_urls['en-us'] = apple_updates_url
    
    save_language_urls_to_json(language_urls)


if __name__ == '__main__':
    main()
