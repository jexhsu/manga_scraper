# manga_scraper/utils/chapter_filter.py
import re
import shutil
from typing import List, Any
from itertools import zip_longest
from .chapter_utils import extract_chapter_number  # Import the helper function


def select_chapters_interactively(
    raw_chapters: List[Any], chapter_extractor: callable
) -> List[Any]:
    """
    Enhanced chapter selection with:
    - Chapter extraction and sorting using chapter_utils
    - Proper zero-padded numbering
    - Multi-column display
    - Full-width headers
    - Left-aligned options
    """
    # Extract and sort chapters using chapter_utils
    chapter_info = []
    for ch in raw_chapters:
        try:
            text = chapter_extractor(ch)
            num = extract_chapter_number(text)  # Use the imported function
            chapter_info.append(
                {
                    "element": ch,
                    "name": text,
                    "number": num,
                    "sort_key": (int(num) if num.is_integer() else num, text.lower()),
                }
            )
        except (AttributeError, ValueError):
            continue

    if not chapter_info:
        print("[×] No chapters available.")
        return []

    # Sort chapters by number then by name
    chapter_info.sort(key=lambda x: x["sort_key"])

    # Calculate display parameters
    term_width = max(shutil.get_terminal_size().columns, 60)
    content_padding = 4
    min_col_width = 30
    pad_width = len(str(len(chapter_info)))  # Number of digits needed

    def display_multi_column(items):
        """Display items in smart columns"""
        if not items:
            return

        max_item_len = max(len(item) for item in items)
        num_cols = max(1, min(term_width // max(min_col_width, max_item_len + 4), 4))
        col_width = (term_width - content_padding) // num_cols

        for row in zip_longest(*[iter(items)] * num_cols, fillvalue=""):
            row_text = " " * content_padding
            for item in row:
                if item:
                    row_text += item.ljust(col_width)
            print(row_text.rstrip())

    def format_numbered_list(items, extractor=None):
        """Format with zero-padded numbers"""
        return [
            f"{i+1:0{pad_width}d}. {extractor(item) if extractor else item['name']}"
            for i, item in enumerate(items)
        ]

    while True:
        print("\033c", end="")  # Clear screen

        # Full-width header
        print(f"\n╔{'═' * (term_width - 2)}╗")
        print(f"║{'CHAPTER SELECTION'.center(term_width - 2)}║")
        print(f"╚{'═' * (term_width - 2)}╝")

        # Display sorted chapters
        numbered_items = format_numbered_list(chapter_info)
        display_multi_column(numbered_items)

        # Options section
        print("─" * term_width)
        print(" " * content_padding + "SELECTION OPTIONS:")
        print(" " * content_padding + "all       - Select all chapters")
        print(" " * content_padding + "newestN   - Select newest N (e.g. 'newest5')")
        print(" " * content_padding + "x-y       - Select range (e.g. '10-20')")
        print(" " * content_padding + "x,y,z     - Select specific chapters")
        print(" " * content_padding + ".x        - Select decimal chapters")
        print(" " * content_padding + "s:term    - Filter chapters")
        print(" " * content_padding + "q         - Quit selection")
        print("─" * term_width)

        selection = (
            input(" " * content_padding + "⌨  Enter selection: ").strip().lower()
        )

        # Process selection
        if not selection:
            print("\n" + " " * content_padding + "[!] Please enter a selection")
            input(" " * content_padding + "Press Enter to continue...")
            continue

        if selection == "q":
            return []

        try:
            selected = []
            if selection == "all":
                selected = [ch["element"] for ch in chapter_info]
                print(
                    "\n"
                    + " " * content_padding
                    + f"Selected all {len(selected)} chapters"
                )
            elif selection.startswith("newest"):
                n = int(selection[6:])
                selected = [ch["element"] for ch in reversed(chapter_info[-n:])]
                print("\n" + " " * content_padding + f"Selected newest {n} chapters")
            elif "-" in selection:
                start, end = map(float, selection.split("-"))
                selected = [
                    ch["element"] for ch in chapter_info if start <= ch["number"] <= end
                ]
                print("\n" + " " * content_padding + f"Selected chapters {start}-{end}")
            elif "," in selection:
                selected_numbers = set(map(float, selection.split(",")))
                selected = [
                    ch["element"]
                    for ch in chapter_info
                    if ch["number"] in selected_numbers
                ]
                print("\n" + " " * content_padding + f"Selected chapters: {selection}")
            elif selection.startswith("."):
                decimal = float(selection)
                selected = [
                    ch["element"]
                    for ch in chapter_info
                    if not ch["number"].is_integer()
                    and abs(ch["number"] % 1 - decimal) < 0.001
                ]
                print("\n" + " " * content_padding + f"Selected .{decimal} chapters")
            elif selection.startswith(("search:", "s:")):
                query = re.sub(r"^(search:|s:)", "", selection)
                selected = [
                    ch["element"] for ch in chapter_info if query in ch["name"].lower()
                ]
                print(
                    "\n"
                    + " " * content_padding
                    + f"Found {len(selected)} matching chapters"
                )

                if selected:
                    print(f"\n╔{'═' * (term_width - 2)}╗")
                    print(f"║{'FILTERED RESULTS'.center(term_width - 2)}║")
                    print(f"╚{'═' * (term_width - 2)}╝")
                    filtered_items = format_numbered_list(selected, chapter_extractor)
                    display_multi_column(filtered_items)
            else:
                num = float(selection)
                selected = [
                    ch["element"]
                    for ch in chapter_info
                    if abs(ch["number"] - num) < 0.001
                ]
                print("\n" + " " * content_padding + f"Selected chapter {num}")

            if not selected:
                print("\n" + " " * content_padding + "[!] No chapters matched")
                input(" " * content_padding + "Press Enter to continue...")
                continue

            # Preview selection
            print(f"\n╔{'═' * (term_width - 2)}╗")
            print(f"║{'SELECTED CHAPTERS'.center(term_width - 2)}║")
            print(f"╚{'═' * (term_width - 2)}╝")
            preview_items = format_numbered_list(selected, chapter_extractor)
            display_multi_column(preview_items)

            confirm = (
                input(" " * content_padding + "Confirm selection? [Y/n/q] ")
                .strip()
                .lower()
            )
            if confirm in ("y", ""):
                return selected
            elif confirm == "q":
                return []

        except Exception as e:
            print("\n" + " " * content_padding + f"[!] Error: {e}")
            input(" " * content_padding + "Press Enter to continue...")
