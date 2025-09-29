#!/usr/bin/env python3
"""Test script for 20-agent prototype with Anthropic provider."""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from core.simulation import TrenchesSimulation
from tools.market_data_tools import get_token_price
from tools.dex_screener import get_liquidity_pool_info
from tools.onchain_tools import get_eth_balance


async def test_20_agents():
    """Test the system with 20 Anthropic-configured agents."""
    print("🚀 Starting 20-Agent Anthropic Test")
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
        
        print("🔧 Tools registered successfully")
        
        # Use context manager
        async with simulation:
            await simulation.initialize()
            
            # Load all agents and filter for Anthropic ones
            all_agents = simulation.agents
            anthropic_agents = {
                agent_id: agent for agent_id, agent in all_agents.items()
                if agent.get('llm', {}).get('provider') == 'anthropic'
            }
            
            print(f"📊 Found {len(anthropic_agents)} Anthropic-configured agents out of {len(all_agents)} total agents")
            
            if len(anthropic_agents) == 0:
                print("❌ No Anthropic agents found! Make sure you've updated agent configurations.")
                return
            
            # Limit to 20 agents for testing
            test_agents = dict(list(anthropic_agents.items())[:20])
            simulation.agents = test_agents
            
            print(f"🎯 Testing with {len(test_agents)} agents:")
            for agent_id in test_agents.keys():
                print(f"  • {agent_id}")
            
            # Override simulation config for testing
            simulation.sim_config.rounds = 2
            simulation.sim_config.max_concurrent_agents = 10
            simulation.sim_config.round_delay_range = [3, 5]
            
            print("\n🏁 Starting simulation...")
            await simulation.run_simulation()
            
            print("\n✅ 20-Agent Anthropic test completed successfully!")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def check_prerequisites():
    """Check if all prerequisites are met."""
    print("🔍 Checking prerequisites...")
    
    # Check API key
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    if not anthropic_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        return False
    
    print(f"✅ Anthropic API key found (length: {len(anthropic_key)})")
    
    # Check if backend might be running
    print("ℹ️  Make sure backend is running: docker compose up -d")
    
    return True


async def main():
    """Main test function."""
    print("🧪 Trenches 20-Agent Anthropic Test Suite")
    print("="*50)
    
    if not check_prerequisites():
        print("❌ Prerequisites not met. Please check your configuration.")
        return
    
    # Run the test
    success = await test_20_agents()
    
    if success:
        print("\n🎉 All tests passed! Your 20-agent Anthropic system is working!")
    else:
        print("\n💥 Tests failed. Check the logs above for details.")


if __name__ == "__main__":
    asyncio.run(main())