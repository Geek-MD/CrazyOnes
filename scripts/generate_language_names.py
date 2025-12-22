#!/usr/bin/env python3
"""
Script to generate language_names.json dynamically from language_urls.json.

This script reads the language URLs that were scraped and generates a mapping
of language codes to their human-readable display names. It only includes
languages that are actually available in Apple Updates.
"""

import json
import sys
from pathlib import Path

# Mapping of language-country codes to human-readable names
LANGUAGE_NAME_MAP = {
    "ar-ae": "Arabic/UAE",
    "ar-bh": "Arabic/Bahrain",
    "ar-eg": "Arabic/Egypt",
    "ar-jo": "Arabic/Jordan",
    "ar-kw": "Arabic/Kuwait",
    "ar-qa": "Arabic/Qatar",
    "ar-sa": "Arabic/Saudi Arabia",
    "de-de": "German/Germany",
    "el-gr": "Greek/Greece",
    "en-ae": "English/UAE",
    "en-al": "English/Albania",
    "en-am": "English/Armenia",
    "en-au": "English/Australia",
    "en-az": "English/Azerbaijan",
    "en-bh": "English/Bahrain",
    "en-bn": "English/Brunei",
    "en-ca": "English/Canada",
    "en-gb": "English/UK",
    "en-hk": "English/Hong Kong",
    "en-il": "English/Israel",
    "en-is": "English/Iceland",
    "en-jo": "English/Jordan",
    "en-sa": "English/Saudi Arabia",
    "en-us": "English/USA",
    "es-cl": "Spanish/Chile",
    "es-co": "Spanish/Colombia",
    "es-es": "Spanish/Spain",
    "es-mx": "Spanish/Mexico",
    "es-us": "Spanish/USA",
    "fi-fi": "Finnish/Finland",
    "fr-ca": "French/Canada",
    "fr-fr": "French/France",
    "fr-sn": "French/Senegal",
    "he-il": "Hebrew/Israel",
    "hu-hu": "Hungarian/Hungary",
    "id-id": "Indonesian/Indonesia",
    "it-it": "Italian/Italy",
    "ja-jp": "Japanese/Japan",
    "ko-kr": "Korean/South Korea",
    "nl-nl": "Dutch/Netherlands",
    "no-no": "Norwegian/Norway",
    "pl-pl": "Polish/Poland",
    "pt-br": "Portuguese/Brazil",
    "pt-pt": "Portuguese/Portugal",
    "ro-ro": "Romanian/Romania",
    "ru-ru": "Russian/Russia",
    "th-th": "Thai/Thailand",
    "tr-tr": "Turkish/Turkey",
    "zh-cn": "Chinese/China",
    "zh-hk": "Chinese/Hong Kong",
    "zh-tw": "Chinese/Taiwan",
    "sv-se": "Swedish/Sweden",
    "da-dk": "Danish/Denmark",
    "cs-cz": "Czech/Czech Republic",
    "sk-sk": "Slovak/Slovakia",
    "uk-ua": "Ukrainian/Ukraine",
    "bg-bg": "Bulgarian/Bulgaria",
    "hr-hr": "Croatian/Croatia",
    "vi-vn": "Vietnamese/Vietnam",
    "ms-my": "Malay/Malaysia",
    "ca-es": "Catalan/Spain",
}


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns the parent directory of the scripts directory, which should be
    the project root. This allows scripts to be run from any directory.
    
    Returns:
        Path object pointing to the project root
    """
    # Get the directory where this script is located
    scripts_dir = Path(__file__).resolve().parent
    # Go up one level to get the project root
    return scripts_dir.parent


def load_language_urls(file_path: str = "data/language_urls.json") -> dict[str, str]:
    """
    Load language URLs from JSON file.

    Args:
        file_path: Path to the language URLs JSON file (relative to project root)

    Returns:
        Dictionary mapping language codes to URLs

    Raises:
        FileNotFoundError: If the language URLs file doesn't exist
    """
    # Resolve path relative to project root
    path = get_project_root() / file_path
    if not path.exists():
        raise FileNotFoundError(f"Language URLs file not found: {file_path}")

    with open(path, encoding="utf-8") as f:
        data: dict[str, str] = json.load(f)
        return data


def generate_language_name(lang_code: str) -> str:
    """
    Generate a human-readable name for a language code.

    Args:
        lang_code: Language code (e.g., 'en-us', 'es-es')

    Returns:
        Human-readable language name

    Examples:
        >>> generate_language_name('en-us')
        'English/USA'
        >>> generate_language_name('es-mx')
        'Spanish/Mexico'
    """
    # Check if we have a predefined name
    if lang_code in LANGUAGE_NAME_MAP:
        return LANGUAGE_NAME_MAP[lang_code]

    # Otherwise, try to generate a reasonable name from the code
    parts = lang_code.split("-")
    if len(parts) == 2:
        lang, country = parts
        return f"{lang.capitalize()}/{country.upper()}"

    return lang_code.upper()


def generate_language_names(
    language_urls: dict[str, str],
) -> dict[str, str]:
    """
    Generate language names mapping from language URLs.

    Args:
        language_urls: Dictionary mapping language codes to URLs

    Returns:
        Dictionary mapping language codes to human-readable names
    """
    language_names = {}

    for lang_code in language_urls.keys():
        language_names[lang_code] = generate_language_name(lang_code)

    return language_names


def save_language_names(
    language_names: dict[str, str],
    output_file: str = "data/language_names.json",
) -> None:
    """
    Save language names to a JSON file.

    Args:
        language_names: Dictionary mapping language codes to names
        output_file: Path to the output JSON file (relative to project root)
    """
    # Resolve path relative to project root
    output_path = get_project_root() / output_file
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(language_names, f, indent=2, ensure_ascii=False)

    print(f"Language names saved to {output_file}")
    print(f"Generated {len(language_names)} language name mappings")


def update_language_names(
    language_urls_file: str = "data/language_urls.json",
    language_names_file: str = "data/language_names.json",
) -> None:
    """
    Update language_names.json with any new languages from language_urls.json.

    This function loads existing language names (if any), then adds any new
    language codes found in language_urls.json that are not yet in
    language_names.json.

    Args:
        language_urls_file: Path to the language URLs JSON file (relative to project root)
        language_names_file: Path to the language names JSON file (relative to project root)
    """
    # Load language URLs
    language_urls = load_language_urls(language_urls_file)

    # Load existing language names if file exists
    language_names_path = get_project_root() / language_names_file
    if language_names_path.exists():
        with open(language_names_path, encoding="utf-8") as f:
            existing_names = json.load(f)
    else:
        existing_names = {}

    # Generate names for all language codes
    new_names = generate_language_names(language_urls)

    # Check if there are any new languages
    new_languages = set(new_names.keys()) - set(existing_names.keys())
    if new_languages:
        print(f"\nDetected {len(new_languages)} new language(s):")
        for lang in sorted(new_languages):
            print(f"  + {lang}: {new_names[lang]}")

    # Merge with existing names (new names take precedence)
    existing_names.update(new_names)

    # Save the updated language names
    save_language_names(existing_names, language_names_file)


def main() -> None:
    """Main function to generate language names from language URLs."""
    print("=== Language Names Generator ===\n")

    try:
        update_language_names()
        print("\n✓ Language names generation completed successfully")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print(
            "\nPlease run scrape_apple_updates.py first to generate "
            "data/language_urls.json"
        )
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
