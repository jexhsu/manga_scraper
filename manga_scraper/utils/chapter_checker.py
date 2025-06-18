from typing import Dict, Union
from pathlib import Path
import logging
import shutil


def check_chapter_completion(
    root_dir: str, site_name: str, chapter_map: Dict[Union[int, str], str]
) -> Dict[Union[int, str], bool]:
    """
    Check completion status for all chapters and clean up failed folders.

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
    raw_dir = pdf_dir / "raw"  # Assuming raw chapters are stored here

    # Ensure directories exist
    pdf_dir.mkdir(parents=True, exist_ok=True)
    if not raw_dir.exists():
        raw_dir.mkdir()

    logger.debug("PDF directory: %s | Raw directory: %s", pdf_dir, raw_dir)

    # Check completion status for all chapters
    logger.debug("Checking completion status for %d chapters", len(chapter_map))
    for key, chapter_id in chapter_map.items():
        pdf_path = pdf_dir / f"chapter-{key}.pdf"
        chapter_folder = raw_dir / str(chapter_id)  # Original folder
        failed_folder = raw_dir / f"{chapter_id}-xxx"  # Marked as failed

        # Case 1: PDF exists → Completed
        if pdf_path.exists():
            completed_map[key] = True
            logger.debug("Chapter %s: Complete (PDF exists)", key)
            continue

        # Case 2: Failed folder exists → Delete it and mark as incomplete
        if failed_folder.exists():
            shutil.rmtree(failed_folder)
            completed_map[key] = False
            logger.warning("Deleted failed chapter folder: %s", failed_folder)
            continue

        # Case 3: Original folder exists but no PDF → Incomplete
        if chapter_folder.exists():
            completed_map[key] = False
            logger.debug("Chapter %s: Incomplete (No PDF but folder exists)", key)
        else:
            # Case 4: No folder or PDF → Assume not downloaded
            completed_map[key] = False
            logger.debug("Chapter %s: Not downloaded", key)

    logger.debug("Completed status check. Results: %s", completed_map)
    return completed_map
