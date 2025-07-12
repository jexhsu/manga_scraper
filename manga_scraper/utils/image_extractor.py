import re
import json
from manga_scraper.utils.lzstring import (
    LZString,
)


def unpack_javascript(p, a, c, k):
    def base36(n):
        return str(n) if n < 10 else chr(ord("a") + n - 10)

    def encode(c):
        return ("" if c < a else encode(c // a)) + (
            chr(c % a + 29) if c % a > 35 else base36(c % a)
        )

    for i in range(c - 1, -1, -1):
        if i < len(k) and k[i]:
            pattern = re.compile(r"\b" + re.escape(encode(i)) + r"\b")
            p = pattern.sub(k[i], p)

    return p


def extract_manhua_image_urls(response, spider=None):
    """
    Extract obfuscated image URLs from manhuagui comic chapter page response.

    Parameters:
        response: Scrapy HtmlResponse
    Returns:
        List[str]: List of full image URLs
    """
    try:
        html = response.text

        pattern = r'window\["\\x65\\x76\\x61\\x6c"\]\(function\(p,a,c,k,e,d\)\{.*?\}\((\'[^\']*\')\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\'[^\']*\')\s*\[\'\\x73\\x70\\x6c\\x69\\x63\'\]\(\'\\x7c\'\)\s*,\s*\d+\s*,\s*\{\}\)\)'
        match = re.search(pattern, html, re.DOTALL)
        if not match:
            if spider:
                spider.logger.warning("Obfuscated JS not found.")
            return []

        p = match.group(1).strip("'")
        a = int(match.group(2))
        c = int(match.group(3))
        e = match.group(4).strip("'")
        k = LZString.decompressFromBase64(e).split("|")

        unpacked_js = unpack_javascript(p, a, c, k)

        json_match = re.search(
            r"SMH\.imgData\((\{.*?\})\)\.preInit\(\);", unpacked_js, re.DOTALL
        )
        if not json_match:
            if spider:
                spider.logger.warning("Image metadata JSON not found.")
            return []

        data = json.loads(json_match.group(1))
        base_url = "https://eu2.hamreus.com"
        path = data["path"]

        full_urls = [f"{base_url}{path}{f}" for f in data["files"]]
        return full_urls

    except Exception as e:
        if spider:
            spider.logger.error(f"Failed to extract image URLs: {e}")
        return []
