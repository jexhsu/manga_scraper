def print_chapter_summary(chapter_list, preview_count=5, max_full_display=20):
    """
    Print a concise summary of the chapter list to avoid flooding the console,
    especially when the chapter count is large.
    
    Args:
        chapter_list (list): List of unique chapters (usually strings or numbers).
        preview_count (int): Number of chapters to show at start and end if truncated.
        max_full_display (int): Maximum number of chapters to print fully.
    """
    total = len(chapter_list)
    print(f"📚 Found {total} unique chapters")

    if total > max_full_display:
        print(f"📚 First {preview_count} chapters: {chapter_list[:preview_count]}")
        print(f"📚 Last {preview_count} chapters: {chapter_list[-preview_count:]}")
        print(f"📚 Total chapters: {total}. Use pagination or filtering to view all chapters.")
    else:
        print(f"📚 Unique chapter list: {chapter_list}")
