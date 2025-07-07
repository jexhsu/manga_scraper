# manga_scraper/utils/chapter_filter.py
import re
from typing import List, Any
from itertools import zip_longest
from natsort import natsorted
from .display_utils import display_boxed_title, display_multi_column_items
from .chapter_utils import extract_chapter_number

def select_chapters_interactively(
    raw_chapters: List[Any], 
    chapter_extractor: callable
) -> List[Any]:
    """Interactive chapter selection with various filtering options."""
    chapter_info = []
    for ch in raw_chapters:
        try:
            text = chapter_extractor(ch)
            num = extract_chapter_number(text)
            chapter_info.append({
                "element": ch,
                "name": text,
                "number": num,
            })
        except (AttributeError, ValueError):
            continue

    if not chapter_info:
        print("[×] No chapters available.")
        return []

    chapter_info = natsorted(
        chapter_info, key=lambda x: (x["number"], x["name"].lower())
    )

    pad_width = len(str(len(chapter_info)))

    def format_numbered_list(items, extractor=lambda x: x["name"]):
        return [
            f"{i+1:0{pad_width}d}. {extractor(item)}" 
            for i, item in enumerate(items)
        ]

    while True:
        print("\033c", end="")  # Clear screen

        # Display boxed title
        term_width = display_boxed_title("CHAPTER SELECTION")

        # Display chapters
        numbered_items = format_numbered_list(chapter_info)
        display_multi_column_items(numbered_items, term_width)

        # Display options
        print("─" * term_width)
        print(" " * 4 + "SELECTION OPTIONS:")
        print(" " * 4 + "all       - Select all chapters")
        print(" " * 4 + "newestN   - Select newest N (e.g. 'newest5')")
        print(" " * 4 + "x-y       - Select range by index (e.g. '10-20')")
        print(" " * 4 + "x,y,z     - Select specific indexes")
        print(" " * 4 + ".x        - Select decimal chapters like .5")
        print(" " * 4 + "s:term    - Filter chapters by name")
        print(" " * 4 + "1.0       - Select chapter number exactly (e.g. 1.0)")
        print(" " * 4 + "q         - Quit selection")
        print("─" * term_width)

        selection = input(" " * 4 + "⌨  Enter selection: ").strip().lower()

        if not selection:
            print("\n" + " " * 4 + "[!] Please enter a selection")
            input(" " * 4 + "Press Enter to continue...")
            continue

        if selection == "q":
            return []

        try:
            selected = []

            if selection == "all":
                selected = chapter_info

            elif selection.startswith("newest"):
                n = int(selection[6:])
                selected = list(reversed(chapter_info[-n:]))

            elif "-" in selection and not re.search(r"[a-z]", selection):
                start, end = map(int, selection.split("-"))
                selected = chapter_info[start - 1 : end]

            elif "," in selection and not re.search(r"[a-z]", selection):
                indices = set(int(x) for x in selection.split(","))
                selected = [
                    ch for i, ch in enumerate(chapter_info, start=1) if i in indices
                ]

            elif selection.startswith("."):
                decimal_part = float("0" + selection)
                selected = [
                    ch
                    for ch in chapter_info
                    if not ch["number"].is_integer()
                    and abs(ch["number"] % 1 - decimal_part) < 0.001
                ]

            elif selection.startswith(("search:", "s:")):
                query = re.sub(r"^(search:|s:)", "", selection)
                selected = [ch for ch in chapter_info if query in ch["name"].lower()]

                if selected:
                    term_width = display_boxed_title("FILTERED RESULTS")
                    filtered_items = format_numbered_list(selected)
                    display_multi_column_items(filtered_items, term_width)

            else:
                # Try both index selection and chapter number selection
                try:
                    # First try as index (1-based)
                    index = int(selection) - 1
                    if 0 <= index < len(chapter_info):
                        selected = [chapter_info[index]]
                    else:
                        # Then try as chapter number
                        num = float(selection)
                        selected = [
                            ch for ch in chapter_info 
                            if abs(ch["number"] - num) < 0.001
                        ]
                except ValueError:
                    print("\n" + " " * 4 + "[!] Invalid selection")
                    input(" " * 4 + "Press Enter to continue...")
                    continue

            if not selected:
                print("\n" + " " * 4 + "[!] No chapters matched")
                input(" " * 4 + "Press Enter to continue...")
                continue

            term_width = display_boxed_title("SELECTED CHAPTERS")
            preview_items = format_numbered_list(selected)
            display_multi_column_items(preview_items, term_width)

            confirm = input(" " * 4 + "Confirm selection? [Y/n/q] ").strip().lower()
            if confirm in ("y", ""):
                return [ch["element"] for ch in selected]
            elif confirm == "q":
                return []

        except Exception as e:
            print("\n" + " " * 4 + f"[!] Error: {e}")
            input(" " * 4 + "Press Enter to continue...")