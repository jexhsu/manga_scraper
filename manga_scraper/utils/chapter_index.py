class ChapterIndexResolver:
    @staticmethod
    def resolve_index(chapter_list, start_chapter):
        # Handle map (dictionary)
        if isinstance(chapter_list, dict):
            chapter_list = list(chapter_list.keys())

        # Handle array (list)
        if start_chapter >= len(chapter_list) or start_chapter < 0:
            print(f"⚠️ start_chapter {start_chapter} out of range, reset to 0")
            return 0

        try:
            return chapter_list.index(str(start_chapter))
        except ValueError:
            print(f"⚠️ start_chapter {start_chapter} not found, resetting to index 0")
            return 0
