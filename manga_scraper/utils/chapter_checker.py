from typing import Dict, Union
from pathlib import Path
from manga_scraper.utils.file_manager import remove_folder
import logging


def check_chapter_completion(
    root_dir: str, site_name: str, chapter_map: Dict[Union[int, str], str]
) -> Dict[Union[int, str], bool]:
    """
    Check completion status for all chapters.

    Args:
        root_dir: Base download directory
        site_name: Name of the manga site (for subfolder)
        chapter_map: Dictionary mapping chapter keys to their identifiers

    Returns:
        Dictionary mapping chapter keys to completion status (True/False)
    """
    logger = logging.getLogger(__name__)
    logger.debug("Starting chapter completion check for site: %s", site_name)

    completed_map: Dict[Union[int, str], bool] = {}
    pdf_dir = Path(root_dir) / site_name

    # Ensure PDF directory exists
    pdf_dir.mkdir(parents=True, exist_ok=True)
    logger.debug("PDF directory: %s", pdf_dir)

    # Check completion status for all chapters
    logger.debug("Checking completion status for %d chapters", len(chapter_map))
    for key in chapter_map.keys():
        pdf_path = pdf_dir / f"chapter-{key}.pdf"
        completed_map[key] = pdf_path.exists()

        logger.debug(
            "Chapter %s status: %s (Path: %s)",
            key,
            "Complete" if completed_map[key] else "Incomplete",
            pdf_path,
        )

    logger.debug("Completed chapter status check with %d entries", len(completed_map))
    return completed_map
