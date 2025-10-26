# src/screens/error.py

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Static, Button

class ErrorScreen(Screen):
    """The application settings view/page."""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Container(
            Static("💊", classes="primary"),
            classes="horizontal"
        )
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "to_home":
            # 2. The key navigation command: pop the current screen
            self.app.push_screen("home")