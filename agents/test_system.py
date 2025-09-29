"""
Test script to validate Trenches AI Agent System functionality
This tests the core system without making actual API calls
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the agents directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.simulation import TrenchesSimulation
from models.config import SimulationConfig
from core.llm_client import LLMClient
from core.simulation_context import SimulationContext


async def test_basic_functionality():
    """Test basic system functionality without API calls"""
    print("🚀 Testing Trenches AI Agent System")
    print("=" * 50)
    
    # Test 1: Configuration loading
    print("1. Testing configuration loading...")
    try:
        config = SimulationConfig()
        print(f"   ✅ Config loaded: {config.rounds} rounds, {config.max_concurrent_agents} max agents")
    except Exception as e:
        print(f"   ❌ Config loading failed: {e}")
        return False
    
    # Test 2: SimulationContext functionality
    print("2. Testing SimulationContext...")
    try:
        context = SimulationContext()
        context.update_trending(["BTC", "ETH", "SOL"])
        context.update_news([{"title": "Test news", "source": "test", "url": "http://test.com"}])
        print(f"   ✅ SimulationContext working: {len(context.trending_tokens)} trending tokens")
    except Exception as e:
        print(f"   ❌ SimulationContext failed: {e}")
        return False
    
    # Test 3: LLM Client initialization
    print("3. Testing LLM Client initialization...")
    try:
        from models.config import LLMConfig
        llm_config = LLMConfig()
        llm_client = LLMClient(llm_config)
        
        # Test provider detection
        test_agent_anthropic = {
            "id": "test_anthropic",
            "llm": {"provider": "anthropic", "model": "claude-3-haiku-20240307"}
        }
        test_agent_groq = {
            "id": "test_groq", 
            "llm": {"provider": "groq", "model": "llama-3.1-8b-instant"}
        }
        
        provider_anthropic = llm_client._get_provider_from_agent(test_agent_anthropic)
        provider_groq = llm_client._get_provider_from_agent(test_agent_groq)
        
        print(f"   ✅ LLM Client working: Anthropic={provider_anthropic}, Groq={provider_groq}")
    except Exception as e:
        print(f"   ❌ LLM Client failed: {e}")
        return False
    
    # Test 4: Agent loading
    print("4. Testing agent loading...")
    try:
        sim = TrenchesSimulation()
        # Test without initializing to avoid API calls
        agent_files = list(Path("agent_spec").glob("*.yaml"))
        anthropic_agents = []
        
        # Find agents configured for Anthropic
        import yaml
        for agent_file in agent_files[:5]:  # Test first 5
            try:
                with open(agent_file, 'r') as f:
                    agent_data = yaml.safe_load(f)
                    if agent_data.get('llm', {}).get('provider') == 'anthropic':
                        anthropic_agents.append(agent_data['id'])
            except:
                continue
        
        print(f"   ✅ Agent loading working: Found {len(agent_files)} total agents")
        print(f"   📊 Anthropic-configured agents: {len(anthropic_agents)} ({', '.join(anthropic_agents[:3])}...)")
    except Exception as e:
        print(f"   ❌ Agent loading failed: {e}")
        return False
    
    # Test 5: Backend connectivity (without simulation)
    print("5. Testing backend connectivity...")
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8080/ping") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Backend connected: {data.get('message', 'OK')}")
                else:
                    print(f"   ⚠️  Backend responded with status {response.status}")
    except Exception as e:
        print(f"   ❌ Backend connection failed: {e}")
        print("   💡 Make sure to run: docker-compose up -d")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Basic functionality test completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Set your ANTHROPIC_API_KEY environment variable")
    print("2. Set your GROQ_API_KEY environment variable") 
    print("3. Run: python run_agent.py")
    print("\n💡 Configured Anthropic agents:", ', '.join(anthropic_agents))
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_basic_functionality())
    sys.exit(0 if success else 1)