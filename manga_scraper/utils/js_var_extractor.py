# manga_scraper/utils/js_var_extractor.py
import re
from scrapy.http import Response


def extract_js_var(response: Response, var_name: str) -> str:
    """
    Extract the value of a JavaScript variable from inline <script> tags in the response HTML.

    Args:
        response (scrapy.Response): The HTTP response object containing HTML.
        var_name (str): The name of the JavaScript variable to extract.

    Returns:
        str: The extracted value of the JavaScript variable.

    Raises:
        ValueError: If the variable is not found in any <script> tag.
    """
    # Join all JavaScript code inside <script> tags into a single string
    script_text = "".join(response.css("script::text").getall())

    # Regex pattern to find: var var_name = 'value' or "value"
    pattern = rf"var\s+{re.escape(var_name)}\s*=\s*['\"]([^'\"]+)['\"]"
    match = re.search(pattern, script_text)

    if match:
        return match.group(1)

    # Not found, raise error for debug
    raise ValueError(f"JavaScript variable '{var_name}' not found in any <script> tag.")
