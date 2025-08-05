#!/usr/bin/env python3
"""
Trenches Agent Runner - Simplified main entry point using modular architecture.
"""
import asyncio
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from tools.onchain_tools import get_eth_balance, get_latest_transactions, get_erc20_transfers
from tools.market_data_tools import get_crypto_prices
from tools.market_data_tools import get_token_price
from tools.liquidity import get_liquidity_pool_info
from tools.orderbook import get_order_book
from tools.news_sources import get_aggregated_news
from tools.market_data_tools import get_top_symbols


import random

symbols = get_top_symbols()
symbol = random.choice(symbols)

# Add the current directory to Python path to fix relative imports
sys.path.append(str(Path(__file__).parent))

# Import the new modular components
from core.simulation import TrenchesSimulation
from tools.onchain_tools import get_eth_balance

# Load environment variables
load_dotenv()


async def main():
    """Main entry point for the Trenches agent simulation"""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Validate all required API keys
    if not os.getenv('GROQ_API_KEY'):
        logger.error("Groq API key not found in environment.")
        return
    logger.info("Groq API key found.")

    if not os.getenv('ETHERSCAN_API_KEY'):
        logger.error("Etherscan API key not found in environment.")
        return
    logger.info("Etherscan API key found.")
    
    # NEW: Validate Coinranking API key
    if not os.getenv('COINRANKING_API_KEY'):
        logger.error("Coinranking API key not found.")
        return
    logger.info("Coinranking API key found.")

    if not os.getenv('NEWS_API_KEY'):
        logger.error("NewsAPI key not found in environment.")
        return
    logger.info("NewsAPI key found.")

    if not os.getenv('CRYPTOPANIC_API_KEY'):
        logger.error("CryptoPanic API key not found in environment.")
        return
    logger.info("CryptoPanic API key found.")

    if not os.getenv('REDDIT_CLIENT_ID') or not os.getenv('REDDIT_CLIENT_SECRET'):
        logger.error("Reddit API credentials not found in environment.")
        return

    config_dir = Path(os.getenv('CONFIG_DIR', 'config'))

    # Define the dictionary of available tools
    tools = {
        "get_eth_balance": get_eth_balance,
        "get_latest_transactions": get_latest_transactions,
        "get_erc20_transfers": get_erc20_transfers,
        "get_crypto_prices": get_crypto_prices,
        "get_token_price": get_token_price,
        "get_liquidity_pool_info": get_liquidity_pool_info,
        "get_order_book": get_order_book,
        "get_aggregated_news": get_aggregated_news,
         "tool_name": "get_token_price",
        "args": {"symbol": symbol}
    }
    
    try:
        # Initialize, register tools, and run simulation
        async with TrenchesSimulation(config_dir) as simulation:
            simulation.register_tools(tools)
            await simulation.run_simulation()

    except Exception as e:
        logger.error(f"Simulation failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    print("🔎 Fetching crypto-related news...")
    
    news, tokens = get_aggregated_news(limit=3)
    
    print("\n📰 Aggregated News:")
    for item in news:
        if "error" in item:
            print(f"[{item['source']}] ❌ Error: {item['error']}")
        else:
            print(f"[{item['source']}] {item.get('title')} - {item.get('url')}")
    
    print("\n🪙 Trending Tokens Detected:")
    if tokens:
        print(", ".join(tokens))
    else:
        print("No tokens identified.")

    asyncio.run(main())
