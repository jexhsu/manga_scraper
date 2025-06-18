# manga_scraper/utils/pdf_utils.py

import os
import logging


def get_pdf_output_path(chapter_path: str) -> str:
    """
    Generate the corresponding PDF output path based on the chapter path.

    Args:
        chapter_path: Path to the chapter file/directory

    Returns:
        The generated PDF file path with the same basename in the same directory
        Example: '/path/to/chapter' -> '/path/to/chapter.pdf'
    """
    chapter_name = os.path.basename(chapter_path)
    output_dir = os.path.dirname(chapter_path)
    output_path = os.path.join(output_dir, f"{chapter_name}.pdf")
    logging.debug(f"Generated PDF output path: {output_path}")
    return output_path
