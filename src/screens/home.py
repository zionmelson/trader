# src/screens/home.py

import pickle
import time
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Header, Footer, Static

class TickerWidget(Static):
    def on_mount(self) -> None:
        """
        Sets the widget's initial content by reading the current state 
        of the App's reactive variable.
        """  
        
        self.watch(self.app, "strategy_data", self.watch_strategy_data)
        
        if not self.app.strategy_data:
            self.update("[i]Application starting up...[/i]")
            return
        
    def watch_strategy_data(self, data: bytes) -> None:
        """
        Called when the TUI's primary strategy_data state changes.
        """
        if not data:
            self.update("[i]No data received[/i]")
            return
        
        try:
            unpickled_data = pickle.loads(data)
            
            if isinstance(unpickled_data, str):
                self.log(f"Received error from worker: {unpickled_data}")
                self.update(f"[red]API Error: {unpickled_data}[/red]")
                return
            
            self.log(f"TickerWidget: received update with data keys: {list(unpickled_data.keys())}")
            
            if data == {}:
                self.update("[i]Waiting for market data...[/i]")
                return
        
        except Exception as e:
            self.log(f"Error unpickling data: {e}")
            self.update("[red]Error: Corrupt data[/red]")
            return
                    
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
   
class LivePricesTable(Static):
    """
    This widget pulls *all* live ticker data from the PriceManager
    and displays it in a formatted table.
    """
    def on_mount(self) -> None:
        self.update("[i]Live Prices (5s): Loading...[/i]")
        # Set this widget's custom latency (faster)
        self.set_interval(2.5, self.refresh_prices) 

    def refresh_prices(self) -> None:
        dex_manager = self.app.dex_manager
        
        if not dex_manager:
            self.update("[red]Error: PriceManager not initialized![/red]")
            return

        # Pull the entire price dictionary
        all_prices = dex_manager.get_all_prices()
        
        if not all_prices:
            self.update("[i]Live Prices (5s): No data received yet...[/i]")
            return

        # Build the rich display string
        lines = ["[bold underline]Live Ticker Prices[/bold underline]\n"]
        
        for exchange_id, symbols_prices in all_prices.items():
            lines.append(f"[bold]{exchange_id.upper()}[/bold]")
            if not symbols_prices:
                lines.append("  [dim]Waiting for data...[/dim]")
                continue

            for symbol, price in symbols_prices.items():
                price_str = f"[green]${price:,.2f}[/green]" if price is not None else "[red]N/A[/red]"
                lines.append(f"  {symbol}: {price_str}")
            lines.append("") # Add a blank line between exchanges
            
        self.update("\n".join(lines))
 
           
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
            # Widget for your strategy data
            TickerWidget(classes="ticker_widget"), 
            
            Static("\n"), # Add some space
            
            # Widget for all live ticker prices
            LivePricesTable(classes="live_prices_table"), 
            
            classes="vertical"
        )
    
