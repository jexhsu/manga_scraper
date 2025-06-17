# Extract image URLs from response, supporting both Playwright and regular Scrapy requests
import asyncio
from scrapy.http import Response

async def extract_image_urls(response: Response, spider) -> list:
    """
    Asynchronously extract image URLs from the response.
    
    Handles both Playwright-rendered pages and regular Scrapy responses.
    
    Args:
        response (scrapy.http.Response): The response object.
        spider (scrapy.Spider): The spider instance for configuration.
        
    Returns:
        list: List of extracted image URLs.
    """
    if "playwright_page" in response.meta:
        page = response.meta["playwright_page"]
        await page.wait_for_selector(spider.image_selector)
        img_elements = await page.query_selector_all(spider.image_selector)
        return [await el.get_attribute("src") for el in img_elements]
    else:
        return response.css(f"{spider.image_selector}::attr(src)").getall()