import re

class ChapterSorter:
    @staticmethod
    def sort_and_deduplicate(chapter_list):
        seen = set()
        unique_chapters = []
        for chap in chapter_list:
            if chap not in seen:
                seen.add(chap)
                unique_chapters.append(chap)

        def chapter_sort_key(chap):
            match = re.match(r'(\d+)(?:-(\d+))?', chap)
            if match:
                main = int(match.group(1))
                sub = int(match.group(2) or 0)
                return (main, sub)
            return (float('inf'), 0)

        return sorted(unique_chapters, key=chapter_sort_key)
