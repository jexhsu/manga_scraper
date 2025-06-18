import logging
from typing import List

logger = logging.getLogger(__name__)


def extract_raw_chapters(
    response,
    paginate: bool,
    paginator=None,
    chapter_list_selector: str = None,
    chapter_pattern: str = None,
) -> List[str]:
    """
    Extract raw chapter list from response, handling both paginated and non-paginated cases.

    Args:
        response: Scrapy response object
        paginate: Whether pagination is enabled
        paginator: Paginator object (if pagination is enabled)
        chapter_list_selector: CSS selector for chapters
        chapter_pattern: Regex pattern for chapter extraction

    Returns:
        List of raw chapter strings
    """
    logger.debug("Extracting raw chapters from URL: %s", response.url)

    if paginate:
        if not paginator:
            logger.error("Paginator is required when pagination is enabled")
            raise ValueError("Paginator must be provided when paginate=True")

        # If pagination is enabled, recursively fetch all pages
        paginator.extract_chapters(response)
        logger.debug(
            "Paginator extracted chapters. Has more pages: %s",
            paginator.has_more_pages,
        )
        raw_chapters = paginator.all_chapters
    else:
        if not chapter_list_selector or not chapter_pattern:
            logger.error(
                "Chapter list selector and pattern are required when pagination is disabled"
            )
            raise ValueError(
                "chapter_list_selector and chapter_pattern must be provided when paginate=False"
            )

        # Directly extract chapter identifiers without pagination
        raw_chapters = response.css(chapter_list_selector).re(chapter_pattern)
        logger.debug("Extracted raw chapters (non-paginated): %s", raw_chapters)

    logger.debug("Extracted %d raw chapters", len(raw_chapters))
    return raw_chapters
