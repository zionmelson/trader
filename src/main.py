import time
import os
import asyncio
import ccxt.async_support as ccxt

from helper.save_file import save_to_file

from helper.filter_leverage import filter_leverage_exchanges
from helper.filter_sandbox import filter_sandbox_exchanges

async def main():
   await filter_leverage_exchanges()
   await filter_sandbox_exchanges()


if __name__ == "__main__":
    asyncio.run(main())
