# src/screens/token.py

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Button

# Page to Render Token Information
class TokenScreen(Screen):
    """The application token view/page."""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Static("token info", classes="title")
        yield Button("home", id="to_home")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "to_home":
            # 2. The key navigation command: pop the current screen
            self.app.push_screen("home")