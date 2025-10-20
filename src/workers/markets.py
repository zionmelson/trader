import ccxt.async_support as ccxt

async def fetch_market(exchange_id, symbol):
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class()
    try:
        order_book = await exchange.fetch_order_book(symbol)
        return order_book
    except Exception as e:
        print(f"{exchange_id}: Error - {str(e)}")
    finally:
        await exchange.close()

async def fetch_markets(exchange_id):
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class()
    try:
        markets = await exchange.load_markets()
        result = f"{exchange_id}: {len(markets)} markets"
        return result  # only return successful results
    except Exception as e:
        return None
    finally:
        await exchange.close()
        
        
