#!/usr/bin/env python3
"""
Utility functions shared across the Apple Updates scraping modules.
"""

import re
from datetime import datetime


def get_user_agent_headers() -> dict[str, str]:
    """
    Get HTTP headers with proper User-Agent for Apple requests.

    Returns:
        Dictionary with User-Agent header to avoid being blocked by Apple's servers
    """
    return {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }


def parse_date_to_iso(date_str: str) -> str:
    """
    Parse date string from various language formats to ISO 8601 format (YYYY-MM-DD).

    Supports multiple date formats across different languages including:
    - English: "11 Dec 2023", "December 11, 2023"
    - Spanish: "09 de enero de 2024", "11 dic 2023"
    - French: "11 déc. 2023", "11 décembre 2023"
    - German: "11. Dez. 2023", "11. Dezember 2023"
    - And many other language formats

    Args:
        date_str: Date string in various formats

    Returns:
        ISO 8601 formatted date string (YYYY-MM-DD) or original string if parsing fails
    """
    # Month name mappings for various languages
    month_mappings = {
        # English
        "jan": 1, "january": 1,
        "feb": 2, "february": 2,
        "mar": 3, "march": 3,
        "apr": 4, "april": 4,
        "may": 5,
        "jun": 6, "june": 6,
        "jul": 7, "july": 7,
        "aug": 8, "august": 8,
        "sep": 9, "sept": 9, "september": 9,
        "oct": 10, "october": 10,
        "nov": 11, "november": 11,
        "dec": 12, "december": 12,

        # Spanish
        "enero": 1, "ene": 1,
        "febrero": 2,
        "marzo": 3,
        "abril": 4, "abr": 4,
        "mayo": 5,
        "junio": 6,
        "julio": 7,
        "agosto": 8, "ago": 8,
        "septiembre": 9,
        "octubre": 10,
        "noviembre": 11,
        "diciembre": 12, "dic": 12,

        # French
        "janvier": 1, "janv": 1,
        "février": 2, "févr": 2, "fev": 2, "fevr": 2,
        "mars": 3,
        "avril": 4, "avr": 4,
        "mai": 5,
        "juin": 6,
        "juillet": 7, "juil": 7,
        "août": 8, "aout": 8,
        "septembre": 9,
        "octobre": 10,
        "novembre": 11,
        "décembre": 12, "decembre": 12, "déc": 12,

        # German
        "januar": 1, "jänner": 1,
        "februar": 2,
        "märz": 3, "marz": 3, "mrz": 3, "mär": 3,
        "juni": 6,
        "juli": 7,
        "oktober": 10, "okt": 10,
        "dezember": 12, "dez": 12,

        # Italian
        "gennaio": 1, "gen": 1,
        "febbraio": 2,
        "aprile": 4,
        "maggio": 5, "mag": 5,
        "giugno": 6, "giu": 6,
        "luglio": 7, "lug": 7,
        "settembre": 9, "set": 9,
        "ottobre": 10, "ott": 10,

        # Portuguese
        "janeiro": 1,
        "fevereiro": 2,
        "março": 3, "marco": 3,
        "maio": 5,
        "junho": 6,
        "julho": 7,
        "setembro": 9,

        # Dutch
        "januari": 1,
        "februari": 2,
        "maart": 3, "mrt": 3,
        "mei": 5,
        "augustus": 8,

        # Russian
        "января": 1, "янв": 1,
        "февраля": 2, "фев": 2,
        "марта": 3, "мар": 3,
        "апреля": 4, "апр": 4,
        "мая": 5,
        "июня": 6, "июн": 6,
        "июля": 7, "июл": 7,
        "августа": 8, "авг": 8,
        "сентября": 9, "сен": 9,
        "октября": 10, "окт": 10,
        "ноября": 11, "ноя": 11,
        "декабря": 12, "дек": 12,
    }

    # Clean the date string
    date_clean = date_str.strip().lower()

    # Try to parse numeric dates first (YYYY-MM-DD, DD/MM/YYYY, etc.)
    # Format: YYYY-MM-DD
    match = re.match(r'^(\d{4})-(\d{1,2})-(\d{1,2})$', date_clean)
    if match:
        return date_str.strip()  # Already in ISO format

    # Format: DD/MM/YYYY or DD-MM-YYYY
    match = re.match(r'^(\d{1,2})[/-](\d{1,2})[/-](\d{4})$', date_clean)
    if match:
        day, month, year = match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"

    # Remove common punctuation and words like "de", "of", etc.
    date_clean = re.sub(r'\bde\b|\bof\b|\.|,', ' ', date_clean)
    date_clean = re.sub(r'\s+', ' ', date_clean).strip()

    # Try to extract day, month name, and year
    # Pattern: "DD month YYYY" or "month DD YYYY"
    parts = date_clean.split()

    day = None
    month = None
    year = None

    for part in parts:
        # Check if it's a year (4 digits)
        if re.match(r'^\d{4}$', part):
            year = int(part)
        # Check if it's a day (1-2 digits, possibly with trailing period)
        elif re.match(r'^\d{1,2}\.?$', part):
            day = int(part.rstrip('.'))
        # Check if it's a month name
        else:
            part_clean = part.rstrip('.')
            if part_clean in month_mappings:
                month = month_mappings[part_clean]

    # If we successfully extracted all parts, format as ISO date
    if day is not None and month is not None and year is not None:
        try:
            # Validate the date
            datetime(year, month, day)
            return f"{year}-{month:02d}-{day:02d}"
        except ValueError:
            # Invalid date, return original
            pass

    # If parsing failed, return the original string
    return date_str
