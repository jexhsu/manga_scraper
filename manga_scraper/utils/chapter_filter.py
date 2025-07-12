# manga_scraper/utils/chapter_filter.py

import re
from typing import List, Any
from natsort import natsorted
from .display_utils import display_boxed_title, display_multi_column_items
from .chapter_utils import extract_chapter_number


def select_chapters_interactively(
    raw_chapters: List[Any], chapter_extractor: callable, debug_mode: bool = False
) -> List[Any]:
    """
    Interactive chapter selector with natural sorting and reusable display layout.

    Args:
        raw_chapters: Raw chapter objects
        chapter_extractor: Callable to extract name from each chapter
        debug_mode: If True, automatically select first chapter

    Returns:
        List of selected raw chapter objects
    """
    if debug_mode:
        if raw_chapters:
            print("[DEBUG] Auto-selecting first chapter only")
            return [raw_chapters[0]]
        return []

    chapter_info = []
    for ch in raw_chapters:
        try:
            name = chapter_extractor(ch)
            number = extract_chapter_number(name)
            chapter_info.append({"element": ch, "name": name, "number": number})
        except Exception:
            continue

    if not chapter_info:
        print("[×] No chapters available.")
        return []

    # Apply natural sorting: number first, then name
    chapter_info = natsorted(
        chapter_info, key=lambda x: (x["number"], x["name"].lower())
    )

    # Format chapter list with numbering
    pad_width = len(str(len(chapter_info)))
    numbered_items = [
        f"{i + 1:0{pad_width}d}. {item['name']}" for i, item in enumerate(chapter_info)
    ]

    while True:
        print("\033c", end="")  # Clear screen
        term_width = display_boxed_title("CHAPTER SELECTION")
        display_multi_column_items(numbered_items, term_width)

        print("─" * term_width)
        print("  SELECTION OPTIONS:")
        print("  all         - Select all chapters")
        print("  newestN     - Select newest N (e.g., newest5)")
        print("  x-y         - Index range (e.g., 10-20)")
        print("  x,y,z       - Specific indexes (e.g., 1,3,5)")
        print("  .x          - Select decimal chapters like .5")
        print("  s:term      - Filter by name keyword")
        print("  1.0         - Select by exact chapter number")
        print("  q           - Quit without selecting")
        print("─" * term_width)

        selection = input("⌨  Enter selection: ").strip().lower()

        if not selection:
            print("[!] Please enter a selection.")
            input("Press Enter to continue...")
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
                    print("\n")
                    term_width = display_boxed_title("FILTERED RESULTS")
                    filtered_items = [
                        f"{i + 1:0{pad_width}d}. {ch['name']}"
                        for i, ch in enumerate(selected)
                    ]
                    display_multi_column_items(filtered_items, term_width)

            else:
                num = float(selection)
                selected = [
                    ch for ch in chapter_info if abs(ch["number"] - num) < 0.001
                ]

            if not selected:
                print("[!] No chapters matched.")
                input("Press Enter to continue...")
                continue

            print("\n")
            term_width = display_boxed_title("SELECTED CHAPTERS")
            preview_items = [
                f"{i + 1:0{pad_width}d}. {ch['name']}" for i, ch in enumerate(selected)
            ]
            display_multi_column_items(preview_items, term_width)

            confirm = input("Confirm selection? [Y/n/q] ").strip().lower()
            if confirm in ("y", ""):
                return [ch["element"] for ch in selected]
            elif confirm == "q":
                return []

        except Exception as e:
            print(f"[!] Error: {e}")
            input("Press Enter to continue...")
