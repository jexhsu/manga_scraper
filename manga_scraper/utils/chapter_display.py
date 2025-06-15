def print_chapter_summary(collection, preview_count=5, max_full_display=20):
    """
    Prints a compact chapter list summary, truncating large outputs.
    For dictionaries, uses only keys for display.

    Args:
        collection (Union[list, dict]): Chapters to summarize.
            Dictionaries will display keys only.
        preview_count (int): Chapters to show at start/end when truncated.
        max_full_display (int): Maximum chapters to display fully.
    """
    chapters = list(collection.keys()) if isinstance(collection, dict) else collection
    total = len(chapters)
    
    print(f"📚 Found {total} chapters")

    if total <= max_full_display:
        print(f"📚 Chapter list: {chapters}")
    else:
        print(f"📚 First {preview_count} chapters: {chapters[:preview_count]}")
        print(f"📚 Last {preview_count} chapters: {chapters[-preview_count:]}")
        print(f"📚 Total chapters: {total} (display truncated)")