import re
import shutil
from typing import List, Any
from itertools import zip_longest
from natsort import natsorted
from .chapter_utils import extract_chapter_number


def select_chapters_interactively(
    raw_chapters: List[Any], chapter_extractor: callable
) -> List[Any]:
    chapter_info = []
    for ch in raw_chapters:
        try:
            text = chapter_extractor(ch)
            num = extract_chapter_number(text)
            chapter_info.append(
                {
                    "element": ch,
                    "name": text,
                    "number": num,
                }
            )
        except (AttributeError, ValueError):
            continue

    if not chapter_info:
        print("[×] No chapters available.")
        return []

    chapter_info = natsorted(
        chapter_info, key=lambda x: (x["number"], x["name"].lower())
    )

    term_width = max(shutil.get_terminal_size().columns, 60)
    content_padding = 4
    min_col_width = 30
    pad_width = len(str(len(chapter_info)))

    def display_multi_column(items):
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

    def format_numbered_list(items, extractor=lambda x: x["name"]):
        return [
            f"{i+1:0{pad_width}d}. {extractor(item)}" for i, item in enumerate(items)
        ]

    while True:
        print("\033c", end="")  # Clear screen

        print(f"\n╔{'═' * (term_width - 2)}╗")
        print(f"║{'CHAPTER SELECTION'.center(term_width - 2)}║")
        print(f"╚{'═' * (term_width - 2)}╝")

        numbered_items = format_numbered_list(chapter_info)
        display_multi_column(numbered_items)

        print("─" * term_width)
        print(" " * content_padding + "SELECTION OPTIONS:")
        print(" " * content_padding + "all       - Select all chapters")
        print(" " * content_padding + "newestN   - Select newest N (e.g. 'newest5')")
        print(
            " " * content_padding + "x-y       - Select range by index (e.g. '10-20')"
        )
        print(" " * content_padding + "x,y,z     - Select specific indexes")
        print(" " * content_padding + ".x        - Select decimal chapters like .5")
        print(" " * content_padding + "s:term    - Filter chapters by name")
        print(
            " " * content_padding
            + "1.0       - Select chapter number exactly (e.g. 1.0)"
        )
        print(" " * content_padding + "q         - Quit selection")
        print("─" * term_width)

        selection = (
            input(" " * content_padding + "⌨  Enter selection: ").strip().lower()
        )

        if not selection:
            print("\n" + " " * content_padding + "[!] Please enter a selection")
            input(" " * content_padding + "Press Enter to continue...")
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
                    print(f"\n╔{'═' * (term_width - 2)}╗")
                    print(f"║{'FILTERED RESULTS'.center(term_width - 2)}║")
                    print(f"╚{'═' * (term_width - 2)}╝")
                    filtered_items = format_numbered_list(selected)
                    display_multi_column(filtered_items)

            else:
                num = float(selection)
                selected = [
                    ch for ch in chapter_info if abs(ch["number"] - num) < 0.001
                ]

            if not selected:
                print("\n" + " " * content_padding + "[!] No chapters matched")
                input(" " * content_padding + "Press Enter to continue...")
                continue

            print(f"\n╔{'═' * (term_width - 2)}╗")
            print(f"║{'SELECTED CHAPTERS'.center(term_width - 2)}║")
            print(f"╚{'═' * (term_width - 2)}╝")
            preview_items = format_numbered_list(selected)
            display_multi_column(preview_items)

            confirm = (
                input(" " * content_padding + "Confirm selection? [Y/n/q] ")
                .strip()
                .lower()
            )
            if confirm in ("y", ""):
                return [ch["element"] for ch in selected]
            elif confirm == "q":
                return []

        except Exception as e:
            print("\n" + " " * content_padding + f"[!] Error: {e}")
            input(" " * content_padding + "Press Enter to continue...")
