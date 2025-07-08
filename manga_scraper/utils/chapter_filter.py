# manga_scraper/utils/chapter_filter.py
import re
from typing import List, Any, Dict
from natsort import natsorted
from .display_utils import display_boxed_title, display_multi_column_items
from .chapter_utils import extract_chapter_number

def select_chapters_interactively(
    raw_chapters: List[Any], 
    chapter_extractor: callable
) -> List[Any]:
    """
    Interactive chapter selection supporting type-based grouping and
    multiple selections with syntax like:

      all
      c x-y / v x-y / e x-y   - Select range by type and index (e.g. 'c 1-5')
      c x,y / v x,y / e x,y   - Select specific indexes by type (e.g. 'c 1,3,5')
      c all / v all / e all   - Select all chapters of a specific type
      s:term                  - Filter chapters by name
      q                      - Quit

    Types:
      c - Chapters
      v - Volumes
      e - Extras

    Multiple selections can be combined like: 'v 1-3, e all, c 2,5'
    """

    # Step 1: Extract and classify chapter info
    chapter_info = []
    for ch in raw_chapters:
        try:
            text = chapter_extractor(ch)
            num = extract_chapter_number(text)
            chapter_info.append({
                "element": ch,
                "name": text,
                "number": num,
                "type": ch.get("type", 1)  # default to 1 (Chapter)
            })
        except Exception:
            continue

    if not chapter_info:
        print("[×] No chapters available.")
        return []

    # Sort by type, then number, then name
    chapter_info = natsorted(
        chapter_info, key=lambda x: (x["type"], x["number"], x["name"].lower())
    )

    pad_width = len(str(len(chapter_info)))

    # Group by type for easier access
    type_groups: Dict[int, List[Dict]] = {
        1: [c for c in chapter_info if c["type"] == 1],
        2: [c for c in chapter_info if c["type"] == 2],
        3: [c for c in chapter_info if c["type"] == 3],
    }

    def format_numbered_list(items, pad, extractor=lambda x: x["name"]):
        return [f"{i+1:0{pad}d}. {extractor(item)}" for i, item in enumerate(items)]

    def display_groups():
        print("\033c", end="")
        width = display_boxed_title("CHAPTER SELECTION")
        for type_id, label in [(1, "CHAPTERS"), (2, "VOLUMES"), (3, "EXTRAS")]:
            group = type_groups[type_id]
            if not group:
                continue
            print()
            content_len = len(label) + 2
            left_len = (width - content_len) // 2
            right_len = width - content_len - left_len
            print("─" * left_len + f" {label} " + "─" * right_len)
            print()
            display_multi_column_items(format_numbered_list(group, pad_width), width)
        print("\n" + "─" * width)
        print(" " * 4 + "SELECTION OPTIONS:")
        print(" " * 4 + "all              - Select all chapters (all types)")
        print(" " * 4 + "c x-y / v x-y / e x-y   - Range by type (e.g. 'c 1-5')")
        print(" " * 4 + "c x,y / v x,y / e x,y   - Index list by type (e.g. 'e 1,3,6')")
        print(" " * 4 + "c all / v all / e all   - Select all of a specific type")
        print(" " * 4 + "s:term           - Filter chapters by name")
        print(" " * 4 + "q                - Quit selection")
        print("─" * width)
        return width

    def parse_index_segment(segment: str) -> List[int]:
        result = set()
        parts = [p.strip() for p in segment.split(",")]
        for part in parts:
            if "-" in part:
                try:
                    start, end = map(int, part.split("-"))
                    result.update(range(start, end + 1))
                except:
                    pass
            else:
                try:
                    result.add(int(part))
                except:
                    pass
        return sorted(result)

    while True:
        term_width = display_groups()
        selection = input(" " * 4 + "⌨  Enter selection: ").strip().lower()
        if not selection:
            print("\n" + " " * 4 + "[!] Please enter a selection")
            input(" " * 4 + "Press Enter to continue...")
            continue
        if selection == "q":
            return []

        selected: List[Dict] = []

        try:
            if selection == "all":
                selected = chapter_info[:]
            elif selection.startswith(("s:", "search:")):
                query = re.sub(r"^(s:|search:)", "", selection).lower()
                filtered = [c for c in chapter_info if query in c["name"].lower()]
                if not filtered:
                    print(" " * 4 + "[!] No chapters matched.")
                    input(" " * 4 + "Press Enter to continue...")
                    continue

                width = display_boxed_title("FILTERED RESULTS")
                display_multi_column_items(format_numbered_list(filtered, len(str(len(filtered))), lambda x: x["name"]), width)

                inner_sel = input(" " * 4 + "Select from filtered (e.g. '1-3'): ").strip()
                indices = parse_index_segment(inner_sel)
                selected = [filtered[i-1] for i in indices if 1 <= i <= len(filtered)]
            else:
                parts = [p.strip() for p in re.split(r",(?=\s*[cve]\s)", selection) if p.strip()]
                if not parts:
                    parts = [selection]

                for part in parts:
                    m = re.match(r"^(c|v|e)\s+(.+)$", part)
                    if not m:
                        continue
                    prefix, rest = m.group(1), m.group(2).strip()
                    type_map = {"c": 1, "v": 2, "e": 3}
                    group = type_groups[type_map[prefix]]

                    if rest == "all":
                        selected.extend(group)
                    else:
                        indices = parse_index_segment(rest)
                        for i in indices:
                            if 1 <= i <= len(group):
                                selected.append(group[i-1])

            if not selected:
                print(" " * 4 + "[!] No chapters matched the selection.")
                input(" " * 4 + "Press Enter to continue...")
                continue

            # === Final Preview with Grouping ===
            final_groups = {
                1: [ch for ch in selected if ch["type"] == 1],
                2: [ch for ch in selected if ch["type"] == 2],
                3: [ch for ch in selected if ch["type"] == 3],
            }

            width = display_boxed_title("SELECTED CHAPTERS")
            final_all = []
            for type_id, label in [(2, "VOLUMES"), (3, "EXTRAS"), (1, "CHAPTERS")]:
                group = final_groups[type_id]
                if not group:
                    continue
                print()
                content_len = len(label) + 2
                left = (width - content_len) // 2
                right = width - content_len - left
                print("─" * left + f" {label} " + "─" * right)
                print()
                numbered = format_numbered_list(group, pad_width)
                final_all.extend(group)
                display_multi_column_items(numbered, width)

            print("\n" + "─" * width)
            confirm = input(" " * 4 + "Confirm selection? [Y/n/q] ").strip().lower()
            if confirm in ("y", ""):
                return [ch["element"] for ch in final_all]
            elif confirm == "q":
                return []

        except Exception as e:
            print(" " * 4 + f"[!] Error: {e}")
            input(" " * 4 + "Press Enter to continue...")