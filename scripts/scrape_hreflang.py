import os
import requests
from bs4 import BeautifulSoup
import yaml

# URL to scrape
URL = "https://support.apple.com/en-us/100100"
OUTPUT_FILE = "html/hreflang_links.yaml"

def fetch_html(url):
    """Makes an HTTP request and returns the HTML content if successful."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"HTTP request error: {e}")
        return None

def extract_hreflangs(html_content):
    """Extracts hreflang links from the HTML and returns them as a dictionary."""
    soup = BeautifulSoup(html_content, "html.parser")
    return {
        link.get("hreflang"): link.get("href")
        for link in soup.find_all("link", hreflang=True)
        if link.get("hreflang") and link.get("href")
    }

def save_to_yaml(data, file_path):
    """Saves the extracted data to a YAML file."""
    try:
        with open(file_path, "w", encoding="utf-8") as yaml_file:
            yaml.dump(data, yaml_file, default_flow_style=False, allow_unicode=True)
        print("Scraping successful. YAML file created.")
    except OSError as e:
        print(f"Error saving YAML file: {e}")

def main():
    html_content = fetch_html(URL)
    if html_content:
        hreflangs = extract_hreflangs(html_content)
        if hreflangs:
            save_to_yaml(hreflangs, OUTPUT_FILE)
        else:
            print("No hreflang links found on the page.")

if __name__ == "__main__":
    main()
