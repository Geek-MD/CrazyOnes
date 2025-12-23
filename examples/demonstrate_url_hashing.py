#!/usr/bin/env python3
"""
Demonstration script showing how URL content hashing optimization works.

This script demonstrates the optimization strategy:
1. Always download content from URL (HTTP request is necessary)
2. Compute SHA256 hash of the downloaded content
3. Compare with stored hash
4. If hash matches → skip expensive HTML parsing
5. If hash differs → proceed with full analysis

This optimization saves significant processing time by avoiding HTML parsing
when content hasn't changed, while still detecting any updates to the page.
"""

import sys
from pathlib import Path

# Add parent directory to path to import from scripts
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.monitor_apple_updates import compute_content_hash


def demonstrate_optimization():
    """Demonstrate the URL content hashing optimization."""
    print("=" * 70)
    print("URL Content Hashing Optimization Demonstration")
    print("=" * 70)
    print()

    # Simulate downloaded content from first check
    print("Step 1: First check - downloading content from URL")
    print("-" * 70)
    content_v1 = """
    <html>
    <body>
        <h2>Apple security updates</h2>
        <table>
            <tr><td>iOS 17.2</td><td>iPhone XS and later</td><td>11 Dec 2023</td></tr>
            <tr><td>macOS Sonoma 14.2</td><td>macOS Sonoma</td><td>11 Dec 2023</td></tr>
        </table>
    </body>
    </html>
    """

    hash_v1 = compute_content_hash(content_v1)
    print("Content downloaded (simulated HTTP request)")
    print(f"Content hash: {hash_v1[:16]}...")
    print("Action: Full analysis performed (extract table, parse dates, etc.)")
    print(f"Stored hash: {hash_v1[:16]}... for future comparisons")
    print()

    # Simulate second check - content unchanged
    print("Step 2: Second check - content unchanged")
    print("-" * 70)
    content_v2 = content_v1  # Same content
    hash_v2 = compute_content_hash(content_v2)
    print("Content downloaded (simulated HTTP request)")
    print(f"Content hash: {hash_v2[:16]}...")
    print(f"Stored hash:  {hash_v1[:16]}...")

    if hash_v2 == hash_v1:
        print("✓ Hashes match → Content unchanged")
        print("⚡ OPTIMIZATION: Skip expensive HTML parsing and table extraction")
        print("   This saves significant processing time!")
    else:
        print("Hash differs → Content changed, perform full analysis")

    print()

    # Simulate third check - content changed
    print("Step 3: Third check - content updated (new iOS version)")
    print("-" * 70)
    content_v3 = """
    <html>
    <body>
        <h2>Apple security updates</h2>
        <table>
            <tr><td>iOS 17.3</td><td>iPhone XS and later</td><td>22 Jan 2024</td></tr>
            <tr><td>macOS Sonoma 14.3</td><td>macOS Sonoma</td><td>22 Jan 2024</td></tr>
        </table>
    </body>
    </html>
    """

    hash_v3 = compute_content_hash(content_v3)
    print("Content downloaded (simulated HTTP request)")
    print(f"Content hash: {hash_v3[:16]}...")
    print(f"Stored hash:  {hash_v1[:16]}...")

    if hash_v3 != hash_v1:
        print("✗ Hashes differ → Content has changed!")
        print("Action: Perform full analysis (extract table, parse dates, etc.)")
        print(f"Update stored hash: {hash_v3[:16]}...")
    else:
        print("Hashes match → Skip analysis")

    print()

    # Summary
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print()
    print("Benefits of this approach:")
    print("  ✓ Always downloads content (ensures we detect changes)")
    print("  ✓ Fast hash comparison (SHA256 is very efficient)")
    print("  ✓ Skips expensive HTML parsing when content unchanged")
    print("  ✓ Detects even minor changes in content")
    print()
    print("Performance impact:")
    print("  • Content download: ~100-500ms (unavoidable, necessary)")
    print("  • Hash computation: ~1-5ms (very fast)")
    print("  • HTML parsing: ~50-200ms (expensive, skipped when unchanged)")
    print()
    print("Result: Significant time savings when content doesn't change!")
    print()


if __name__ == "__main__":
    demonstrate_optimization()
