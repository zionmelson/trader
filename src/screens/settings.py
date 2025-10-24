# src/screens/settings.py

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Button

class SettingsScreen(Screen):
    """The application settings view/page."""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Static("Configuration and Settings ⚙️", classes="title")
        yield Button("home", id="to_home")
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "to_home":
            # 2. The key navigation command: pop the current screen
            self.app.push_screen("home")