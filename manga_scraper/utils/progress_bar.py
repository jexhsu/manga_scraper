# manga_scraper/utils/progress_bar.py
import sys
import shutil


class ProgressBar:
    """
    Terminal-friendly progress bar with auto width adjustment and color support.
    """

    def __init__(
        self, min_width: int = 30, max_width: int = 80, use_color: bool = True
    ):
        self.min_width = min_width
        self.max_width = max_width
        self.use_color = use_color
        self.last_progress = ""
        self.last_progress_length = 0
        self._update_terminal_width()

    def _color(self, text: str, color_code: str) -> str:
        return f"{color_code}{text}\033[0m" if self.use_color else text

    def _update_terminal_width(self) -> None:
        try:
            terminal_width = shutil.get_terminal_size().columns
            self.available_width = min(
                max(terminal_width - 25, self.min_width), self.max_width
            )
        except Exception:
            self.available_width = self.min_width

    def progress_bar(self, current: int, total: int) -> str:
        self._update_terminal_width()

        if total <= 0:
            return "[" + " " * self.available_width + "]"

        progress_ratio = min(current / total, 1.0)
        filled = int(progress_ratio * self.available_width)

        bar = self._color("━" * filled, "\033[92m") + self._color(  # green filled
            "─" * (self.available_width - filled), "\033[90m"
        )  # grey empty
        return f"[{bar}]"

    def format_progress(self, chapter: str, current: int, total: int) -> str:
        max_digits = len(str(total))
        bar = self.progress_bar(current, total)
        return f"⏳ Chapter {chapter}: {bar} ({current:{max_digits}d}/{total})"

    def update_progress(self, text: str) -> None:
        if text != self.last_progress:
            sys.stdout.write(
                "\r" + text + " " * max(0, self.last_progress_length - len(text))
            )
            sys.stdout.flush()
            self.last_progress = text
            self.last_progress_length = len(text)

    def clear_progress(self) -> None:
        if self.last_progress_length > 0:
            sys.stdout.write("\r" + " " * self.last_progress_length + "\r")
            sys.stdout.flush()
            self.last_progress = ""
            self.last_progress_length = 0

    def __call__(self, chapter: str, current: int, total: int) -> None:
        """
        Enables direct call usage: progress(chapter, current, total)
        """
        self.update_progress(self.format_progress(chapter, current, total))
