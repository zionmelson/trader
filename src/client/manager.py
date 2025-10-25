# src/clients/manager.py

import ccxt.async_support as ccxt
import toml
from typing import Dict, Any, List

class DexchangeClient:
    """
    Manages all API interaction for a single dexchange.
    """
    def __init__(self, ccxt_client_instance: ccxt.Exchange, symbols_list: List[str]):
       self._client = ccxt_client_instance
       self.symbols = symbols_list

    def __getattr__(self, name: str) -> Any:
        return getattr(self._client, name)
    
    # --- You can now add your own custom methods here ---

    async def fetch_latest_prices(self) -> Dict[str, float]:
        """
        Fetches the most recent price for all tracked symbols.
        Returns a dict like {'BTC/USDT': 60000.50}
        """
        prices = {}
        try:
            tickers = await self.client.fetch_tickers(self.symbols)
            for symbol in self.symbols:
                # 3. Look up the symbol in the (potentially unordered) tickers dict
                ticker_data = tickers.get(symbol)
                
                # 4. Add to our new dict in the correct order
                if ticker_data and 'last' in ticker_data:
                    prices[symbol] = ticker_data['last']
                else:
                    # Handle if dexchange didn't return data for a symbol
                    prices[symbol] = None
                    
                print(prices[symbol])
        except Exception as e:
            print(f"Error fetching prices for {self.exchange_id}: {e}")
        
            for symbol in self.symbols:
                prices[symbol] = None
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
        """Properly close the dexchange connection."""
        await self.client.close()

class DexManager:
    """
    Orchestrates all ExchangeClients and aggregates their data.
    """
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = toml.load(f)
        
        self.clients: Dict[str, DexchangeClient] = {}
        self.latest_prices: Dict[str, Dict[str, float]] = {}

        for exchange_name in self.config['active_exchanges']:
            if exchange_name in self.config['exchanges']:
                client_config = self.config['exchanges'][exchange_name]
                
                # 1. Build the config for the raw ccxt client
                exchange_class = getattr(ccxt, client_config['id'])
                use_sandbox = client_config.get('paper_trade', False)
                
                ccxt_config = {
                    'apiKey': client_config.get('api_key'),
                    'secret': client_config.get('secret'),
                    'enableRateLimit': True,
                }
                if use_sandbox:
                    ccxt_config['sandbox'] = True
                
                # 2. Create the raw client instance
                raw_client = exchange_class(ccxt_config)
                
                # 3. Create your wrapper, passing the raw client to it
                symbols_list = client_config['symbols']
                self.clients[exchange_name] = DexchangeClient(raw_client, symbols_list)
                
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
        
    def get_price(self, dexchange: str, symbol: str) -> float | None:
        """Lightweight getter for the TUI to use."""
        return self.latest_prices.get(dexchange, {}).get(symbol)

    def get_all_prices(self) -> Dict[str, Dict[str, float]]:
        """Gets the entire aggregated price data structure."""
        return self.latest_prices

    async def place_order(self, dexchange: str, symbol: str, side: str, amount: float):
        """Delegates placing an order to the correct client."""
        if dexchange not in self.clients:
            print(f"Error: No client for dexchange '{dexchange}'.")
            return None
        
        return await self.clients[dexchange].place_order(symbol, side, amount)

    async def close_all(self):
        """Closes all client connections."""
        for client in self.clients.values():
            await client.close()