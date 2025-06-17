import os
from typing import List, Dict, Union
from manga_scraper.utils.file_manager import remove_folder
from manga_scraper.utils.print_chapter_status_grid import print_chapter_completion_map

def check_chapter_completion_and_get_start_index(root_dir, site_name, chapter_list, spider):
    """
    Determines which chapters have already been completed and returns the first incomplete chapter index.
    Updates completion map and prints status before making decisions.
    """
    completed_map: Dict[Union[int, str], bool] = {}
    pdf_dir = os.path.join(root_dir, site_name)
    first_incomplete_index = None
    cleaning_allowed = True  # Only clean folders in the first continuous completed block

    # First pass: Check all chapter statuses
    for i, key in enumerate(chapter_list):
        pdf_path = os.path.join(pdf_dir, f"chapter-{key}.pdf")
        completed_map[key] = os.path.isfile(pdf_path)

    # Update spider's completion map and print status
    spider.chapter_completed_map = completed_map
    print_chapter_completion_map(completed_map)

    # Second pass: Handle cleaning and find first incomplete
    for i, key in enumerate(chapter_list):
        if completed_map[key] and cleaning_allowed:
            print(f"\n✅ Chapter {key}: Already downloaded. Cleaning temp files...")
            folder = os.path.join(pdf_dir, f"chapter-{key}")
            remove_folder(folder)
        elif not completed_map[key] and first_incomplete_index is None:
            first_incomplete_index = i
            cleaning_allowed = False  # Stop cleaning after first gap

    return first_incomplete_index if first_incomplete_index is not None else len(chapter_list)