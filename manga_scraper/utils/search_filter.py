# manga_scraper/utils/search_filter.py
import re
import shutil
from typing import List, Any, Optional
from itertools import zip_longest
from difflib import get_close_matches


def display_results(
    items: List[str],
    title: str = "RESULTS",
    cols: int = 3,
    min_width: int = 60,
    max_width: int = 120,
    pad_width: int = None,  # Auto-calculate if None
) -> None:
    """
    Enhanced display function with smart zero-padding
    """
    if not items:
        return

    # Calculate padding width if not specified
    if pad_width is None:
        pad_width = len(str(len(items)))

    term_width = min(max(shutil.get_terminal_size().columns, min_width), max_width)
    numbered_items = [f"{i+1:0{pad_width}d}. {name}" for i, name in enumerate(items)]
    max_len = max(len(item) for item in numbered_items) + 2
    cols = max(1, min(cols, term_width // max_len))
    content_width = cols * max_len
    display_width = max(len(title) + 4, content_width)
    display_width = min(display_width, term_width)

    # Header with full-width borders
    print(f"\n╔{'═' * (display_width - 2)}╗")
    print(f"║{title.center(display_width - 2)}║")
    print(f"╚{'═' * (display_width - 2)}╝")

    # Multi-column display with consistent padding
    for row in zip_longest(*[iter(numbered_items)] * cols, fillvalue=""):
        row_text = " │ ".join(f"{name:<{max_len}}" for name in row).rstrip()
        print(f" {row_text.ljust(display_width - 2)}")


def select_manga_interactively(
    manga_list: List[Any], manga_name_extractor: callable
) -> Optional[Any]:
    """
    Interactive selection with smart zero-padding and consistent styling
    """
    if not manga_list:
        print("[×] No items found.")
        return None

    original_list = manga_list.copy()
    current_list = manga_list
    last_search = None
    pad_width = len(str(len(original_list)))  # Determine padding from total count

    while True:
        item_names = [manga_name_extractor(item).strip() for item in current_list]

        print("\033c", end="")
        if last_search:
            print(f"\n🔍 Filtered results for: '{last_search}'\n")

        # Use calculated pad_width for consistent numbering
        display_results(item_names, "MANGA SELECTION", cols=2, pad_width=pad_width)

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
                    # Use same padding for similar results
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
