#!/usr/bin/env python3
"""Direct test of individual agents with Anthropic provider."""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from core.simulation import TrenchesSimulation
from core.simulation_context import SimulationContext
from models.entities import Tweet
from tools.market_data_tools import get_token_price
from tools.dex_screener import get_liquidity_pool_info
from tools.onchain_tools import get_eth_balance


async def test_individual_agents():
    """Test individual agents to ensure they can generate tweets."""
    print("🎯 Testing Individual Anthropic Agents")
    print("="*50)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    
    try:
        # Initialize simulation
        config_path = Path("config")
        simulation = TrenchesSimulation(config_path)
        
        # Register tools
        tools = {
            "get_token_price": get_token_price,
            "get_liquidity_pool_info": get_liquidity_pool_info,
            "get_eth_balance": get_eth_balance
        }
        simulation.register_tools(tools)
        
        async with simulation:
            await simulation.initialize()
            
            # Get Anthropic agents
            anthropic_agents = {
                agent_id: agent for agent_id, agent in simulation.agents.items()
                if agent.get('llm', {}).get('provider') == 'anthropic'
            }
            
            print(f"📊 Found {len(anthropic_agents)} Anthropic agents")
            
            # Test first 5 agents individually
            test_agents = list(anthropic_agents.items())[:5]
            
            # Create a simple context
            context = SimulationContext()
            context.trending_tokens = ["BTC", "ETH", "SOL"]
            context.activity_level = "high"
            context.sentiment = "positive"
            
            print(f"\n🧪 Testing {len(test_agents)} agents individually...")
            
            successful_tests = 0
            for agent_id, agent in test_agents:
                try:
                    print(f"\n🤖 Testing agent: {agent_id}")
                    print(f"   Provider: {agent.get('llm', {}).get('provider')}")
                    print(f"   Model: {agent.get('llm', {}).get('model')}")
                    
                    # Execute tweet action directly
                    await simulation._execute_tweet(agent, context)
                    
                    print(f"✅ {agent_id} successfully posted a tweet!")
                    successful_tests += 1
                    
                except Exception as e:
                    print(f"❌ {agent_id} failed: {e}")
                    import traceback
                    traceback.print_exc()
            
            print(f"\n📈 Results: {successful_tests}/{len(test_agents)} agents successfully posted tweets")
            
            # Check backend for posted tweets
            try:
                tweets = await simulation.api_client.get_timeline(limit=10)
                print(f"📝 Found {len(tweets)} recent tweets in backend:")
                for tweet in tweets[:5]:  # Show first 5
                    print(f"   @{tweet.agent_id}: {tweet.content[:80]}...")
            except Exception as e:
                print(f"⚠️  Could not fetch tweets from backend: {e}")
            
            return successful_tests > 0
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    print("🧪 Direct Anthropic Agent Test")
    print("="*50)
    
    # Check API key
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    if not anthropic_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        return
    
    print(f"✅ Anthropic API key found")
    
    # Run the test
    success = await test_individual_agents()
    
    if success:
        print("\n🎉 Anthropic agents are working and posting tweets!")
    else:
        print("\n💥 Test failed. Check the logs above for details.")


if __name__ == "__main__":
    asyncio.run(main())