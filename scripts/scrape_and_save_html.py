import os
import requests
import yaml
from pathlib import Path
import filecmp

# Read hreflang_links.yaml with UTF-8 encoding
yaml_path = Path("html/hreflang_links.yaml")
if not yaml_path.exists():
    print(f"Error: {yaml_path} not found.")
    exit(1)

with yaml_path.open("r", encoding="utf-8") as yaml_file:
    hreflangs = yaml.safe_load(yaml_file)

# Create the 'html' directory if it doesn't exist
output_dir = Path("html")
output_dir.mkdir(exist_ok=True)

# Scrape each URL and save it as an HTML file
for hreflang, url in hreflangs.items():
    file_path = output_dir / f"{hreflang}.html"

    try:
        # Make a request to the URL with a timeout
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error if the request fails
        new_content = response.text

        # Write to a temporary file for comparison
        temp_file = file_path.with_suffix(".tmp")

        with temp_file.open("w", encoding="utf-8") as tmp_html:
            tmp_html.write(new_content)

        # Compare with the existing file if it exists
        if file_path.exists() and filecmp.cmp(str(temp_file), str(file_path), shallow=False):
            print(f"No changes for {file_path}. Skipping...")
            temp_file.unlink()  # Delete the temporary file
            continue

        # Rename the temporary file if there are changes
        temp_file.replace(file_path)
        print(f"Stored: {file_path}")

    except requests.exceptions.Timeout:
        print(f"Timeout error: {url} took too long to respond.")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {url} returned {e.response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error when downloading {url}: {e}")
