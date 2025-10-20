import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Trading Parameters
    STARTING_CAPITAL = 10000.0
    MAX_POSITION_SIZE = 0.1  # 10% of capital per trade
    MAX_LEVERAGE = 3
    
    # Hyperliquid API Configuration
    HYPERLIQUID_MAINNET = "https://api.hyperliquid.xyz"
    HYPERLIQUID_TESTNET = "https://api.hyperliquid-testnet.xyz"
    
    # Use testnet for development
    BASE_URL = HYPERLIQUID_TESTNET
    
    # API Keys (set these in your .env file)
    PRIVATE_KEY = os.getenv("HYPERLIQUID_PRIVATE_KEY")
    WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
    
    # Trading Pairs
    DEFAULT_SYMBOL = "BTC"
    
    # Risk Management
    STOP_LOSS_PCT = 0.02  # 2% stop loss
    TAKE_PROFIT_PCT = 0.04  # 4% take profit
    
    # Logging
    LOG_LEVEL = "INFO"