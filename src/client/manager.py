# src/clients/manager.py

import ccxt.async_support as ccxt
import toml
from typing import Dict, Any, List

class ExchangeClient:
    """
    Manages all API interaction for a single exchange.
    """
    def __init__(self, config: Dict[str, Any]):
        self.exchange_id = config['id']
        self.symbols = config['symbols']
        
        # Instantiate the CCXT client
        exchange_class = getattr(ccxt, self.exchange_id)
        self.client = exchange_class({
            'apiKey': config.get('api_key'), # Use .get() for safety
            'secret': config.get('secret'),
            'enableRateLimit': True,
        })

    async def fetch_latest_prices(self) -> Dict[str, float]:
        """
        Fetches the most recent price for all tracked symbols.
        Returns a dict like {'BTC/USDT': 60000.50}
        """
        prices = {}
        try:
            tickers = await self.client.fetch_tickers(self.symbols)
            for symbol, ticker_data in tickers.items():
                if 'last' in ticker_data:
                    prices[symbol] = ticker_data['last']
        except Exception as e:
            print(f"Error fetching prices for {self.exchange_id}: {e}")
        
        return prices

    async def place_order(self, symbol: str, side: str, amount: float, price: float = None):
        """Wrapper for placing an order."""
        print(f"Placing {side} order for {amount} {symbol} on {self.exchange_id}")
        try:
            order_type = 'limit' if price else 'market'
            order = await self.client.create_order(symbol, order_type, side, amount, price)
            return order
        except Exception as e:
            print(f"Order failed on {self.exchange_id}: {e}")
            return None

    async def close(self):
        """Properly close the exchange connection."""
        await self.client.close()


class PriceManager:
    """
    Orchestrates all ExchangeClients and aggregates their data.
    """
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = toml.load(f)
        
        self.clients: Dict[str, ExchangeClient] = {}
        self.latest_prices: Dict[str, Dict[str, float]] = {}

        for exchange_name in self.config['active_exchanges']:
            if exchange_name in self.config['exchanges']:
                client_config = self.config['exchanges'][exchange_name]
                self.clients[exchange_name] = ExchangeClient(client_config)
                self.latest_prices[exchange_name] = {}
            else:
                print(f"Warning: Config for '{exchange_name}' not found.")

    async def update_all_prices(self):
        """
        Polls all clients for their latest prices and updates
        the internal state.
        """
        for name, client in self.clients.items():
            self.latest_prices[name] = await client.fetch_latest_prices()
        
        # This log is helpful for debugging
        self.log(f"Prices updated: {self.latest_prices}")

    def get_price(self, exchange: str, symbol: str) -> float | None:
        """Lightweight getter for the TUI to use."""
        return self.latest_prices.get(exchange, {}).get(symbol)

    def get_all_prices(self) -> Dict[str, Dict[str, float]]:
        """Gets the entire aggregated price data structure."""
        return self.latest_prices

    async def place_order(self, exchange: str, symbol: str, side: str, amount: float):
        """Delegates placing an order to the correct client."""
        if exchange not in self.clients:
            print(f"Error: No client for exchange '{exchange}'.")
            return None
        
        return await self.clients[exchange].place_order(symbol, side, amount)

    async def close_all(self):
        """Closes all client connections."""
        for client in self.clients.values():
            await client.close()