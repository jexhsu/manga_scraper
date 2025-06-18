import re
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def create_chapter_map(raw_chapters: List[str]) -> Dict[str, str]:
    """
    Create a sorted chapter map from raw chapter URLs/identifiers.

    Args:
        raw_chapters: List of raw chapter strings extracted from the website

    Returns:
        Dictionary mapping normalized chapter keys to original raw values
    """
    logger.debug("Creating chapter map from %d raw chapters", len(raw_chapters))

    # Pattern to match chapter numbers (highest priority)
    chapter_pattern = re.compile(r"(?:ch|chapter)[-_]0*(\d+(?:-\d+)*)", re.IGNORECASE)
    # Pattern to extract just the content after volume number
    volume_content_pattern = re.compile(r"vol(?:ume)?[-_]\d+-(.+)$", re.IGNORECASE)

    descending_chapter_map = {}

    for raw in raw_chapters:
        # First try to find chapter number
        chapter_match = chapter_pattern.search(raw)
        if chapter_match:
            chapter_key = chapter_match.group(1)
        else:
            # If no chapter number, try to get just the volume content
            content_match = volume_content_pattern.search(raw)
            if content_match:
                chapter_key = content_match.group(1)  # Just the content part
            else:
                # Fallback to raw string
                chapter_key = raw

        descending_chapter_map[chapter_key] = raw
        logger.debug("Mapped chapter: %s -> %s", chapter_key, raw)

    # Safe sorting that handles both numeric and non-numeric keys
    def sort_key(item):
        # Try to extract a number from the key
        num_match = re.search(r"\d+", item[0])
        if num_match:
            return int(num_match.group())
        # For non-numeric keys (like volume content), put them at the end
        return float("inf")

    ascending_chapter_map = {
        k: v for k, v in sorted(descending_chapter_map.items(), key=sort_key)
    }

    logger.debug(
        "Final sorted chapter map created with %d entries", len(ascending_chapter_map)
    )
    return ascending_chapter_map
