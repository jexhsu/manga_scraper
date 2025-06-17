import os
from typing import Dict, List, Union
from pathlib import Path
from manga_scraper.utils.file_manager import remove_folder
from manga_scraper.utils.print_chapter_status_grid import print_chapter_completion_map
import logging

def check_chapter_completion_and_get_start_index(
    root_dir: str,
    site_name: str,
    chapter_map: Dict[Union[int, str], str],
    spider
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
    logger.info("🔍 Starting chapter completion check")
    
    completed_map: Dict[Union[int, str], bool] = {}
    pdf_dir = Path(root_dir) / site_name
    first_incomplete_index = None
    cleaning_allowed = True
    chapter_list = list(chapter_map.keys())
    
    # Ensure PDF directory exists
    pdf_dir.mkdir(parents=True, exist_ok=True)
    
    # First pass: Check completion status for all chapters
    logger.debug("📊 Checking completion status for all chapters")
    for i, key in enumerate(chapter_list):
        pdf_path = pdf_dir / f"chapter-{key}.pdf"
        completed_map[key] = pdf_path.exists()
        
        logger.debug(
            f"  - Chapter {key}: {'✅ Complete' if completed_map[key] else '❌ Incomplete'} "
            f"(Path: {pdf_path})"
        )
    
    # Update spider state and print visual status
    spider.chapter_completed_map = completed_map
    # Second pass: Handle cleaning and find first incomplete chapter
    logger.info("🧹 Processing chapter cleanup and identifying start point")
    for i, key in enumerate(chapter_list):
        if completed_map[key] and cleaning_allowed:
            logger.info(f"  - Chapter {key}: Already completed, cleaning temp files")
            folder = pdf_dir / f"chapter-{key}"
            
            try:
                remove_folder(str(folder))
                logger.debug(f"    ♻️ Successfully cleaned: {folder}")
            except Exception as e:
                logger.error(f"    🚨 Failed to clean {folder}: {str(e)}")
                
        elif not completed_map[key] and first_incomplete_index is None:
            first_incomplete_index = i
            cleaning_allowed = False
            logger.info(
                f"  - 🚩 First incomplete chapter found at index {i} (Chapter {key})"
            )
    
    # Determine final start index
    if first_incomplete_index is None:
        logger.info("🎯 All chapters already completed!")
        return len(chapter_list)
    
    logger.info(
        f"📌 Resuming download from chapter index {first_incomplete_index} "
        f"(Chapter {chapter_list[first_incomplete_index]})"
    )
    return first_incomplete_index