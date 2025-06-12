import re

class ChapterPaginator:
    def __init__(self, start_url, selector, pattern):
        self.start_url = start_url
        self.selector = selector
        self.pattern = pattern
        self.page = 1
        self.all_chapters = []
        self.has_more_pages = True

    def extract_chapters(self, response):
        chapters = response.css(self.selector).re(self.pattern)
        new_chapters = [c for c in chapters if c not in self.all_chapters]
        self.all_chapters.extend(new_chapters)
        if not new_chapters:
            self.has_more_pages = False
        return new_chapters

    def next_page_url(self):
        self.page += 1
        return f"{self.start_url}?page={self.page}"

    def reset(self):
        self.page = 1
        self.all_chapters.clear()
        self.has_more_pages = True
