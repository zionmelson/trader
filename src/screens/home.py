# src/screens/home.py

import pickle
import time
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Button

class TickerWidget(Static):
    current_data: dict = {}
    def on_mount(self) -> None:
        """
        Sets the widget's initial content by reading the current state 
        of the App's reactive variable.
        """  
        
        self.watch(self.app, "market_data", self.watch_market_data)
        
        if not self.app.market_data:
            self.update("[i]Application starting up...[/i]")
            return

        
    def watch_market_data(self, data: bytes) -> None:
        """
        Called when the TUI's primary market_data state changes.
        """
        self.log('unpicing data')
        
        try:
            unpickled_data = pickle.loads(data)
            
            if isinstance(unpickled_data, str):
                self.log(f"Received error from worker: {unpickled_data}")
                self.update(f"[red]API Error: {unpickled_data}[/red]")
                return
            
            current_data = unpickled_data
            self.log(f"TickerWidget: received update with data keys: {list(current_data.keys())}")
            
            self.log('unpicing data')
            
            if data == {}:
                self.update("[i]Waiting for market data...[/i]")
                return
        
        except Exception as e:
            self.log(f"Error unpickling data: {e}")
            self.update("[red]Error: Corrupt data[/red]")
            return
            
        # 3. Handle if the unpickled data is an error string
        
        df_5m = unpickled_data.get("5m")
        df_1h = unpickled_data.get("1h")
        df_1d = unpickled_data.get("1d")

        if df_5m is None or df_1h is None or df_1d is None:
            self.update("[i]Incomplete market data received...[/i]")
            return

        try:
            last_row = df_5m.iloc[-1]
            
            self.log(f"TickerWidget: last_row data: {last_row.to_dict()}")
            
            symbol = self.app.symbols[0] 
            price = last_row.get("close", "N/A") # Get the 'close' price from the last row

            # Format the display string
            if price != "N/A" and isinstance(price, (int, float)):
                 price_str = f"[bold green]${price:.2f}[/bold green]"
            else:
                price_str = f"[bold red]{price}[/bold red]"

            self.update(
                f"[bold white]{symbol}[/bold white]: {price_str}"
            )
        except Exception as e:
            self.log(f"Error processing DataFrame: {e}")
            self.update(f"[red]Error parsing data[/red]:", e)
        
class HomeScreen(Screen):
    """The main application view/page."""
    
    # Textual calls this method to define the structure of the screen
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Container(
            Static("💹", classes="primary"),
            classes="horizontal"
        )
        yield Container(
            TickerWidget(classes="secondary"),
            classes="vertical"
        )
    

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "to_settings":
            # 1. The key navigation command: push the next screen
            self.app.push_screen("settings")