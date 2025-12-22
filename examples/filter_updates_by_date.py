#!/usr/bin/env python3
"""
Example script showing how to filter updates by date using the new ISO date format.

The new JSON format includes:
- 'id': Ascending numeric ID for each update
- 'date': ISO 8601 format (YYYY-MM-DD) for easy filtering and sorting
"""

import json
from datetime import datetime
from pathlib import Path


def load_updates(language_code: str) -> list[dict]:
    """Load updates for a specific language."""
    file_path = Path(f"data/updates/{language_code}.json")
    if not file_path.exists():
        print(f"No updates file found for {language_code}")
        return []

    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


def filter_updates_after_date(updates: list[dict], date_str: str) -> list[dict]:
    """
    Filter updates to only those after a specific date.

    Args:
        updates: List of update dictionaries
        date_str: Date string in ISO format (YYYY-MM-DD)

    Returns:
        Filtered list of updates
    """
    cutoff_date = datetime.fromisoformat(date_str).date()
    filtered = []

    for update in updates:
        update_date = datetime.fromisoformat(update["date"]).date()
        if update_date > cutoff_date:
            filtered.append(update)

    return filtered


def filter_updates_in_date_range(
    updates: list[dict], start_date: str, end_date: str
) -> list[dict]:
    """
    Filter updates within a date range.

    Args:
        updates: List of update dictionaries
        start_date: Start date in ISO format (YYYY-MM-DD)
        end_date: End date in ISO format (YYYY-MM-DD)

    Returns:
        Filtered list of updates
    """
    start = datetime.fromisoformat(start_date).date()
    end = datetime.fromisoformat(end_date).date()
    filtered = []

    for update in updates:
        update_date = datetime.fromisoformat(update["date"]).date()
        if start <= update_date <= end:
            filtered.append(update)

    return filtered


def sort_updates_by_date(updates: list[dict], reverse: bool = True) -> list[dict]:
    """
    Sort updates by date.

    Args:
        updates: List of update dictionaries
        reverse: If True, sort newest first (default)

    Returns:
        Sorted list of updates
    """
    return sorted(updates, key=lambda x: x["date"], reverse=reverse)


def main():
    """Demonstrate filtering capabilities."""
    print("=== Example: Filtering Updates by Date ===\n")

    # Load updates (example with Spanish Chile)
    language_code = "es-cl"
    updates = load_updates(language_code)

    if not updates:
        print(f"No updates found for {language_code}")
        return

    print(f"Total updates: {len(updates)}\n")

    # Example 1: Filter updates after a specific date
    print("Example 1: Updates after 2024-01-15")
    filtered = filter_updates_after_date(updates, "2024-01-15")
    for update in filtered:
        print(f"  [{update['id']}] {update['date']}: {update['name']}")

    # Example 2: Filter updates in a date range
    print("\nExample 2: Updates between 2024-01-01 and 2024-01-31")
    filtered = filter_updates_in_date_range(updates, "2024-01-01", "2024-01-31")
    for update in filtered:
        print(f"  [{update['id']}] {update['date']}: {update['name']}")

    # Example 3: Sort updates by date (newest first)
    print("\nExample 3: All updates sorted by date (newest first)")
    sorted_updates = sort_updates_by_date(updates, reverse=True)
    for update in sorted_updates[:5]:  # Show first 5
        print(f"  [{update['id']}] {update['date']}: {update['name']}")

    # Example 4: Find updates by ID
    print("\nExample 4: Get update by ID")
    target_id = 2
    update = next((u for u in updates if u["id"] == target_id), None)
    if update:
        print(f"  Update #{target_id}:")
        print(f"    Name: {update['name']}")
        print(f"    Date: {update['date']}")
        print(f"    Target: {update['target']}")


if __name__ == "__main__":
    main()
