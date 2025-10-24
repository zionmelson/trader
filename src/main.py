import time
import os
import pandas as pd
import numpy as np
import talib
import asyncio
import ccxt.async_support as ccxt
from datetime import datetime

exchange = ccxt.kraken()

SHORT_DURATION = 5 # weekly x crypto markets
NORMAL_DURATION = 15 # current market trend
LONG_DURATION = 45 # macro adoptance

async def main():
   timeframes = {
      "5m": await exchange.fetch_ohlcv('ETH/USD', '5m', limit=(NORMAL_DURATION * 12)),
      "1h": await exchange.fetch_ohlcv('ETH/USD', '1h',  limit=(NORMAL_DURATION * 4)),
      "1d": await exchange.fetch_ohlcv('ETH/USD', '1d',  limit=(LONG_DURATION * 1)),
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
      
   custom_df = dfs["5m"][["open"]].copy()

   print("\n=== 5m Data ===")
   print(dfs["5m"])
   print("\n=== 1h Data ===")
   print(dfs["1h"])
   print("\n=== 1d Data ===")
   print(dfs["1d"])
   print("\n=== Custom Data (open only) ===")
   print(custom_df)

   
   await exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
