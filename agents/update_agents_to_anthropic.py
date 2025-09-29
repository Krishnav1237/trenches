#!/usr/bin/env python3
"""Script to update agent configurations to use Anthropic provider."""

import os
import yaml
from pathlib import Path

def update_agent_to_anthropic(agent_file: Path):
    """Update a single agent file to use Anthropic provider."""
    try:
        with open(agent_file, 'r') as f:
            agent_data = yaml.safe_load(f)
        
        # Check if agent has LLM config
        if 'llm' not in agent_data:
            agent_data['llm'] = {}
        
        # Update to use Anthropic
        agent_data['llm']['provider'] = 'anthropic'
        
        # Set appropriate Anthropic model if not claude already
        current_model = agent_data['llm'].get('model', '')
        if not current_model.startswith('claude'):
            agent_data['llm']['model'] = 'claude-3-haiku-20240307'
        
        # Ensure reasonable temperature
        if 'temperature' not in agent_data['llm']:
            agent_data['llm']['temperature'] = 0.7
        
        # Write back
        with open(agent_file, 'w') as f:
            yaml.dump(agent_data, f, default_flow_style=False, sort_keys=False)
        
        print(f"✅ Updated {agent_file.name}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update {agent_file.name}: {e}")
        return False

def main():
    """Update specific agents to use Anthropic."""
    agent_dir = Path("agent_spec")
    
    # List of 20 agents to update for testing
    target_agents = [
        "agent_bitcoin_warriors_warrior_01.yaml",
        "agent_bitcoin_warriors_warrior_02.yaml", 
        "agent_crypto_degen_01.yaml",
        "agent_crypto_degen_02.yaml",
        "agent_eth_maxi_01.yaml",
        "agent_eth_maxi_02.yaml",
        "agent_defi_degen_01.yaml",
        "agent_defi_degen_02.yaml",
        "agent_meme_lord_81.yaml",
        "agent_meme_lord_82.yaml",
        "agent_crypto_analyst_26.yaml",
        "agent_crypto_analyst_27.yaml",
        "agent_tech_guru_71.yaml",
        "agent_tech_guru_72.yaml",
        "agent_trader_11.yaml",
        "agent_crypto_trader_46.yaml",
        "agent_nft_collector_01.yaml",
        "agent_nft_collector_02.yaml",
        "agent_yield_farmer_01.yaml",
        "agent_yield_farmer_02.yaml"
    ]
    
    updated_count = 0
    for agent_name in target_agents:
        agent_file = agent_dir / agent_name
        if agent_file.exists():
            if update_agent_to_anthropic(agent_file):
                updated_count += 1
        else:
            print(f"⚠️  Agent file not found: {agent_name}")
    
    print(f"\n🎉 Updated {updated_count}/{len(target_agents)} agents to use Anthropic")

if __name__ == "__main__":
    main()