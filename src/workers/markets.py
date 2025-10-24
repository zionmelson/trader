# src/workers/markets.py

from datetime import datetime
import pandas as pd
import numpy as np
import talib
import pickle

import ccxt.async_support as ccxt
from textual.app import App
from textual.message import Message

SHORT_DURATION = 5 # weekly x crypto markets
NORMAL_DURATION = 15 # current market trend
LONG_DURATION = 45 # macro adoptance

class ApiDataFetched(Message):
    """A message sent when API data has been successfully fetched."""
    def __init__(self, data: dict) -> None:
        self.data = data
        super().__init__()

async def fetch_ohlcv(app: App):
    """
    Fetches OHLCV data using the CCXT client attached to the main App.
    """
    
    if app.exchange_client is None:
        app.log("Error: CCXT client not initialized.")
        return
    
    try:
        ohlcv = await app.exchange_client.fetch_ohlcv(app.symbols[0], '1d', limit=30)
        timeframes = {
            "5m": await app.exchange_client.fetch_ohlcv('ETH/USD', '5m', limit=(NORMAL_DURATION * 12)),
            "1h": await app.exchange_client.fetch_ohlcv('ETH/USD', '1h',  limit=(NORMAL_DURATION * 4)),
            "1d": await app.exchange_client.fetch_ohlcv('ETH/USD', '1d',  limit=(LONG_DURATION * 1)),
     }
        
        dfs = {}
        for tf, ohlcv in timeframes.items():
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = (
                    pd.to_datetime(df['timestamp'], unit='ms')
                    .dt.tz_localize('UTC')               
                    .dt.tz_convert('America/New_York')    
                )
            df.set_index('timestamp', inplace=True)

            df['log_return'] = np.log(df['close'] / df['close'].shift(1))
            
            df['macd'], df['macdsignal'], df['s_macdhist'] = talib.MACD(
                df['close'].astype(float),
            )
            
            df['s_adx'] = talib.ADX(
                df['high'].astype(float),
                df['low'].astype(float),
                df['close'].astype(float),
                timeperiod=SHORT_DURATION
            )
            df['adx'] = talib.ADX(
                df['high'].astype(float),
                df['low'].astype(float),
                df['close'].astype(float),
                timeperiod=NORMAL_DURATION
            )
            df['l_adx'] = talib.ADX(
                df['high'].astype(float),
                df['low'].astype(float),
                df['close'].astype(float),
                timeperiod=LONG_DURATION
            )
        
            df['s_atr'] = talib.ATR(
                df['high'].astype(float),
                df['low'].astype(float),
                df['close'].astype(float),
                timeperiod=SHORT_DURATION
            )
            df['atr'] = talib.ATR(
                df['high'].astype(float),
                df['low'].astype(float),
                df['close'].astype(float),
                timeperiod=NORMAL_DURATION
            )
            df['l_atr'] = talib.ATR(
                df['high'].astype(float),
                df['low'].astype(float),
                df['close'].astype(float),
                timeperiod=LONG_DURATION
            )

            df['s_rsi'] = talib.RSI(
                df['close'].astype(float),
                timeperiod=SHORT_DURATION
            )
            df['rsi'] = talib.RSI(
                df['close'].astype(float),
                timeperiod=NORMAL_DURATION
            )
            df['l_rsi'] = talib.RSI(
                df['close'].astype(float),
                timeperiod=LONG_DURATION
            )
            
            dfs[tf] = df
    
        pickled_dfs = pickle.dumps(dfs)
        app.post_message(ApiDataFetched(pickled_dfs))
    except Exception as e:
        app.post_message(ApiDataFetched(str(e)))
    finally:
        await app.exchange_client.close()

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
   
        
        
