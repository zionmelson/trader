# src/screens/home.py

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Button

class TickerWidget(Static):
   def watch_market_data(self, data: dict) -> None:
        """
        Called when the TUI's primary market_data state changes.
        """
        self.log(f"TickerWidget: received update with data keys: {list(data.keys())}")
        
        # 1. Handle the initial empty state (or if the API call fails)
        if not data:
            self.update("[i]Waiting for market data...[/i]")
            return

        # 2. Safely extract and format the data
        # Ensure your keys match the format returned by CCXT (e.g., 'symbol' and 'last' for fetch_ticker)
        symbol = data.get("symbol", "N/A")
        price = data.get("price", data.get("last", "N/A")) # Check for 'price' or 'last'
        
        # Format the display string
        if price != "N/A" and isinstance(price, (int, float)):
             price_str = f"[bold green]${price:.2f}[/bold green]"
        else:
            price_str = f"[bold red]{price}[/bold red]"
            
        self.update(
            f"[bold blue]{symbol}[/bold blue]: {price_str}"
        )
        
        def on_mount(self) -> None:
            """
            Sets the widget's initial content by reading the current state 
            of the App's reactive variable.
            """
            # Get the current value of the app's market_data property
            current_data = self.app.market_data 
            
            # Manually trigger the update logic with the current data
            # This will set it to "[i]Waiting for market data...[/i]" initially
            self.watch_market_data(current_data)
            
            # Important: set a default content, in case watch_market_data fails
            if not self.app.market_data:
                self.update("[i]Application starting up...[/i]")

class HomeScreen(Screen):
    """The main application view/page."""
    
    # Textual calls this method to define the structure of the screen
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Container(
            Static("Welcome to the Home Screen! 👋", classes="primary"),
            classes="horizontal",
        )
        yield Container(
            Static("Real-Time Data:", classes="secondary"),
            TickerWidget(classes="ticker_widget"),
            classes="vertical",
        )
        yield Static("logged in as: user123", classes="secondary")
    

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "to_settings":
            # 1. The key navigation command: push the next screen
            self.app.push_screen("settings")