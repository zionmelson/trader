import ccxt.async_support as ccxt

from datetime import datetime
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Header, Footer, Static, Button, Digits

from workers.markets import fetch_market, fetch_markets, ApiDataFetched

from screens.home import HomeScreen
from screens.settings import SettingsScreen

class RealTimeTUIApp(App):
    market_data = reactive({})  # Global reactive state for market data
    
    exchange_client: ccxt.Exchange | None = None
    symbols: list[str] = []

    SCREENS = {
        "home": HomeScreen,
        "settings": SettingsScreen,
    }
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("s", "push_screen('settings')", "Settings"), # Direct key navigation
    ]
    
    def on_mount(self):
        # Initialize exchange client
        try:
            self.exchange_client = ccxt.hyperliquid({
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
        self.run_worker(fetch_markets(self), exclusive=True)

    def on_api_data_fetched(self, message: ApiDataFetched):
            """Called when ApiDataFetched message is received from the worker."""
            
            self.market_data = message.data 
            
            self.log("Global market_data state updated!")

            message.stop()

    def action_push_screen(self, screen_name: str) -> None:
        """A simple method to handle key bindings that switch screens."""
        self.push_screen(screen_name)
    
    # Note: Textual is asynchronous, so 'async' is often used here
    # but is omitted for simplicity of this example.

if __name__ == "__main__":
    app = RealTimeTUIApp()
    app.run()