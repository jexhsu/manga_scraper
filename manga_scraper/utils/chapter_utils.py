# manga_scraper/utils/chapter_utils.py
import re


def extract_chapter_number(chapter_str):
    """
    Extract chapter number from various string formats, including:
      - 'Ch.139.5', 'Volume 3 Chapter 1', 'ajin-chapter-83', etc.

    Args:
        chapter_str (str): The input string containing chapter info.

    Returns:
        int | float | str: Returns numeric chapter (int or float) if matched,
                           or string like 'chapter-83' if hyphen style is matched,
                           or 0 if nothing is found.
    """
    text = str(chapter_str or "")

    # First, try to extract float/int from dot formats like 'Ch.123.5', 'Chapter 139'
    match = re.search(
        r"(?:ch|chapter)\.?\s*(\d+(?:\.\d+)?)|(?:vol|volume)\.?\s*(\d+(?:\.\d+)?)",
        text,
        re.IGNORECASE,
    )
    if match:
        num_str = match.group(1) or match.group(2)
        try:
            num = float(num_str)
            return int(num) if num.is_integer() else num
        except ValueError:
            pass

    # Second, try to extract hyphen-style chapter name like 'chapter-83'
    match2 = re.search(r"(ch(?:apter)?-\d+(?:\.\d+)?)", text, re.IGNORECASE)
    if match2:
        return match2.group(1).lower()

    # Fallback
    return 0
