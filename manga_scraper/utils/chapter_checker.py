# manga_scraper/utils/chapter_checker.py
from typing import Dict, Union
from pathlib import Path
from manga_scraper.utils.file_manager import remove_folder
import logging


def check_chapter_completion_and_get_start_index(
    root_dir: str, site_name: str, chapter_map: Dict[Union[int, str], str], spider
) -> int:
    """
    Enhanced chapter completion checker with improved logging and error handling.

    Args:
        root_dir: Base download directory
        site_name: Name of the manga site (for subfolder)
        chapter_map: Dictionary mapping chapter keys to their identifiers
        spider: Spider instance for logging and state management

    Returns:
        Index of first incomplete chapter or total count if all complete
    """
    # Initialize logging context
    logger = logging.getLogger(__name__)
    logging.debug("Starting chapter completion check for site: %s", site_name)

    completed_map: Dict[Union[int, str], bool] = {}
    pdf_dir = Path(root_dir) / site_name
    first_incomplete_index = None
    cleaning_allowed = True
    chapter_list = list(chapter_map.keys())

    # Ensure PDF directory exists
    pdf_dir.mkdir(parents=True, exist_ok=True)
    logging.debug("PDF directory: %s", pdf_dir)

    # First pass: Check completion status for all chapters
    logging.debug("Checking completion status for %d chapters", len(chapter_list))
    for i, key in enumerate(chapter_list):
        pdf_path = pdf_dir / f"chapter-{key}.pdf"
        completed_map[key] = pdf_path.exists()

        logging.debug(
            "Chapter %s status: %s (Path: %s)",
            key,
            "Complete" if completed_map[key] else "Incomplete",
            pdf_path,
        )

    # Update spider state and print visual status
    spider.chapter_completed_map = completed_map
    logging.debug(
        "Updated spider chapter_completed_map with %d entries", len(completed_map)
    )

    # Second pass: Handle cleaning and find first incomplete chapter
    logging.debug("Processing chapter cleanup and identifying start point")
    for i, key in enumerate(chapter_list):
        if completed_map[key] and cleaning_allowed:
            logging.debug("Chapter %s already completed, cleaning temp files", key)
            folder = pdf_dir / f"chapter-{key}"

            try:
                remove_folder(str(folder))
                logging.debug("Successfully cleaned folder: %s", folder)
            except Exception as e:
                logging.debug("Failed to clean folder %s: %s", folder, str(e))

        elif not completed_map[key] and first_incomplete_index is None:
            first_incomplete_index = i
            cleaning_allowed = False
            logging.debug(
                "First incomplete chapter found at index %d (Chapter %s)", i, key
            )

    # Determine final start index
    if first_incomplete_index is None:
        logging.debug("All chapters already completed")
        return len(chapter_list)

    logging.debug(
        "Resuming download from chapter index %d (Chapter %s)",
        first_incomplete_index,
        chapter_list[first_incomplete_index],
    )
    return first_incomplete_index
