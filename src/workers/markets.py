import ccxt.async_support as ccxt
from textual.app import App
from textual.message import Message

class ApiDataFetched(Message):
    """A message sent when API data has been successfully fetched."""
    def __init__(self, data: dict) -> None:
        self.data = data
        super().__init__()

async def fetch_market(app: App):
    """
    Fetches data using the CCXT client attached to the main App.
    """
    
    if app.exchange_client is None:
        app.log("Error: CCXT client not initialized.")
        return
    
    try:
        order_book = await app.exchange_client.fetch_order_book(app.symbols[0])
        app.post_message(ApiDataFetched(order_book))
    except Exception as e:
        app.post_message(ApiDataFetched(str(e)))
    finally:
        await app.exchange_client.close()

async def fetch_markets(app: App):
    """
    Fetches market data for all symbols using the CCXT client.
    """
    if app.exchange_client is None:
        app.log("Error: CCXT client not initialized.")
        return

    try:
        markets = await app.exchange_client.fetch_markets()
        app.post_message(ApiDataFetched(markets))
    except Exception as e:
        app.post_message(ApiDataFetched(str(e)))
    finally:
        await app.exchange_client.close()
   
        
        
