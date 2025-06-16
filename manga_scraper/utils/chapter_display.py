def print_chapter_summary(chapters, preview_count=5, max_full_display=20):
    """
    Prints a concise summary of the chapter list, with truncation for large collections.

    If the total number of chapters is less than or equal to `max_full_display`,
    all chapters are printed. Otherwise, only the first and last `preview_count` chapters
    are shown. If input is a dictionary, only its keys are used for display.

    Args:
        chapters (Union[list, dict]): A list or dictionary of chapters to summarize.
            If a dictionary is provided, only its keys will be used.
        preview_count (int): Number of chapters to display at the beginning and end when truncated.
        max_full_display (int): Maximum number of chapters to display fully before truncating.
    """
    total = len(chapters)

    print(f"📚 Found {total} chapters")

    if isinstance(chapters, dict):
        keys = list(chapters.keys())
    else:
        keys = chapters

    if total <= max_full_display:
        print(f"📚 Chapter list: {keys}")
    else:
        print(f"📚 First {preview_count} chapters: {keys[:preview_count]}")
        print(f"📚 Last {preview_count} chapters: {keys[-preview_count:]}")
        print(f"📚 Total chapters: {total} (display truncated)")
