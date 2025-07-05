# manga_scraper/utils/chapter_utils.py
import re


def extract_chapter_number(chapter_str):
    """
    Extract chapter number from chapter string.

    Supports formats like:
        - 'Chapter 139.6'
        - 'Ch.139.5'
        - 'Vol.32 Ch.127'
        - 'Ch.000'
        - 'Vol 10.5'
    """
    s = str(chapter_str or "")
    match = re.search(
        r"(?:ch|chapter)\.?\s*(\d+(?:\.\d+)?)|(?:vol|volume)\.?\s*(\d+(?:\.\d+)?)",
        s,
        re.IGNORECASE,
    )
    try:
        return float(match.group(1) or match.group(2))
    except (AttributeError, ValueError):
        return 0.0
