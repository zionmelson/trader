import time
import os
import asyncio
import ccxt.async_support as ccxt

from helper.save_file import save_to_file

from workers.markets import fetch_market, fetch_markets

async def main():
    exchange = ccxt.okx()
    symbols = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'DOGE/USD']
    

if __name__ == "__main__":
    asyncio.run(main())
