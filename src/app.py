# src/app.py

from pathlib import Path
import ccxt.async_support as ccxt

from datetime import datetime
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Header, Footer, Static, Button, Digits

from .client.manager import DexManager, DexchangeClient

from .workers.markets import fetch_ohlcv, fetch_prices, ApiDataFetched

from .screens.home import HomeScreen
from .screens.settings import SettingsScreen
from .screens.error import ErrorScreen

PROJECT_ROOT = Path(__file__).parent.parent

CONFIG_FILE_PATH = PROJECT_ROOT / 'config.toml'
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
  
    dexchange_client: DexchangeClient | None = None
    dex_manager: DexManager | None = None
    strategy_data = reactive(b"")  # Global reactive state for market data
    symbols: list[str] = []

    SCREENS = {
        "home": HomeScreen,
        "settings": SettingsScreen,
        "error": ErrorScreen
    }
    
    BINDINGS = [
        ("q", "quit", "quit"),
        ("s", "push_screen('settings')", "settings"), # Direct key navigation
    ]
    
    async def on_mount(self):
        try:
            self.dex_manager = DexManager(CONFIG_FILE_PATH)
            
            # await self._initialize_clients()
            
        except Exception as e:
            self.log(f"Error on mount: {e}")
            self.bell()
            self.show_error_screen()
            return
        
        
        try:
            if not self.dex_manager.clients:
                self.log("No exchanges loaded from config.toml. Strategy worker will not run.")
                self.bell()
                self.show_error_screen()
            else:
                first_client_name = list(self.dex_manager.clients.keys())[0]
                
                self.dexchange_client = self.dex_manager.clients[first_client_name]
                
                self.symbols = self.dexchange_client.symbols
                
                self.log(f"Default strategy client set to: {first_client_name}")
        except Exception as e:
            self.log(f"Error setting default strategy client: {e}")
            self.bell()
            self.show_error_screen()
            return
        
        self.push_screen("home")
        
        self.set_interval(60.0, self.start_strategy_fetch)
        self.set_interval(2.0, self.start_tickers_fetch)
   
    async def _initialize_clients(self):
        """Initialize all exchange clients asynchronously"""
        if not self.dex_manager or not self.dex_manager.clients:
            self.log("❌ No exchanges loaded from config")
            self.bell()
            self.push_screen("error")
            return
        
        # Initialize each client
        for client_name, client in self.dex_manager.clients.items():
            if hasattr(client, 'initialize') and callable(client.initialize):
                await client.initialize()
                self.log(f"✅ Initialized {client_name}")
        
        # Set default strategy client
        first_client_name = list(self.dex_manager.clients.keys())[0]
        self.dexchange_client = self.dex_manager.clients[first_client_name]
        self.symbols = self.dexchange_client.symbols
        
        self.log(f"📊 Default strategy client: {first_client_name}")
        
        # Test blockchain connection for DEX clients
        for client_name, client in self.dex_manager.clients.items():
            if client.is_dex and client.solana_client:
                balance = await client.solana_client.get_balance()
                self.log(f"💰 {client_name} wallet balance: {balance:.4f} SOL")
     
    def start_tickers_fetch(self):
        self.run_worker(fetch_prices(self), exclusive=True)
                
    def start_strategy_fetch(self):
        self.run_worker(fetch_ohlcv(self), exclusive=True)
        
    def on_api_data_fetched(self, message: ApiDataFetched):
            """Called when ApiDataFetched message is received from the worker."""
            
            self.strategy_data = message.data 

            message.stop()

    def show_error_screen(self):
        self.push_screen("error");

if __name__ == "__main__":
    app = RealTimeTUIApp()
    app.run()