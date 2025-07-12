# manga_scraper/utils/chapter_filter.py
import re
from typing import List, Any, Dict, Optional
from natsort import natsorted
from .display_utils import display_boxed_title, display_multi_column_items
from .chapter_utils import extract_chapter_number

"""
Expected JSON Structure:
{
    "build": {
        "type": [
            {
                "id": int,       # 1 for chapters, 2 for volumes, 3 for extras
                "name": str      # Display name (e.g. "单话", "单行本", "番外篇")
            }
        ]
    },
    "groups": {
        "<group_id>": {          # e.g. "chapters", "volumes", "extras"
            "count": int,        # Total count
            "name": str,         # Display name (e.g. "单话", "单行本", "番外篇")
            "chapters": [
                {
                    "type": int, # Matches type id from build.type
                    "name": str, # Display name (e.g. "第01话")
                    "id": str    # Unique identifier
                }
            ]
        }
    }
}
"""


def select_chapters_interactively(
    raw_json: Dict[str, Any],
    chapter_extractor: callable = lambda x: x["name"],
    debug_choice: Optional[str] = None,
) -> List[Any]:
    """
    Interactive chapter selection with proper group ordering and selection.

    Args:
        raw_json: The manga JSON data with groups and chapters
        chapter_extractor: Function to extract chapter display text
        debug_choice: Optional pre-set selection for testing

    Returns:
        List of selected chapter objects
    """

    # Map type id to type name, e.g. {1: "話", 2: "卷", 3: "番外篇"}
    type_mapping = {t["id"]: t["name"] for t in raw_json["build"]["type"]}
    short_to_type = {"c": 1, "v": 2, "e": 3}  # Shortcuts for types

    # Prepare group info and shortcuts for easy lookup
    group_info = {}
    group_short = {}
    all_chapters = []

    # Sort groups by their numeric suffix in short key, e.g. g1, g2, ...
    sorted_groups = sorted(
        raw_json["groups"].items(),
        key=lambda x: (
            int(x[1].get("short", "g0")[1:])
            if x[1].get("short", "").startswith("g")
            else 0
        ),
    )

    for i, (group_id, group_data) in enumerate(sorted_groups, 1):
        short = f"g{i}"
        group_info[group_id] = {
            "name": group_data["name"],
            "count": group_data["count"],
            "short": short,
            "index": i,
        }
        group_short[short] = group_id
        group_short[group_id] = group_id

        for ch in group_data["chapters"]:
            ch_copy = ch.copy()
            ch_copy["group"] = group_id
            all_chapters.append(ch_copy)

    if not all_chapters:
        print("[×] No chapters available.")
        return []

    # Sort all chapters globally by group index, type, and chapter number
    all_chapters = natsorted(
        all_chapters,
        key=lambda x: (
            group_info[x["group"]]["index"],
            x["type"],
            extract_chapter_number(chapter_extractor(x)),
            chapter_extractor(x).lower(),
        ),
    )

    # Organize chapters by group and type for display and selection
    group_data = {}
    for ch in all_chapters:
        gid = ch["group"]
        if gid not in group_data:
            group_data[gid] = {
                "display_name": group_info[gid]["name"],
                "short": group_info[gid]["short"],
                "index": group_info[gid]["index"],
                "count": group_info[gid]["count"],
                "types": {t: [] for t in type_mapping},
            }
        group_data[gid]["types"][ch["type"]].append(ch)

    def format_numbered_list(items, pad, extractor=chapter_extractor):
        """Format list items with zero-padded numbering"""
        return [f"{i+1:0{pad}d}. {extractor(item)}" for i, item in enumerate(items)]

    def display_chapter_groups():
        """Display all chapter groups with types in multi-column format"""
        print("\033c", end="")  # Clear screen
        width = display_boxed_title("CHAPTER SELECTION")
        # Display groups in order by index
        for gid in sorted(group_data.keys(), key=lambda x: group_info[x]["index"]):
            data = group_data[gid]
            group_title = (
                f"[{data['short']}] {data['display_name']} (Total: {data['count']})"
            )
            pad = width - len(group_title) - 4
            print("\n" + "=" * (pad // 2) + f" {group_title} " + "=" * (pad - pad // 2))

            for type_id in sorted(type_mapping.keys()):
                chapters = data["types"][type_id]
                if not chapters:
                    continue
                short_key = list(short_to_type.keys())[
                    list(short_to_type.values()).index(type_id)
                ]
                header = (
                    f"  {short_key}: {type_mapping[type_id]} (Count: {len(chapters)})"
                )
                print("\n" + header)
                print("  " + "-" * (len(header) - 2))
                pad_width = len(str(len(chapters)))
                display_multi_column_items(
                    format_numbered_list(chapters, pad_width), width
                )

        # Display help
        print("\n" + "=" * width)
        print(" " * 4 + "SELECTION EXAMPLES:")
        print(
            " " * 4 + "g1(c(1-3), v(all))      - Group 1: Chapters 1-3 and all volumes"
        )
        print(" " * 4 + "g2(v(1,3), e(2-5))      - Group 2: Volumes 1,3 and extras 2-5")
        print(
            " " * 4
            + "g1(c(1)),g2(v(1)),g3(c(1)) - Multiple group selections separated by commas or spaces"
        )
        print(" " * 4 + "all                      - Select all chapters")
        print(" " * 4 + "q                        - Quit selection")
        print("=" * width)
        return width

    def parse_index_segment(segment: str) -> List[int]:
        """
        Parse index segments like '1-3,5,7-9' into a sorted list of integers.
        """
        result = set()
        for part in segment.split(","):
            part = part.strip()
            if "-" in part:
                try:
                    start, end = map(int, part.split("-"))
                    result.update(range(start, end + 1))
                except Exception:
                    continue
            elif part.isdigit():
                result.add(int(part))
        return sorted(result)

    def parse_group_selection(group_sel: str) -> List[Dict]:
        """
        Parse individual group selection string like 'g2(v(all), e(2-5))'
        """
        selected = []
        # Use non-greedy matching for inner parentheses content
        match = re.match(r"^(g\d+|\w+)\s*\((.*?)\)$", group_sel)
        if not match:
            return []

        group_key = match.group(1)
        type_selections = match.group(2)

        group_id = group_short.get(group_key)
        if not group_id:
            # fallback: find by short name
            for gid, g in group_info.items():
                if g["short"] == group_key:
                    group_id = gid
                    break
        if not group_id or group_id not in group_data:
            return []

        # Parse each type selection like c(...), v(...), e(...)
        for type_sel in re.finditer(r"(c|v|e)\s*\(([^)]*)\)", type_selections):
            type_char = type_sel.group(1)
            selections = type_sel.group(2).strip()
            type_id = short_to_type.get(type_char)
            if type_id not in group_data[group_id]["types"]:
                continue

            if selections == "all":
                selected.extend(group_data[group_id]["types"][type_id])
            else:
                indices = parse_index_segment(selections)
                for i in indices:
                    if 1 <= i <= len(group_data[group_id]["types"][type_id]):
                        selected.append(group_data[group_id]["types"][type_id][i - 1])
        return selected

    def split_group_selections(selection: str) -> List[str]:
        """
        Split input string into full group selections by matching parentheses
        and commas.

        Example:
            "g1(c(1-3),v(all)), g2(v(1,3),e(2-5))"
        ->
            ["g1(c(1-3),v(all))", "g2(v(1,3),e(2-5))"]

        Also supports space separated:
            "g1(c(1)) g2(v(2))"
        """
        results = []
        buf = ""
        depth = 0
        for ch in selection:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1

            if ch == "," and depth == 0:
                if buf.strip():
                    results.append(buf.strip())
                    buf = ""
            else:
                buf += ch

        if buf.strip():
            results.append(buf.strip())
        return results

    # ===== DEBUG SHORTCUT =====
    if debug_choice is not None:
        print(f"[DEBUG] Auto chapter selection: {debug_choice!r}")
        all_chapters = []

        selected = []
        group_selections = split_group_selections(debug_choice)
        for group_sel in group_selections:
            selected.extend(parse_group_selection(group_sel))

        if not selected:
            print("[DEBUG] No matching chapters found for debug_choice")
        else:
            print(f"[DEBUG] {len(selected)} chapters auto-selected.")
        return selected

    # === Main interaction loop ===
    while True:
        width = display_chapter_groups()
        selection = input(" " * 4 + "⌨ Selection: ").strip().lower()

        if not selection:
            print(" " * 4 + "[!] Please enter a valid selection")
            input(" " * 4 + "Press Enter to continue...")
            continue

        if selection == "q":
            return []
        elif selection == "all":
            selected = all_chapters[:]
        else:
            selected = []
            group_selections = split_group_selections(selection)
            for group_sel in group_selections:
                selected.extend(parse_group_selection(group_sel))

        if not selected:
            print(" " * 4 + "[!] No matching chapters found")
            input(" " * 4 + "Press Enter to continue...")
            continue

        width = display_boxed_title("SELECTED CHAPTERS")
        final_groups = {}

        for ch in selected:
            gid = ch["group"]
            if gid not in final_groups:
                final_groups[gid] = {
                    "display_name": group_data[gid]["display_name"],
                    "short": group_data[gid]["short"],
                    "index": group_data[gid]["index"],
                    "types": {t: [] for t in type_mapping},
                }
            final_groups[gid]["types"][ch["type"]].append(ch)

        for gid in sorted(final_groups.keys(), key=lambda x: group_info[x]["index"]):
            data = final_groups[gid]
            group_title = f"[{data['short']}] {data['display_name']} (Selected: {sum(len(t) for t in data['types'].values())})"
            pad = width - len(group_title) - 4
            print("\n" + "=" * (pad // 2) + f" {group_title} " + "=" * (pad - pad // 2))
            for type_id in sorted(type_mapping.keys()):
                chapters = data["types"][type_id]
                if not chapters:
                    continue
                short_key = list(short_to_type.keys())[
                    list(short_to_type.values()).index(type_id)
                ]
                header = (
                    f"  {short_key}: {type_mapping[type_id]} (Count: {len(chapters)})"
                )
                print("\n" + header)
                print("  " + "-" * (len(header) - 2))
                pad_width = len(str(len(chapters)))
                display_multi_column_items(
                    format_numbered_list(chapters, pad_width), width
                )

        print("\n" + "=" * width)
        confirm = input(" " * 4 + "Confirm selection? [Y/n/q] ").strip().lower()
        if confirm in ("y", ""):
            return selected
        elif confirm == "q":
            return []
