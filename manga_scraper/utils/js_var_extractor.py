#  manga_scraper/utils/js_var_extractor.py
import re
from scrapy.http import Response
from typing import Optional


def extract_js_var(response: Response, length: int = 16) -> Optional[str]:
    """
    Extract the value of any JavaScript variable assignment from <script> tags
    where the value is exactly of given length.

    Args:
        response (scrapy.Response): Scrapy Response object containing HTML.
        length (int): Expected length of the variable value. Default is 16.

    Returns:
        str | None: The first matching variable value of exact length, or None if not found.
    """
    # Combine all inline script contents into one text block
    script_text = "".join(response.css("script::text").getall())

    # Match pattern like: var xyz = 'xxxxxxxxxxxxxxxx';
    pattern = rf"var\s+\w+\s*=\s*['\"]([^'\"]{{{length}}})['\"]"
    match = re.search(pattern, script_text)

    if match:
        return match.group(1)
    return None
