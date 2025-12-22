# Examples

This directory contains example scripts demonstrating how to use the updated JSON format with IDs and ISO dates.

## New JSON Format

Starting from this version, all update JSON files include:

1. **`id`**: Ascending numeric identifier for each update (1, 2, 3, ...)
2. **`date`**: ISO 8601 format (YYYY-MM-DD) for programmatic filtering and sorting

### Example JSON Structure

```json
[
  {
    "id": 1,
    "name": "watchOS 10.3",
    "target": "Apple Watch Series 4 y posterior",
    "date": "2024-01-22",
    "url": "https://support.apple.com/es-cl/120306"
  },
  {
    "id": 2,
    "name": "tvOS 17.3",
    "target": "Apple TV HD y Apple TV 4K (todos los modelos)",
    "date": "2024-01-22",
    "url": "https://support.apple.com/es-cl/120311"
  }
]
```

### Benefits

- **Easy Filtering**: Filter updates by date range programmatically
- **Simple Sorting**: Sort updates chronologically
- **Unique IDs**: Reference specific updates by their ID
- **Standard Format**: ISO 8601 is internationally recognized

## Available Examples

### filter_updates_by_date.py

Demonstrates how to:
- Filter updates after a specific date
- Filter updates within a date range
- Sort updates by date (newest or oldest first)
- Find updates by ID

**Usage:**

```bash
python3 examples/filter_updates_by_date.py
```

## Integration Notes

The existing code (including the Telegram bot) will continue to work without modifications. The `date` field is simply displayed differently:

- **Before**: `"22 de enero de 2024"` (locale-specific format)
- **After**: `"2024-01-22"` (ISO 8601 format)

Both formats are human-readable, but the ISO format enables programmatic date operations.
