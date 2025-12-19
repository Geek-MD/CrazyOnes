#!/usr/bin/env python3
"""
Utility functions shared across the Apple Updates scraping modules.
"""


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
