#!/usr/bin/env python3
"""
Script to select and configure 100 diverse agents for the simulation.
This ensures we have a good mix of personalities, domains, and behaviors.
"""

import os
import yaml
import random
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set


def analyze_agent_diversity(agent_dir: Path) -> Dict:
    """Analyze the diversity of available agents."""
    
    agents_data = []
    
    for agent_file in agent_dir.glob("*.yaml"):
        try:
            with open(agent_file, 'r', encoding='utf-8') as f:
                agent_data = yaml.safe_load(f)
                if agent_data and 'id' in agent_data:
                    agents_data.append({
                        'file': agent_file.name,
                        'id': agent_data['id'],
                        'classification': agent_data.get('classification', 'Unknown'),
                        'domain': agent_data.get('domain', 'general'),
                        'personality': agent_data.get('personality', {}),
                        'alias': agent_data.get('alias', ''),
                        'threat_level': agent_data.get('threat_level', 'Unknown'),
                        'temperament': agent_data.get('personality', {}).get('temperament', 'neutral'),
                        'tone': agent_data.get('personality', {}).get('tone', 'neutral'),
                        'emotionality': agent_data.get('personality', {}).get('emotionality', 'medium'),
                        'decision_bias': agent_data.get('personality', {}).get('decision_bias', 'balanced'),
                    })
        except Exception as e:
            print(f"Warning: Could not process {agent_file.name}: {e}")
    
    return agents_data


def select_diverse_agents(agents_data: List[Dict], target_count: int = 100) -> List[Dict]:
    """Select diverse agents ensuring good representation across different categories."""
    
    # Categorize agents
    by_classification = defaultdict(list)
    by_domain = defaultdict(list)
    by_temperament = defaultdict(list)
    by_tone = defaultdict(list)
    by_threat_level = defaultdict(list)
    
    for agent in agents_data:
        by_classification[agent['classification']].append(agent)
        by_domain[agent['domain']].append(agent)
        by_temperament[agent['temperament']].append(agent)
        by_tone[agent['tone']].append(agent)
        by_threat_level[agent['threat_level']].append(agent)
    
    print(f"📊 Agent Diversity Analysis:")
    print(f"   Classifications: {len(by_classification)} types")
    print(f"   Domains: {len(by_domain)} domains")
    print(f"   Temperaments: {len(by_temperament)} types")
    print(f"   Tones: {len(by_tone)} types")
    print(f"   Threat Levels: {len(by_threat_level)} levels")
    
    # Strategy: Select proportionally from each category
    selected_agents = []
    used_ids = set()
    
    # Priority categories for diversity
    categories = [
        ('classification', by_classification),
        ('domain', by_domain),
        ('temperament', by_temperament),
        ('tone', by_tone),
        ('threat_level', by_threat_level),
    ]
    
    # Round-robin selection across categories
    agents_per_category = target_count // len(categories)
    
    for category_name, category_dict in categories:
        category_selected = 0
        category_agents = []
        
        # Get agents from this category, shuffled
        for category_value, agent_list in category_dict.items():
            category_agents.extend(agent_list)
        
        random.shuffle(category_agents)
        
        # Select agents from this category
        for agent in category_agents:
            if agent['id'] not in used_ids and category_selected < agents_per_category:
                selected_agents.append(agent)
                used_ids.add(agent['id'])
                category_selected += 1
                
                if len(selected_agents) >= target_count:
                    break
        
        if len(selected_agents) >= target_count:
            break
    
    # Fill remaining slots with random agents
    while len(selected_agents) < target_count:
        remaining_agents = [a for a in agents_data if a['id'] not in used_ids]
        if not remaining_agents:
            break
        
        agent = random.choice(remaining_agents)
        selected_agents.append(agent)
        used_ids.add(agent['id'])
    
    return selected_agents[:target_count]


def update_agent_to_anthropic(agent_file: Path) -> bool:
    """Update an agent file to use Anthropic provider."""
    try:
        with open(agent_file, 'r', encoding='utf-8') as f:
            agent_data = yaml.safe_load(f)
        
        # Ensure LLM config exists
        if 'llm' not in agent_data:
            agent_data['llm'] = {}
        
        # Update to use Anthropic
        agent_data['llm']['provider'] = 'anthropic'
        
        # Set appropriate Anthropic model
        current_model = agent_data['llm'].get('model', '')
        if not current_model.startswith('claude'):
            agent_data['llm']['model'] = 'claude-3-haiku-20240307'
        
        # Ensure reasonable temperature
        if 'temperature' not in agent_data['llm']:
            agent_data['llm']['temperature'] = 0.7
        
        # Write back
        with open(agent_file, 'w', encoding='utf-8') as f:
            yaml.dump(agent_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to update {agent_file.name}: {e}")
        return False


def main():
    """Main function to select and configure 100 diverse agents."""
    
    print("🚀 Selecting 100 Diverse Agents for Anthropic")
    print("=" * 50)
    
    agent_dir = Path("agent_spec")
    
    # Analyze all available agents
    print("📊 Analyzing agent diversity...")
    agents_data = analyze_agent_diversity(agent_dir)
    print(f"   Found {len(agents_data)} valid agents")
    
    # Select 100 diverse agents
    print(f"\n🎯 Selecting 100 diverse agents...")
    selected_agents = select_diverse_agents(agents_data, 100)
    
    print(f"✅ Selected {len(selected_agents)} agents")
    
    # Show diversity breakdown
    classifications = Counter(agent['classification'] for agent in selected_agents)
    domains = Counter(agent['domain'] for agent in selected_agents)
    temperaments = Counter(agent['temperament'] for agent in selected_agents)
    tones = Counter(agent['tone'] for agent in selected_agents)
    
    print(f"\n📈 Selected Agent Diversity:")
    print(f"   Classifications: {dict(classifications)}")
    print(f"   Domains: {dict(domains)}")
    print(f"   Temperaments: {dict(temperaments)}")
    print(f"   Tones: {dict(tones)}")
    
    # Update selected agents to use Anthropic
    print(f"\n🔧 Configuring agents for Anthropic...")
    updated_count = 0
    
    for agent in selected_agents:
        agent_file = agent_dir / agent['file']
        if update_agent_to_anthropic(agent_file):
            updated_count += 1
            if updated_count % 10 == 0:
                print(f"   Updated {updated_count}/{len(selected_agents)} agents...")
    
    print(f"\n🎉 Successfully configured {updated_count}/{len(selected_agents)} agents for Anthropic!")
    
    # Save the list of selected agents
    selected_list = [agent['id'] for agent in selected_agents]
    with open('selected_100_agents.txt', 'w') as f:
        for agent_id in selected_list:
            f.write(f"{agent_id}\n")
    
    print(f"📋 Agent list saved to: selected_100_agents.txt")
    
    # Show sample of selected agents
    print(f"\n🎭 Sample of Selected Agents:")
    for i, agent in enumerate(selected_agents[:10]):
        print(f"   {i+1:2d}. {agent['id']} ({agent['classification']}) - {agent['alias']}")
    print(f"   ... and {len(selected_agents) - 10} more diverse agents")


if __name__ == "__main__":
    random.seed(42)  # For reproducible selection
    main()