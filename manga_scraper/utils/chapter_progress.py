def check_and_log_chapter_progress(chapter_index, chapter_list, chapter_map):
    """
    Check chapter progress and log appropriate messages.
    
    Args:
        chapter_index (int): Current chapter index.
        chapter_list (list): List of chapters.
        chapter_map (dict): Map of chapters.
    
    Returns:
        bool: True if download should continue, False otherwise.
    """
    # Log start information
    start_chapter = chapter_index + 1
    print(f"\n📍 Starting download from chapter {start_chapter} at index {chapter_index}")

    # Check if all chapters are already completed
    if chapter_index >= len(chapter_list or chapter_map):
        print("🎉 All chapters already completed. Nothing to download.")
        return False
    
    if not chapter_list and not chapter_map:
        print("⚠️ No chapters found")
        return False
        
    return True