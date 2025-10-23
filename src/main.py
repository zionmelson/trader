import time
import os
import pandas as pd
import numpy as np
import talib
import asyncio
import ccxt.async_support as ccxt
from datetime import datetime

exchange = ccxt.kraken()

async def main():
   five_minute = pd.DataFrame()
   one_hour = pd.DataFrame()
   one_day = pd.DataFrame()
   
   five_minute_ohlcv = await exchange.fetch_ohlcv('BTC/USD', '5m', limit=10)
   one_hour_ohlcv = await exchange.fetch_ohlcv('BTC/USD', '1h', limit=10)
   one_day_ohlcv = await exchange.fetch_ohlcv('BTC/USD', '1d', limit=10)
   
   df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
   df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
   print(df)
   df.set_index('timestamp', inplace=True)

   open_price = df['open'].values
   high_price = df['high'].values
   low_price = df['low'].values
   close_price = df['close'].values

   num = talib.CDLMORNINGSTAR(open_price, high_price, low_price, close_price)
   
   await exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
