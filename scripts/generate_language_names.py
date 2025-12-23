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
# Based on ISO 639-1 (language) and ISO 3166-1 alpha-2 (country) codes
LANGUAGE_NAME_MAP = {
    # Arabic variants
    "ar-ae": "Arabic/UAE",
    "ar-bh": "Arabic/Bahrain",
    "ar-dz": "Arabic/Algeria",
    "ar-eg": "Arabic/Egypt",
    "ar-iq": "Arabic/Iraq",
    "ar-jo": "Arabic/Jordan",
    "ar-kw": "Arabic/Kuwait",
    "ar-lb": "Arabic/Lebanon",
    "ar-ly": "Arabic/Libya",
    "ar-ma": "Arabic/Morocco",
    "ar-om": "Arabic/Oman",
    "ar-qa": "Arabic/Qatar",
    "ar-sa": "Arabic/Saudi Arabia",
    "ar-sy": "Arabic/Syria",
    "ar-tn": "Arabic/Tunisia",
    "ar-ye": "Arabic/Yemen",
    # Bulgarian
    "bg-bg": "Bulgarian/Bulgaria",
    # Catalan
    "ca-es": "Catalan/Spain",
    # Czech
    "cs-cz": "Czech/Czech Republic",
    # Welsh
    "cy-gb": "Welsh/UK",
    # Danish
    "da-dk": "Danish/Denmark",
    # German variants
    "de-at": "German/Austria",
    "de-ch": "German/Switzerland",
    "de-de": "German/Germany",
    "de-li": "German/Liechtenstein",
    "de-lu": "German/Luxembourg",
    # Greek
    "el-cy": "Greek/Cyprus",
    "el-gr": "Greek/Greece",
    # English variants
    "en-ae": "English/UAE",
    "en-al": "English/Albania",
    "en-am": "English/Armenia",
    "en-au": "English/Australia",
    "en-az": "English/Azerbaijan",
    "en-bh": "English/Bahrain",
    "en-bn": "English/Brunei",
    "en-bw": "English/Botswana",
    "en-by": "English/Belarus",
    "en-ca": "English/Canada",
    "en-eg": "English/Egypt",
    "en-gb": "English/UK",
    "en-ge": "English/Georgia",
    "en-gu": "English/Guam",
    "en-gw": "English/Guinea-Bissau",
    "en-hk": "English/Hong Kong",
    "en-ie": "English/Ireland",
    "en-il": "English/Israel",
    "en-in": "English/India",
    "en-is": "English/Iceland",
    "en-jo": "English/Jordan",
    "en-ke": "English/Kenya",
    "en-kg": "English/Kyrgyzstan",
    "en-kw": "English/Kuwait",
    "en-kz": "English/Kazakhstan",
    "en-lb": "English/Lebanon",
    "en-lk": "English/Sri Lanka",
    "en-md": "English/Moldova",
    "en-me": "English/Montenegro",
    "en-mk": "English/North Macedonia",
    "en-mn": "English/Mongolia",
    "en-mo": "English/Macau",
    "en-mt": "English/Malta",
    "en-my": "English/Malaysia",
    "en-mz": "English/Mozambique",
    "en-ng": "English/Nigeria",
    "en-nz": "English/New Zealand",
    "en-om": "English/Oman",
    "en-ph": "English/Philippines",
    "en-qa": "English/Qatar",
    "en-sa": "English/Saudi Arabia",
    "en-sg": "English/Singapore",
    "en-tj": "English/Tajikistan",
    "en-tm": "English/Turkmenistan",
    "en-ug": "English/Uganda",
    "en-us": "English/USA",
    "en-uz": "English/Uzbekistan",
    "en-vn": "English/Vietnam",
    "en-za": "English/South Africa",
    # Spanish variants
    "es-ar": "Spanish/Argentina",
    "es-bo": "Spanish/Bolivia",
    "es-cl": "Spanish/Chile",
    "es-co": "Spanish/Colombia",
    "es-cr": "Spanish/Costa Rica",
    "es-do": "Spanish/Dominican Republic",
    "es-ec": "Spanish/Ecuador",
    "es-es": "Spanish/Spain",
    "es-gt": "Spanish/Guatemala",
    "es-hn": "Spanish/Honduras",
    "es-mx": "Spanish/Mexico",
    "es-ni": "Spanish/Nicaragua",
    "es-pa": "Spanish/Panama",
    "es-pe": "Spanish/Peru",
    "es-py": "Spanish/Paraguay",
    "es-sv": "Spanish/El Salvador",
    "es-us": "Spanish/USA",
    "es-uy": "Spanish/Uruguay",
    "es-ve": "Spanish/Venezuela",
    # Estonian
    "et-ee": "Estonian/Estonia",
    # Basque
    "eu-es": "Basque/Spain",
    # Finnish
    "fi-fi": "Finnish/Finland",
    # French variants
    "fr-be": "French/Belgium",
    "fr-ca": "French/Canada",
    "fr-cf": "French/Central African Republic",
    "fr-ch": "French/Switzerland",
    "fr-ci": "French/Côte d'Ivoire",
    "fr-cm": "French/Cameroon",
    "fr-fr": "French/France",
    "fr-gn": "French/Guinea",
    "fr-gq": "French/Equatorial Guinea",
    "fr-lu": "French/Luxembourg",
    "fr-ma": "French/Morocco",
    "fr-mg": "French/Madagascar",
    "fr-ml": "French/Mali",
    "fr-mu": "French/Mauritius",
    "fr-ne": "French/Niger",
    "fr-sn": "French/Senegal",
    "fr-tn": "French/Tunisia",
    # Irish
    "ga-ie": "Irish/Ireland",
    # Galician
    "gl-es": "Galician/Spain",
    # Hebrew
    "he-il": "Hebrew/Israel",
    # Croatian
    "hr-hr": "Croatian/Croatia",
    # Hungarian
    "hu-hu": "Hungarian/Hungary",
    # Indonesian
    "id-id": "Indonesian/Indonesia",
    # Icelandic
    "is-is": "Icelandic/Iceland",
    # Italian variants
    "it-ch": "Italian/Switzerland",
    "it-it": "Italian/Italy",
    # Japanese
    "ja-jp": "Japanese/Japan",
    # Korean
    "ko-kr": "Korean/South Korea",
    # Lithuanian
    "lt-lt": "Lithuanian/Lithuania",
    # Latvian
    "lv-lv": "Latvian/Latvia",
    # Malay
    "ms-my": "Malay/Malaysia",
    # Maltese
    "mt-mt": "Maltese/Malta",
    # Norwegian variants
    # Note: Norwegian has three codes:
    # - nb-no: Norwegian Bokmål (most common written form, ~85% of population)
    # - nn-no: Norwegian Nynorsk (alternative written form, ~15% of population)
    # - no-no: Generic Norwegian (used by Apple, defaults to Bokmål)
    "nb-no": "Norwegian Bokmål/Norway",
    "nn-no": "Norwegian Nynorsk/Norway",
    "no-no": "Norwegian/Norway",
    # Dutch
    "nl-be": "Dutch/Belgium",
    "nl-nl": "Dutch/Netherlands",
    # Polish
    "pl-pl": "Polish/Poland",
    # Portuguese variants
    "pt-ao": "Portuguese/Angola",
    "pt-br": "Portuguese/Brazil",
    "pt-mz": "Portuguese/Mozambique",
    "pt-pt": "Portuguese/Portugal",
    # Romanian
    "ro-md": "Romanian/Moldova",
    "ro-ro": "Romanian/Romania",
    # Russian
    "ru-ru": "Russian/Russia",
    # Slovak
    "sk-sk": "Slovak/Slovakia",
    # Slovenian
    "sl-si": "Slovenian/Slovenia",
    # Serbian
    "sr-rs": "Serbian/Serbia",
    # Swedish
    "sv-se": "Swedish/Sweden",
    # Thai
    "th-th": "Thai/Thailand",
    # Turkish
    "tr-tr": "Turkish/Turkey",
    # Ukrainian
    "uk-ua": "Ukrainian/Ukraine",
    # Vietnamese
    "vi-vn": "Vietnamese/Vietnam",
    # Chinese variants
    "zh-cn": "Chinese/China",
    "zh-hk": "Chinese/Hong Kong",
    "zh-mo": "Chinese/Macau",
    "zh-sg": "Chinese/Singapore",
    "zh-tw": "Chinese/Taiwan",
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

    Language names are sorted alphabetically by language code.

    Args:
        language_names: Dictionary mapping language codes to names
        output_file: Path to the output JSON file (relative to project root)
    """
    # Resolve path relative to project root
    output_path = get_project_root() / output_file
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(language_names, f, indent=2, ensure_ascii=False, sort_keys=True)

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
        language_urls_file: Path to the language URLs JSON file
            (relative to project root)
        language_names_file: Path to the language names JSON file
            (relative to project root)
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
