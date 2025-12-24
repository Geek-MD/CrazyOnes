#!/usr/bin/env python3
"""
Script to generate translation JSON files for all supported languages.

This script creates translation files (xx-yy.json) for each language code
in LANGUAGE_NAME_MAP. It uses strings.json (English) as the base template.

For now, all translations are in English. Users can manually translate
these files to their respective languages later.
"""

import json
from pathlib import Path

from generate_language_names import LANGUAGE_NAME_MAP


def load_base_strings() -> dict[str, str]:
    """
    Load the base English strings from strings.json.

    Returns:
        Dictionary with base string keys and values
    """
    script_dir = Path(__file__).parent
    translations_dir = script_dir / "translations"
    strings_file = translations_dir / "strings.json"
    
    if not strings_file.exists():
        raise FileNotFoundError("strings.json not found in scripts/translations directory")
    
    with open(strings_file, encoding="utf-8") as f:
        return json.load(f)


def generate_translation_file(lang_code: str, base_strings: dict[str, str]) -> None:
    """
    Generate a translation file for a specific language code.

    Args:
        lang_code: Language code (e.g., 'en-us', 'es-es')
        base_strings: Dictionary with base string keys and values
    """
    script_dir = Path(__file__).parent
    translations_dir = script_dir / "translations"
    translations_dir.mkdir(exist_ok=True)
    output_file = translations_dir / f"{lang_code}.json"
    
    # For now, use English strings as placeholder
    # Users can manually translate these files later
    translations = base_strings.copy()
    
    # Save the translation file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(translations, f, indent=2, ensure_ascii=False)
    
    print(f"Generated: {lang_code}.json")


def main() -> None:
    """Main function to generate all translation files."""
    print("=== Translation Files Generator ===\n")
    
    # Load base strings
    print("Loading base strings from strings.json...")
    try:
        base_strings = load_base_strings()
        print(f"Loaded {len(base_strings)} base strings\n")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    # Generate translation files for all languages
    print(f"Generating translation files for {len(LANGUAGE_NAME_MAP)} languages...\n")
    
    generated_count = 0
    for lang_code in sorted(LANGUAGE_NAME_MAP.keys()):
        try:
            generate_translation_file(lang_code, base_strings)
            generated_count += 1
        except Exception as e:
            print(f"Error generating {lang_code}.json: {e}")
    
    print(f"\n✓ Successfully generated {generated_count} translation files")
    print("\nNote: All files currently contain English text as placeholders.")
    print("Please manually translate each file to its respective language.")


if __name__ == "__main__":
    main()
