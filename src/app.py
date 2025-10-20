from datetime import datetime
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Button, Digits


class ClockApp(App):
    CSS = """
    Screen { align: center middle; }
    Static { text-align: center; }
    Digits { text-align: center; }
    """

    def compose(self) -> ComposeResult:
        # yield Header()
        yield Static("Welcome to the Home Screen! 👋", classes="title")
        yield Digits("")
        # yield Footer()

    def on_ready(self) -> None:
        self.update_clock()
        self.set_interval(1, self.update_clock)

    def update_clock(self) -> None:
        clock = datetime.now().time()
        self.query_one(Digits).update(f"{clock:%T}")

if __name__ == "__main__":
    app = ClockApp()
    app.run()