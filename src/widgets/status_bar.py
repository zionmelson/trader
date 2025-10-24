# src/widgets/status_bar.py

from textual.widget import Widget
from textual.reactive import reactive
from rich.text import Text

class StatusBar(Widget):
    """A simple textual status bar widget.

    - Left side shows a short status (e.g. "Ready", "Connected").
    - Right side shows a message (e.g. "Saving...", "Error: ...").
    """

    status: str = reactive("Ready")
    message: str = reactive("")

    def render(self) -> Text:
        """Render a single-line status bar. Left-aligned status, right-aligned message."""
        width = self.size.width or 80

        left = f" {self.status} "
        right = f" {self.message} "

        # Ensure we never exceed available width; truncate message if needed.
        available_for_right = max(width - len(left), 0)
        if len(right) > available_for_right:
            if available_for_right <= 1:
                right = ""
            else:
                # leave room for an ellipsis
                right = right[: available_for_right - 1] + "…"

        # Fill the space between left and right
        middle_space = max(width - len(left) - len(right), 0)
        text = left + (" " * middle_space) + right

        t = Text(text)
        # Give the whole bar a subtle background by using reverse style,
        # and make the left status bold to stand out.
        t.stylize("reverse")
        t.stylize("bold", 0, len(left))
        return t

    # Convenience mutators to update the bar from application code
    def set_status(self, status: str) -> None:
        self.status = status

    def set_message(self, message: str) -> None:
        self.message = message

    def clear_message(self) -> None:
        self.message = ""