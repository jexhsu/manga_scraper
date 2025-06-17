import logging

async def handle_spider_error(spider, request_or_response, error):
    """
    Centralized error handling for spider exceptions.
    
    Args:
        spider (scrapy.Spider): The spider instance.
        request_or_response (scrapy.Request|scrapy.Response): The request or response object.
        error (Exception): The exception that occurred.
    """
    chapter = request_or_response.meta.get('chapter', 'unknown')
    error_msg = str(error)
    
    if isinstance(error, str):  # Handle failure.value from errback
        logging.error(f"❌ Error in chapter {chapter}: {error_msg}")
    else:
        logging.error(f"❌ Critical error parsing chapter {chapter}: {error_msg}")
        logging.debug(f"Error details:", exc_info=True)
    
    if "ERR_CONNECTION_CLOSED" in error_msg:
        logging.info("🔄 Connection closed, will retry...")
        if hasattr(request_or_response, 'copy'):
            yield request_or_response.copy()
    else:
        logging.error("⏩ Skipping due to non-retryable error")
        for req in request_next_chapter(spider, spider.chapter_map if spider.chapter_map else spider.chapter_list):
            yield req
        return