# src/client/manager.py

import ccxt.async_support as ccxt
import toml
import asyncio
import os

from typing import Dict, Any, List

from .solana import SolanaAMMClient

class DexchangeClient:
    """
    Manages all API interaction for a single dexchange.
    """
    def __init__(self, ccxt_client_instance: ccxt.Exchange, symbols_list: List[str], client_config: Dict[str, Any]):
       self._client = ccxt_client_instance
       self.symbols = symbols_list
       self.config = client_config 
       self.symbols = client_config.get('symbols', [])
       self.is_dex = client_config.get('is_dex', False)
       self.exchange_id = client_config.get('id', 'unknown_exchange')
       
       self.solana_client = None
       if self.is_dex and client_config.get('rpc_url'):
            self._initialize_solana_client(client_config)

    def __getattr__(self, name: str) -> Any:
        if self.is_dex and not hasattr(self._client, name):
             # Or handle specific known ccxt methods differently if needed
             # print(f"Warning: Method '{name}' not applicable for DEX {self.id}")
            pass
    
        try:
            return getattr(self._client, name)
        except AttributeError:
             raise AttributeError(f"'{self.__class__.__name__}' object (wrapping {self.id}) has no attribute '{name}'")

    def _initialize_solana_client(self, config: Dict[str, Any]):
        """Initialize Solana client for DEX operations"""
        try:
            
            private_key = os.getenv(config.get('wallet_private_key_env', ''))
            if not private_key:
                print(f"Warning: No private key found for DEX {self.exchange_id}")
                return
                
            self.solana_client = SolanaAMMClient(
                rpc_url=config['rpc_url'],
                wallet_private_key=private_key,
                program_id=config.get('program_id', 'Gz1uGFbdpM9Bn255ydYmCRgM1JZNiEYFC68pVi3Bhwfg')
            )
            
        except ImportError:
            print("Solana dependencies not available")
        except Exception as e:
            print(f"Failed to initialize Solana client: {e}")
    
    def _parse_symbol(self, symbol: str) -> tuple[str, str]:
        """Parse trading symbol into token addresses"""
        # Map symbols to actual Solana token addresses
        token_map = {
            "SOL/USDC": ("So11111111111111111111111111111111111111112", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"),
            "RAY/SOL": ("4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R", "So11111111111111111111111111111111111111112"),
        }
        base, quote = symbol.split('/')
        return token_map.get(symbol, (base, quote))
    
    def _get_amm_address(self, symbol: str) -> str:
        """Get AMM pool address for symbol"""
        # This would map to actual Raydium pool addresses
        amm_map = {
            "SOL/USDC": "58oQChx4yWmvKdwLLZzBi4ChoCc2fqCUWBkwMihLYQo2",
            "RAY/SOL": "AVs9TA4nWDzfPJE9gGVNJMVhcQy3V9PGazuz33BfG2RA",
        }
        return amm_map.get(symbol, "")

    async def create_order(self, symbol: str, side: str, amount: float, price: float = None):
        """
        Overrides the create_order method.
        Executes custom DEX logic or falls back to ccxt.
        """
        order_type = 'limit' if price else 'market'

        if self.is_dex:
            # --- CUSTOM DEX LOGIC ---
            print(f"Executing custom DEX order logic for {self.id}...")
            # Placeholder for your Rust interaction:
            # Example:
            # command = [
            #     "path/to/your/rust_solana_cli",
            #     "place-order",
            #     "--rpc", self.rpc_url,
            #     "--key", self.wallet_private_key, # Be careful with key handling!
            #     "--market", symbol, # You might need to map symbols (e.g., SOL/USDC -> market address)
            #     "--side", side,
            #     "--amount", str(amount),
            # ]
            # if price:
            #     command.extend(["--price", str(price)])
            #
            # try:
            #     # Run the Rust executable
            #     result = subprocess.run(command, capture_output=True, text=True, check=True)
            #     print("DEX Order Success:", result.stdout)
            #     # Parse result.stdout to return a consistent order structure if possible
            #     return {"info": result.stdout, "id": "...", "symbol": symbol, ...} # Mock ccxt-like structure
            # except subprocess.CalledProcessError as e:
            #     print(f"DEX Order Error for {self.id}: {e.stderr}")
            #     return None
            # except Exception as e:
            #      print(f"Unexpected error during DEX order: {e}")
            #      return None

            # --- For now, just simulate ---
            print("SIMULATED DEX order placed.")
            await asyncio.sleep(0.1) # Simulate async work
            return {"info": "Simulated DEX Order", "id": "dex-order-123", "symbol": symbol}
            # --- END CUSTOM DEX LOGIC ---

        else:
            if not self._client:
                 print(f"Error: ccxt client not available for {self.id}")
                 return None
            try:
                order = await self._client.create_order(symbol, order_type, side, amount, price)
                return order
            except Exception as e:
                # Use self.id (from __getattr__) for logging CEX ID
                print(f"CEX Order failed on {self.id}: {e}")
                return None

    async def fetch_latest_prices(self) -> Dict[str, float]:
        """
        Fetches the most recent price for all tracked symbols.
        Returns a dict like {'BTC/USDT': 60000.50}
        """
        prices = {}
       
        if self.is_dex and self.solana_client:
            try:
                if not hasattr(self, '_solana_initialized'):
                    await self.solana_client.initialize()
                    self._solana_initialized = True
                
                for symbol in self.symbols:
                    # Map symbol to Solana token addresses
                    token_a, token_b = self._parse_symbol(symbol)
                    amm_address = self._get_amm_address(symbol)
                    
                    if amm_address:
                        price = await self.solana_client.get_amm_price(
                            amm_address, token_a, token_b
                        )
                        prices[symbol] = price
                    else:
                        prices[symbol] = None
                        
            except Exception as e:
                print(f"Error fetching DEX prices from Solana: {e}")
                for symbol in self.symbols:
                    prices[symbol] = None
        else:
            if not self._client:
                print(f"Error: ccxt client not available for {self.id}")
                return None
            try:
                tickers = await self._client.fetch_tickers(self.symbols)
                for symbol in self.symbols:
                    # 3. Look up the symbol in the (potentially unordered) tickers dict
                    ticker_data = tickers.get(symbol)
                    
                # 4. Add to our new dict in the correct order
                    if ticker_data and 'last' in ticker_data:
                        prices[symbol] = ticker_data['last']
                    else:
                        # Handle if dexchange didn't return data for a symbol
                        prices[symbol] = None
            except Exception as e:
                print(f"Error fetching prices for {self.id}: {e}")
                for symbol in self.symbols:
                    prices[symbol] = None
                
        return prices

    async def close(self):
        """ Overrides close method. Uses self.is_dex. """
        print(f"Attempting to close connection for {self.exchange_id}...")
        if self.is_dex:
            # --- CUSTOM DEX CLOSE LOGIC ---
            print(f"Executing custom DEX close logic for {self.exchange_id} (if any)...")
            await asyncio.sleep(0.01) # Simulate
            print(f"DEX {self.exchange_id} cleanup complete.")
            # --- END CUSTOM DEX CLOSE LOGIC ---
        else:
            # --- Standard CCXT Logic ---
            if not self._client:
                 # print(f"Warning: No ccxt client to close for {self.exchange_id}") # Optional warning
                 return
            try:
                await self._client.close()
                print(f"Closed ccxt client for {self.exchange_id}.")
            except Exception as e:
                 print(f"Error closing ccxt client for {self.exchange_id}: {e}") # Use stored ID


class DexManager:
    """
    Orchestrates all ExchangeClients and aggregates their data.
    """
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = toml.load(f)
        required_fields = ['id', 'api_key', 'secret', 'symbols']

        self.clients: Dict[str, DexchangeClient] = {}
        self.latest_prices: Dict[str, Dict[str, float]] = {}
        
        for exchange_name in self.config['active_exchanges']:
            if exchange_name in self.config['exchanges']:
                client_config = self.config['exchanges'][exchange_name]
                raw_client = None # Placeholder for the raw client

                # Only create raw ccxt client if NOT a DEX
                if not client_config.get('is_dex', False):
                    try:
                        exchange_class = getattr(ccxt, client_config['id'])
                        use_sandbox = client_config.get('sandbox', False)
                        ccxt_config = {
                            'apiKey': client_config.get('api_key'),
                            'secret': client_config.get('secret'),
                            'enableRateLimit': True,
                            'timeout': 30000,
                        }
                        if use_sandbox:
                            ccxt_config['sandbox'] = True
                        raw_client = exchange_class(ccxt_config)
                    except Exception as e:
                         print(f"Failed to initialize ccxt client for {exchange_name}: {e}")
                         # Decide if you want to skip this client or continue without a raw client
                         # raw_client = None # Ensure it's None if init fails

                # Create the wrapper, passing the raw client (which might be None for DEX)
                # and the FULL config section
                self.clients[exchange_name] = DexchangeClient(raw_client, client_config.get('symbols', []), client_config)

                self.latest_prices[exchange_name] = {}
                # self.ohlcv_data[exchange_name] = {} # If using OHLCV manager
            else:
                print(f"Warning: Config for '{exchange_name}' not found.")

    async def update_all_prices(self):
        """
        Polls all clients for their latest prices and updates
        the internal state.
        """
        for name, client in self.clients.items():
            self.latest_prices[name] = await client.fetch_latest_prices()
  
    async def update_strategy_prices(self):
        pass;
        
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