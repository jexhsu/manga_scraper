# manga_scraper/utils/print_chapter_status_grid.py
import shutil
import re


def print_chapter_completion_map(chapter_completed_map):
    """
    Prints chapter status as: number[✓] with compact alignment, number left, status right.
    Colors: green for success, red for failure.
    """
    if not chapter_completed_map:
        print("No chapter completion data available.")
        return

    GREEN = "\033[92m"
    RED = "\033[91m"
    RESET = "\033[0m"

    def chapter_sort_key(item):
        key_str = str(item[0])
        match = re.search(r"\d+", key_str)
        return (int(match.group()) if match else float("inf"), key_str.lower())

    sorted_items = sorted(chapter_completed_map.items(), key=chapter_sort_key)

    max_ch_len = max(len(str(ch)) for ch, _ in sorted_items)
    block_width = max_ch_len + 3  # number + [✓] or [×]
    spacing = 4  # spaces between blocks
    total_block = block_width + spacing

    term_width = shutil.get_terminal_size((80, 20)).columns
    blocks_per_line = max(1, term_width // total_block)

    print("\n📘 Chapter Completion Status:")

    line = []
    for idx, (chapter, done) in enumerate(sorted_items, 1):
        symbol = "✓" if done else "×"
        color = GREEN if done else RED
        block = f"{color}{str(chapter):>{max_ch_len}}[{symbol}]{RESET}"
        line.append(block)

        if idx % blocks_per_line == 0 or idx == len(sorted_items):
            print((" " * spacing).join(line))
            line = []
