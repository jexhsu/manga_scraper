# manga_scraper/utils/search_filter.py
import re
from typing import List, Any, Optional
from difflib import get_close_matches
from .display_utils import (
    display_boxed_title,
    display_multi_column_items,
)


def display_results(
    items: List[str],
    title: str = "RESULTS",
    cols: int = None,
    min_width: int = 60,
    max_width: int = 120,
    pad_width: int = None,
    max_cols: int = 4,
) -> None:
    """Display a list of items with boxed title and multi-column layout."""
    if not items:
        return

    # Determine prefix number width if not provided
    pad_width = pad_width or len(str(len(items)))

    # Format each item with numbered prefix
    numbered_items = [f"{i+1:0{pad_width}d}. {name}" for i, name in enumerate(items)]

    # Display the boxed title and get terminal width
    term_width = display_boxed_title(title, min_width, max_width)

    # Display items in columns
    display_multi_column_items(numbered_items, term_width, cols=cols, max_cols=max_cols)


def select_manga_interactively(
    manga_list: List[Any],
    manga_name_extractor: callable,
    debug_choice: Optional[int] = None,
) -> Optional[Any]:
    """Interactive manga selection or auto-select in debug mode."""
    if not manga_list:
        print("[×] No manga items found.")
        return None

    if debug_choice is not None:
        if 0 <= debug_choice < len(manga_list):
            print(
                f"[DEBUG] Auto-selected manga #{debug_choice + 1}: {manga_name_extractor(manga_list[debug_choice])}"
            )
            return manga_list[debug_choice]
        else:
            print("[DEBUG] debug_choice index out of range.")
            return None

    original_list = manga_list.copy()
    current_list = manga_list
    last_search = None
    pad_width = len(str(len(original_list)))

    while True:
        item_names = [manga_name_extractor(item).strip() for item in current_list]

        print("\033c", end="")  # Clear terminal
        if last_search:
            print(f"\n🔍 Filtered results for: '{last_search}'\n")

        # Display list with fixed-width title
        display_results(item_names, "MANGA SELECTION", cols=None, pad_width=pad_width)

        # Display input help
        help_text = [
            "\nSELECTION OPTIONS:",
            f" • 1-{len(current_list)}       - Select by number",
            " • s:term     - Filter items (e.g. 's:naruto')",
            " • r          - Reset filters" if last_search else "",
            " • q          - Quit selection",
            "―" * 40,
        ]
        print("\n".join(filter(None, help_text)))

        selection = input("\n⌨  Enter selection: ").strip().lower()

        if not selection:
            print("\n[!] Please enter a valid selection")
            input("↵ Press Enter to continue...")
            continue

        if selection == "q":
            return None

        if selection == "r" and last_search:
            current_list = original_list.copy()
            last_search = None
            continue

        if selection.startswith(("search:", "s:")):
            query = re.sub(r"^(search:|s:)", "", selection)
            if not query:
                print("\n[!] Please enter a search term")
                input("↵ Press Enter to continue...")
                continue

            last_search = query
            current_list = [
                item
                for item in original_list
                if query.lower() in manga_name_extractor(item).lower()
            ]

            if not current_list:
                print(f"\n[!] No results for '{query}'. Similar titles:")
                all_names = [manga_name_extractor(item) for item in original_list]
                similar = get_close_matches(query, all_names, n=5, cutoff=0.3)
                if similar:
                    display_results(
                        similar, "SIMILAR TITLES", cols=1, pad_width=pad_width
                    )
                input("↵ Press Enter to continue...")
                current_list = original_list.copy()
                last_search = None
            continue

        try:
            selected_index = int(selection) - 1
            if 0 <= selected_index < len(current_list):
                selected_item = current_list[selected_index]
                selected_name = manga_name_extractor(selected_item)

                print(f"\n✔ Selected: {selected_name}")
                confirm = input("↵ Confirm selection? [Y/n/r/q] ").strip().lower()

                if confirm in ("y", ""):
                    return selected_item
                elif confirm == "r":
                    current_list = original_list.copy()
                    last_search = None
                    continue
                elif confirm == "q":
                    return None
                continue

            print(f"[!] Please enter 1-{len(current_list)}")
            input("↵ Press Enter to continue...")

        except ValueError:
            print("[!] Invalid input. Use number, 's:term', 'r' or 'q'")
            input("↵ Press Enter to continue...")
