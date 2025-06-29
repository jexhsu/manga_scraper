# manga_scraper/utils/chapter_filter.py
import re
import shutil
from typing import List, Any
from itertools import zip_longest


def display_chapters(chapter_names: list[str], title: str = "AVAILABLE CHAPTERS", ascending: bool = True) -> None:
    """
    Display chapters with perfectly aligned header and content.

    Args:
        chapter_names: List of chapter names
        title: Header title
        ascending: Sort order (True for ascending)
    """
    def natural_sort_key(s):
        return [
            float(part) if part.replace(".", "", 1).isdigit() else part.lower()
            for part in re.split(r"([0-9.]+)", s)
        ]

    sorted_chapters = sorted(chapter_names, key=natural_sort_key, reverse=not ascending)

    # Get terminal width with reasonable constraints
    term_width = min(max(shutil.get_terminal_size().columns, 60), 120)
    
    # Calculate optimal column layout
    max_len = max(len(name) for name in sorted_chapters) + 2
    cols = max(1, min(6, term_width // max_len))
    content_width = cols * max_len
    
    # Ensure header width matches content width
    display_width = max(len(title) + 4, content_width)
    display_width = min(display_width, term_width)  # Don't exceed terminal width
    
    # Print perfectly aligned header
    print(f"\n{title.center(display_width)}")
    print("─" * display_width)

    # Display chapters in perfectly aligned columns
    for row in zip_longest(*[iter(sorted_chapters)] * cols, fillvalue=""):
        row_text = " ".join(f"{name:<{max_len}}" for name in row).rstrip()
        # Pad the row to full display width
        print(row_text.ljust(display_width))


def select_chapters_interactively(
    raw_chapters: List[Any], chapter_extractor: callable
) -> List[Any]:
    """
    Interactive chapter selection with perfectly aligned display.
    """
    # Extract and sort chapters with error handling
    chapter_info = []
    for ch in raw_chapters:
        try:
            text = chapter_extractor(ch)
            num = float(re.search(r"\d+\.?\d*", text).group())
            chapter_info.append({"element": ch, "name": text, "number": num})
        except (AttributeError, ValueError):
            continue

    if not chapter_info:
        print("[ERROR] No chapters found to select from.")
        return []

    while True:
        # Clear screen and display available chapters
        print("\033c", end="")  # ANSI escape code to clear screen
        display_chapters([ch["name"] for ch in chapter_info])

        # Display selection help
        print("\nSELECTION OPTIONS:")
        print(" * all       - Select all chapters")
        print(" * newestN   - Select newest N chapters (e.g. 'newest5')")
        print(" * x-y       - Select range (e.g. '10-20')")
        print(" * x,y,z     - Select specific chapters (e.g. '1,3,5')")
        print(" * .x        - Select decimal chapters (e.g. '.5')")
        print(" * search:term - Search by name (e.g. 'search:prologue')")
        
        # Get user input
        selection = input("\nEnter selection: ").strip().lower()
        if not selection:
            print("\n[ERROR] Please enter a selection")
            input("Press Enter to continue...")
            continue

        try:
            # Process selection
            print("\nProcessing your selection...")
            
            if selection == "all":
                selected = [ch["element"] for ch in chapter_info]
                print(f"Selected all {len(selected)} chapters")
            elif selection.startswith("newest"):
                n = int(selection[6:])
                selected = [
                    ch["element"]
                    for ch in sorted(
                        chapter_info, key=lambda x: x["number"], reverse=True
                    )[:n]
                ]
                print(f"Selected newest {n} chapters")
            elif "-" in selection:
                start, end = map(float, selection.split("-"))
                selected = [
                    ch["element"] for ch in chapter_info if start <= ch["number"] <= end
                ]
                print(f"Selected chapters from {start} to {end}")
            elif "," in selection:
                selected_numbers = set(map(float, selection.split(",")))
                selected = [
                    ch["element"]
                    for ch in chapter_info
                    if ch["number"] in selected_numbers
                ]
                print(f"Selected specific chapters: {selection}")
            elif selection.startswith("."):
                decimal = float(selection)
                selected = [
                    ch["element"] for ch in chapter_info if ch["number"] % 1 == decimal
                ]
                print(f"Selected decimal chapters: {selection}")
            elif selection.startswith("search:"):
                query = selection[7:].lower()
                selected = [
                    ch["element"] for ch in chapter_info if query in ch["name"].lower()
                ]
                print(f"Found {len(selected)} chapters matching '{query}'")
            else:
                num = float(selection)
                selected = [ch["element"] for ch in chapter_info if ch["number"] == num]
                print(f"Selected chapter {num}")

            # Show selection preview
            if not selected:
                print("\n[WARNING] No chapters matched your selection.")
                input("\nPress Enter to continue...")
                continue

            print("\nSELECTION PREVIEW:")
            display_chapters(
                [chapter_extractor(ch) for ch in selected],
                title="SELECTED CHAPTERS"
            )

            # Confirmation
            confirm = input("\nConfirm selection? [Y/n]: ").strip().lower()
            if not confirm or confirm == "y":
                return selected

        except Exception as e:
            print(f"\n[ERROR] {e}\nPlease try again.")
            input("\nPress Enter to continue...")