# manga_scraper/utils/chapter_utils.py
import re


def extract_chapter_number(chapter_str: str) -> float:
    """
    Extract chapter number from a given chapter string.

    Supports:
        - Arabic numerals with '话' or '卷' (e.g. '103话', '5卷')
        - Chinese numerals (e.g. '第六卷附赠')
        - English formats like 'Vol.10.5', 'Ch.127'
        - Special cases like '番外', '短篇' are placed at the end

    Returns:
        A float chapter number for sorting.
        Special text chapters will be returned as large float values (e.g. 10000+).
    """
    s = str(chapter_str or "").strip()

    # Handle special pure-text chapters by sending them to the end
    if any(kw in s for kw in ["番外", "短篇", "附赠"]):
        return 10000.0  # Special chapters sorted at the end

    # Arabic numeral match (e.g. 103话, 5卷, Chapter 127)
    match = re.search(r"(\d+(?:\.\d+)?)", s)
    if match:
        return float(match.group(1))

    # Chinese numeral map
    chinese_numerals = {
        "零": 0,
        "〇": 0,
        "一": 1,
        "二": 2,
        "三": 3,
        "四": 4,
        "五": 5,
        "六": 6,
        "七": 7,
        "八": 8,
        "九": 9,
        "十": 10,
    }

    def chinese_to_number(text: str) -> int:
        """
        Convert simple Chinese numerals (up to 99) to integer.
        Examples: '十' => 10, '十二' => 12, '二十六' => 26
        """
        if not text:
            return 0
        if text == "十":
            return 10
        if text.startswith("十"):
            return 10 + chinese_numerals.get(text[1], 0)
        if "十" in text:
            parts = text.split("十")
            tens = chinese_numerals.get(parts[0], 0)
            ones = chinese_numerals.get(parts[1], 0) if len(parts) > 1 else 0
            return tens * 10 + ones
        return sum(chinese_numerals.get(c, 0) for c in text)

    # Match pattern like '第六话', '第十卷'
    zh_match = re.search(r"第([一二三四五六七八九十〇零]+)[话卷]", s)
    if zh_match:
        return float(chinese_to_number(zh_match.group(1)))

    # Default fallback
    return 0.0
