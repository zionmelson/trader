# src/client/solana_client.py
import asyncio
import base64
import json
from typing import Dict, List, Optional, Any
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solana.transaction import Transaction
from solana.keypair import Keypair
from solders.pubkey import Pubkey
from anchorpy import Program, Provider, Wallet, Context

class SolanaAMMClient:
    """
    Client for interacting with Solana AMMs (Raydium, Orca, etc.)
    """
    
    def __init__(self, rpc_url: str, wallet_private_key: str, program_id: str):
        self.rpc_url = rpc_url
        self.wallet = self._load_wallet(wallet_private_key)
        self.program_id = Pubkey.from_string(program_id)
        self.client = None
        self.program = None
        self.provider = None
        
    async def initialize(self):
        """Initialize the Solana client connection"""
        self.client = AsyncClient(self.rpc_url)
        self.provider = Provider(self.client, Wallet(self.wallet))
        # Load your compiled Anchor program
        # self.program = await Program.from_idl(idl, self.program_id, self.provider)
        
    def _load_wallet(self, private_key_str: str) -> Keypair:
        """Load wallet from private key string"""
        try:
            # Handle different private key formats
            if private_key_str.startswith('['):
                # Array format
                key_bytes = json.loads(private_key_str)
            else:
                # Base58 or hex
                if len(private_key_str) == 64:
                    key_bytes = list(bytes.fromhex(private_key_str))
                else:
                    key_bytes = list(base58.b58decode(private_key_str))
            
            return Keypair.from_secret_key(bytes(key_bytes))
        except Exception as e:
            raise Exception(f"Failed to load wallet: {e}")
    
    async def get_amm_price(self, amm_address: str, token_a: str, token_b: str) -> float:
        """
        Get current price from an AMM pool
        """
        try:
            # This would query the AMM pool account to get reserves and calculate price
            # For Raydium, you'd fetch the pool state account
            pool_pubkey = Pubkey.from_string(amm_address)
            
            # Fetch pool data
            pool_data = await self.client.get_account_info(pool_pubkey)
            if not pool_data.value:
                raise Exception(f"Pool not found: {amm_address}")
            
            # Parse pool data to extract reserves and calculate price
            # This is simplified - actual implementation depends on the AMM
            price = await self._calculate_pool_price(pool_data.value.data, token_a, token_b)
            return price
            
        except Exception as e:
            print(f"Error getting AMM price: {e}")
            return 0.0
    
    async def _calculate_pool_price(self, pool_data: bytes, token_a: str, token_b: str) -> float:
        """
        Calculate price from pool data
        This is AMM-specific and would need to be implemented for each DEX
        """
        # Simplified implementation - you'd need to parse the actual pool structure
        # For a constant product pool: price = reserve_b / reserve_a
        try:
            # Mock implementation - replace with actual AMM data parsing
            reserve_a = 1000000  # Would extract from pool_data
            reserve_b = 50000    # Would extract from pool_data
            
            if reserve_a == 0:
                return 0.0
                
            return reserve_b / reserve_a
        except Exception as e:
            print(f"Error calculating pool price: {e}")
            return 0.0
    
    async def execute_arbitrage(
        self, 
        amm_a: str, 
        amm_b: str, 
        token_a: str, 
        token_b: str, 
        amount: float
    ) -> bool:
        """
        Execute arbitrage trade between two AMMs
        """
        try:
            # 1. Check if arbitrage is still profitable
            price_a = await self.get_amm_price(amm_a, token_a, token_b)
            price_b = await self.get_amm_price(amm_b, token_a, token_b)
            
            if not self._is_arbitrage_profitable(price_a, price_b, amount):
                print("Arbitrage no longer profitable")
                return False
            
            # 2. Prepare transaction
            transaction = Transaction()
            
            # 3. Add swap instructions for both AMMs
            # This would use the Anchor program or direct CPI calls
            
            # 4. Send transaction
            signature = await self.provider.send(transaction)
            
            # 5. Confirm transaction
            await self.client.confirm_transaction(signature)
            
            print(f"Arbitrage executed successfully: {signature}")
            return True
            
        except Exception as e:
            print(f"Arbitrage execution failed: {e}")
            return False
    
    def _is_arbitrage_profitable(self, price_a: float, price_b: float, amount: float) -> bool:
        """
        Determine if arbitrage is profitable after fees
        """
        price_diff = abs(price_a - price_b)
        min_price_diff = 0.01  # 1% minimum difference after fees
        return price_diff / min(price_a, price_b) > min_price_diff
    
    async def close(self):
        """Close the Solana client connection"""
        if self.client:
            await self.client.close()