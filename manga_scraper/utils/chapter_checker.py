import os
from typing import List, Dict, Union
from manga_scraper.utils.file_manager import remove_folder

def check_chapter_completion_and_get_start_index(root_dir, site_name, chapter_list, spider):
    """
    Determines which chapters have already been completed (i.e., their corresponding PDFs exist),
    cleans up their temporary folders if allowed, and returns the index of the first incomplete chapter.

    Behavior:
    - Iterates over the provided chapter list (could be a list of chapter keys or chapter numbers).
    - For each chapter:
        - Checks if the corresponding PDF exists.
        - If completed and within the first continuous completed block, logs and deletes the folder.
        - If not completed, marks the index as the starting point for further downloads.
    - Updates `spider.chapter_completed_map` with chapter completion statuses.
    - Returns:
        - The index of the first incomplete chapter.
        - If all chapters are complete, returns the length of the chapter list.
    
    Parameters:
    - root_dir (str): Root directory where PDFs are stored.
    - site_name (str): Name of the manga site (used to locate the subfolder).
    - chapter_list (List[Union[int, str]]): List of chapter identifiers.
    - spider (object): The spider instance whose `chapter_completed_map` will be updated.
    """

    completed_map: Dict[Union[int, str], bool] = {}
    pdf_dir = os.path.join(root_dir, site_name)

    first_incomplete_index = None
    cleaning_allowed = True  # Only clean folders in the first continuous completed block

    for i, key in enumerate(chapter_list):
        pdf_path = os.path.join(pdf_dir, f"chapter-{key}.pdf")
        is_completed = os.path.isfile(pdf_path)
        completed_map[key] = is_completed

        if is_completed and cleaning_allowed:
            print(f"\n✅ Chapter {key}: This chapter has already been downloaded. Skipping...")
            folder = os.path.join(pdf_dir, f"chapter-{key}")
            remove_folder(folder)
        elif not is_completed and first_incomplete_index is None:
            first_incomplete_index = i
            cleaning_allowed = False  # Stop cleaning after the first incomplete chapter

    spider.chapter_completed_map = completed_map

    return first_incomplete_index if first_incomplete_index is not None else len(chapter_list)
