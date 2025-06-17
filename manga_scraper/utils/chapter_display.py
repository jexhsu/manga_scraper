def print_chapter_summary(chapter_map, preview_count=5, max_full_display=20):
    """
    Prints a concise summary of a chapter map (dictionary) with smart truncation.
    
    Features:
    - Works exclusively with dictionary input
    - Color-coded output for better readability
    - Detailed count of completed/incomplete chapters
    - Smart truncation with ellipsis
    - Progress percentage calculation
    
    Args:
        chapter_map (dict): Dictionary of chapters {chapter_key: completion_status}
        preview_count (int): Number of chapters to display at beginning/end when truncated
        max_full_display (int): Threshold for full display before truncating
    """
    if not isinstance(chapter_map, dict):
        raise ValueError("❌ Input must be a dictionary (chapter map)")
    
    total = len(chapter_map)
    completed = sum(1 for status in chapter_map.values() if status)
    completion_rate = (completed / total) * 100 if total > 0 else 0
    
    # Color codes
    COLOR_GREEN = '\033[92m'
    COLOR_YELLOW = '\033[93m'
    COLOR_END = '\033[0m'
    
    print(f"\n📊 {COLOR_YELLOW}CHAPTER MAP SUMMARY{COLOR_END}")
    print(f"📚 Total chapters: {total}")
    print(f"✅ Completed: {completed} ({completion_rate:.1f}%)")
    print(f"❌ Incomplete: {total - completed}")
    
    keys = list(chapter_map.keys())
    
    if total <= max_full_display:
        print("\n🔍 Full chapter list:")
        for key in keys:
            status = COLOR_GREEN + "✓" + COLOR_END if chapter_map[key] else COLOR_YELLOW + "✗" + COLOR_END
            print(f"  {status} {key}")
    else:
        print(f"\n🔍 First {preview_count} chapters:")
        for key in keys[:preview_count]:
            status = COLOR_GREEN + "✓" + COLOR_END if chapter_map[key] else COLOR_YELLOW + "✗" + COLOR_END
            print(f"  {status} {key}")
        
        print(f"\n⋯ {total - 2*preview_count} chapters hidden ⋯")
        
        print(f"\n🔍 Last {preview_count} chapters:")
        for key in keys[-preview_count:]:
            status = COLOR_GREEN + "✓" + COLOR_END if chapter_map[key] else COLOR_YELLOW + "✗" + COLOR_END
            print(f"  {status} {key}")