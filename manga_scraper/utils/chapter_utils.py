# manga_scraper/utils/chapter_utils.py
import re


def extract_chapter_number(chapter_str):
    """
    Extract chapter number from various string formats.

    Args:
        chapter_str (str): Chapter string in formats like:
            - 'Chapter 139.6'
            - 'Ch.139.5'
            - 'Vol.32 Ch.127'
            - 'Ch.000'

    Returns:
        float: Extracted chapter number (0.0 if not found)
    """
    match = re.search(
        r"(?:ch|chapter)\.?\s*(\d+\.?\d*)|(?:vol|volume)\.?\s*(\d+\.?\d*)",
        str(chapter_str or ""),
        re.IGNORECASE,
    )
    return float((match or [[], ["0"]]).group(1) or 0)
