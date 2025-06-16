import shutil
import re

def print_chapter_completion_map(chapter_completed_map):
    """
    Pretty-prints the chapter completion status in a compact, color-coded block format.
    Adjusts items per line based on terminal width.
    """
    if not chapter_completed_map:
        print("No chapter completion data available.")
        return

    GREEN = "\033[92m"
    RED = "\033[91m"
    RESET = "\033[0m"

    def chapter_sort_key(item):
        chapter_key = str(item[0])
        match = re.search(r'\d+', chapter_key)
        return (int(match.group()) if match else float('inf'), chapter_key.lower())

    sorted_items = sorted(chapter_completed_map.items(), key=chapter_sort_key)

    max_key_length = max(len(str(key)) for key, _ in sorted_items)
    sample_entry = f"[{GREEN}✓{RESET}] {'ch'+str('9'*max_key_length)}"
    sample_width = len(sample_entry) + 3  # 3 spaces between items
    term_width = shutil.get_terminal_size((80, 20)).columns
    items_per_line = max(1, term_width // sample_width)

    print("\n📊 Chapter Completion Status:")
    line = []

    for i, (chapter, completed) in enumerate(sorted_items, 1):
        color = GREEN if completed else RED
        status = "✅" if completed else "❌"
        entry = f"[{color}{status}{RESET}] {str(chapter):>{max_key_length}}"
        line.append(entry)

        if i % items_per_line == 0 or i == len(sorted_items):
            print("   ".join(line))
            line = []
