# src/app.py

import pickle
import ccxt.async_support as ccxt

from datetime import datetime
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Header, Footer, Static, Button, Digits

from clients.manager import PriceManager

from workers.markets import fetch_ohlcv, fetch_market, fetch_markets, ApiDataFetched

from screens.home import HomeScreen
from screens.settings import SettingsScreen
from screens.token import TokenScreen

class RealTimeTUIApp(App):
    CSS = """
    Header {
        dock: top;
        text-style: bold;
        height: 1;
        content-align: center middle;
        background: $panel;
        color: $text;
        padding-bottom: 1;
    }
    Footer {
        dock: bottom;
        height: 1;
        content-align: center middle;
        background: $panel;
        color: $text;
    }
    .primary{
        text-style: bold;
        content-align: center middle;
    }
    .secondary {
        text-style: dim;
        content-align: center middle;
    }
    .horizontal {
        layout: horizontal;
        height: auto;
        padding: 1;
    }
    .vertical {
        layout: vertical;
        height: auto;
        padding: 1;
    }
    """
    
    price_manager: PriceManager | None = None
    
    strategy_data = reactive(b"")  # Global reactive state for market data
    
    exchange_client: ccxt.Exchange | None = None
    symbols: list[str] = []

    SCREENS = {
        "home": HomeScreen,
        "settings": SettingsScreen,
        "token": TokenScreen,
    }
    
    BINDINGS = [
        ("q", "quit", "quit"),
        ("s", "push_screen('settings')", "settings"), # Direct key navigation
        ("t", "push_screen('token')", "token info"), # Direct key navigation
    ]
    
    def on_mount(self):
        # Initialize exchange client
        try:
            self.exchange_client = ccxt.binanceus({
                'enableRateLimit': True,
            })
            self.symbols = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'DOGE/USD']

            self.log("Exchange client initialized.")
        except Exception as e:
            self.log(f"Error initializing exchange client: {e}")
            self.bell();
            return
        
        # Start on the home screen
        self.push_screen("home")
        self.set_interval(5.0, self.start_data_fetch)
                
    def start_data_fetch(self):
        """A placeholder method to start data fetching tasks."""
        self.run_worker(fetch_ohlcv(self), exclusive=True)

    def on_api_data_fetched(self, message: ApiDataFetched):
            """Called when ApiDataFetched message is received from the worker."""
            
            self.strategy_data = message.data 

            message.stop()

if __name__ == "__main__":
    app = RealTimeTUIApp()
    app.run()