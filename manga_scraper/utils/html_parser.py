import re
from typing import List
from scrapy.http import Response


def extract_urls_from_qwik_json(response: Response) -> List[str]:
    """
    Extract all URL strings from the <script type="qwik/json"> tag in the response HTML,
    starting after the "manga-xxxxx" marker until the end of the script block.

    Args:
        response (Response): The Scrapy HTTP response object containing the HTML.

    Returns:
        List[str]: A list of extracted URLs appearing after "manga-xxxxx".
    """
    html = response.text

    # Match the <script type="qwik/json">...</script> content
    script_match = re.search(r'<script\s+type="qwik/json">([\s\S]*?)</script>', html)
    if not script_match:
        return []

    json_text = script_match.group(1)

    # Find the position of "manga-xxxxx"
    manga_match = re.search(r'"manga-\d+"', json_text)
    if not manga_match:
        return []

    # Slice from the end of "manga-xxxxx" match to the end of script content
    start_index = manga_match.end()
    json_tail = json_text[start_index:]

    # Extract all URLs in that tail (starting with http/https)
    urls = re.findall(r'"(https?://[^"]+)"', json_tail)

    return urls
