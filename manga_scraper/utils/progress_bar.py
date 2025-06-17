import asyncio
import sys
import shutil
from typing import Optional
from scrapy.http import Response

class ProgressBar:
    """
    Optimized progress bar that dynamically adjusts width while minimizing padding.
    """
    
    def __init__(self, min_width: int = 30, max_width: int = 80):
        """
        Initialize with more conservative width defaults.
        
        Args:
            min_width: Reasonable minimum width (default: 30)
            max_width: Optimal maximum width (default: 80)
        """
        self.min_width = min_width
        self.max_width = max_width
        self.last_progress = ""
        self.last_progress_length = 0
        self._update_terminal_width()

    def _update_terminal_width(self) -> None:
        """Calculate available width more precisely."""
        try:
            terminal_width = shutil.get_terminal_size().columns
            # Reserve space for: 
            # "⏳ Chapter X: [] (XX/XX) " ≈ 25 chars (for chapter numbers up to 999)
            self.available_width = min(
                max(terminal_width - 25, self.min_width),
                self.max_width
            )
        except:
            self.available_width = self.min_width

    def progress_bar(self, current: int, total: int) -> str:
        """
        Generate optimized progress bar with dynamic width.
        """
        self._update_terminal_width()
        
        if total <= 0:
            return "[" + " " * self.available_width + "]"

        progress_ratio = min(current / total, 1.0)
        filled = int(progress_ratio * self.available_width)
        
        # More compact visual style
        bar = (
            "\033[92m" + "━" * filled +  # Solid block for completed
            "\033[90m" + "─" * (self.available_width - filled) +  # Lighter for remaining
            "\033[0m"
        )
        
        return f"[{bar}]"

    def format_progress(self, chapter: str, current: int, total: int) -> str:
        """
        Optimized progress line formatter.
        """
        # Estimate maximum digits needed for numbering
        max_digits = len(str(total))
        progress_text = (
            f"⏳ Chapter {chapter}: "
            f"{self.progress_bar(current, total)} "
            f"({current:{max_digits}d}/{total}) "
        )
        return progress_text

    def update_progress(self, text: str) -> None:
        """More efficient progress update."""
        if text != self.last_progress:
            # Clear only what we need to
            sys.stdout.write("\r" + text + " " * max(0, self.last_progress_length - len(text)))
            sys.stdout.flush()
            self.last_progress = text
            self.last_progress_length = len(text)

    def clear_progress(self) -> None:
        """Optimized clear."""
        if self.last_progress_length > 0:
            sys.stdout.write("\r" + " " * self.last_progress_length + "\r")
            sys.stdout.flush()
            self.last_progress = ""
            self.last_progress_length = 0