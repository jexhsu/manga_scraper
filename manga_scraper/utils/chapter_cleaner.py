from pathlib import Path
from typing import Dict, Union
from manga_scraper.utils.file_manager import remove_folder
import logging


def clean_completed_chapters(
    root_dir: str,
    site_name: str,
    chapter_completed_map: Dict[Union[int, str], bool],
) -> None:
    """
    Clean temporary folders for completed chapters.

    Args:
        root_dir: Base download directory
        site_name: Name of the manga site
        chapter_completed_map: Dictionary mapping chapter keys to completion status
    """
    logger = logging.getLogger(__name__)
    logger.debug("Starting cleaning of completed chapters")

    chapter_list = list(chapter_completed_map.keys())
    pdf_dir = Path(root_dir) / site_name

    for key in chapter_list:
        if chapter_completed_map[key]:
            logger.debug("Chapter %s already completed, cleaning temp files", key)
            folder = pdf_dir / f"chapter-{key}"

            try:
                remove_folder(str(folder))
                logger.debug("Successfully cleaned folder: %s", folder)
            except Exception as e:
                logger.debug("Failed to clean folder %s: %s", folder, str(e))

    logger.debug("Completed chapter cleaning process")
