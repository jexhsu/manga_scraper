from typing import Dict, Union
import logging


def get_start_index(chapter_completed_map: Dict[Union[int, str], bool]) -> int:
    """
    Find the first incomplete chapter index.

    Args:
        chapter_completed_map: Dictionary mapping chapter keys to completion status

    Returns:
        Index of first incomplete chapter or total count if all complete
    """
    logger = logging.getLogger(__name__)
    logger.debug("Identifying first incomplete chapter")

    chapter_list = list(chapter_completed_map.keys())

    for i, key in enumerate(chapter_list):
        if not chapter_completed_map[key]:
            logger.debug(
                "First incomplete chapter found at index %d (Chapter %s)", i, key
            )
            return i

    logger.debug("All chapters already completed")
    return len(chapter_list)
