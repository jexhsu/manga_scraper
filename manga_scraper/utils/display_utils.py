# manga_scraper/utils/display_utils.py
import shutil
import math
from typing import List

def calculate_display_width(s: str) -> int:
    """Calculate display width considering CJK characters as double-width."""
    width = 0
    for c in s:
        if "\u4e00" <= c <= "\u9fff" or c in ("│", "║", "═", "╔", "╗", "╚", "╝"):
            width += 2
        else:
            width += 1
    return width

def display_boxed_title(title: str, min_width: int = 60, max_width: int = 120) -> int:
    """
    Display a boxed title that spans the terminal width.
    Returns the actual terminal width used.
    """
    term_width = max(min(shutil.get_terminal_size().columns, max_width), min_width)
    print(f"\n╔{'═' * (term_width - 2)}╗")
    print(f"║{title.center(term_width - 2)}║")
    print(f"╚{'═' * (term_width - 2)}╝")
    return term_width

def display_multi_column_items(
    items: List[str],
    term_width: int,
    cols: int = None,
    content_padding: int = 4,
    min_col_width: int = 30,
    max_cols: int = 4
) -> None:
    """Display items in multiple columns with proper alignment."""
    if not items:
        return

    # Auto-calculate number of columns if not specified
    if cols is None:
        max_item_width = max(calculate_display_width(item) for item in items) + 2
        possible_cols = min(max_cols, term_width // max(min_col_width, max_item_width))
        cols = max(1, possible_cols)

        # Balance columns if last one would be too short
        rows_needed = math.ceil(len(items) / cols)
        last_col_items = len(items) % cols
        if last_col_items > 0 and last_col_items < cols / 2 and cols > 1:
            test_cols = cols - 1
            test_rows = math.ceil(len(items) / test_cols)
            if test_rows * test_cols - len(items) < test_cols / 2:
                cols = test_cols

    # Calculate column width and number of rows
    col_width = (term_width - content_padding) // cols
    rows = math.ceil(len(items) / cols)

    # Print items row by row with aligned columns
    for row_idx in range(rows):
        row_items = items[row_idx * cols : (row_idx + 1) * cols]
        row_text = " " * content_padding
        for item in row_items:
            display_width = calculate_display_width(item)
            space_padding = col_width - display_width
            row_text += item + " " * space_padding
        print(row_text.rstrip())