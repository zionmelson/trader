# main.py

import asyncio
from src.app import RealTimeTUIApp

async def main():
    """
    The main asynchronous entrypoint for the application.
    """
    app = RealTimeTUIApp()
    
    # Use run_async() to run the Textual app
    # This matches the async main stub you provided.
    await app.run_async()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An error occurred: {e}")