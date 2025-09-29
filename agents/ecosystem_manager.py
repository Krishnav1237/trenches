#!/usr/bin/env python3
"""
Ecosystem Manager - Orchestrates diverse ecosystem agents with realistic social dynamics
"""

import random
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from ecosystem_agent_generator import EcosystemAgentGenerator
from ecosystem_warriors_generator import EcosystemWarriorsGenerator


class EcosystemManager:
    """Manages diverse ecosystem agents with realistic social dynamics"""
    
    def __init__(self, output_dir: Path = None):
        if output_dir is None:
            output_dir = Path("agent_spec")
        self.output_dir = output_dir
        self.ecosystem_generator = EcosystemAgentGenerator(output_dir)
        self.warriors_generator = EcosystemWarriorsGenerator(output_dir)
        
        # Ecosystem relationships and dynamics
        self.ecosystem_relationships = self._load_ecosystem_relationships()
        self.social_dynamics = self._load_social_dynamics()
    
    def _load_ecosystem_relationships(self) -> Dict[str, Any]:
        """Load ecosystem relationships and conflicts"""
        return {
            "ethereum": {
                "allies": ["arbitrum", "optimism", "base", "polygon"],
                "enemies": ["solana", "bsc", "avalanche", "cardano"],
                "neutral": ["bitcoin", "cosmos", "polkadot"],
                "conflict_level": 0.8
            },
            "solana": {
                "allies": ["raydium", "serum", "orca"],
                "enemies": ["ethereum", "bitcoin", "bsc", "polygon"],
                "neutral": ["avalanche", "cosmos", "polkadot"],
                "conflict_level": 0.9
            },
            "bitcoin": {
                "allies": ["lightning", "stacks", "rootstock"],
                "enemies": ["ethereum", "solana", "bsc", "polygon", "avalanche"],
                "neutral": ["cosmos", "polkadot", "cardano"],
                "conflict_level": 0.7
            },
            "defi": {
                "allies": ["ethereum", "arbitrum", "optimism", "polygon"],
                "enemies": ["tradfi", "traditional_finance"],
                "neutral": ["bitcoin", "solana", "cosmos"],
                "conflict_level": 0.9
            },
            "tradfi": {
                "allies": ["traditional_finance", "regulated_finance"],
                "enemies": ["ethereum", "solana", "bitcoin", "defi"],
                "neutral": ["stablecoin", "layer2"],
                "conflict_level": 0.6
            }
        }
    
    def _load_social_dynamics(self) -> Dict[str, Any]:
        """Load social dynamics and interaction patterns"""
        return {
            "interaction_patterns": {
                "ethereum_warriors": {
                    "likes": ["ethereum_warriors", "defi_warriors", "layer2_warriors"],
                    "dislikes": ["solana_warriors", "bsc_warriors", "avalanche_warriors"],
                    "neutral": ["bitcoin_warriors", "tradfi_warriors"]
                },
                "solana_warriors": {
                    "likes": ["solana_warriors", "defi_warriors"],
                    "dislikes": ["ethereum_warriors", "bitcoin_warriors", "tradfi_warriors"],
                    "neutral": ["nft_warriors", "gaming_warriors"]
                },
                "bitcoin_warriors": {
                    "likes": ["bitcoin_warriors", "privacy_warriors"],
                    "dislikes": ["ethereum_warriors", "solana_warriors", "defi_warriors"],
                    "neutral": ["tradfi_warriors", "nft_warriors"]
                },
                "defi_warriors": {
                    "likes": ["ethereum_warriors", "defi_warriors", "layer2_warriors"],
                    "dislikes": ["tradfi_warriors", "bitcoin_warriors"],
                    "neutral": ["solana_warriors", "nft_warriors"]
                },
                "tradfi_warriors": {
                    "likes": ["tradfi_warriors", "regulation_warriors"],
                    "dislikes": ["ethereum_warriors", "solana_warriors", "defi_warriors"],
                    "neutral": ["bitcoin_warriors", "stablecoin_warriors"]
                }
            },
            "content_patterns": {
                "ethereum_warriors": {
                    "topics": ["Ethereum", "DeFi", "Layer 2", "Smart Contracts", "ETH 2.0"],
                    "sentiment": "bullish",
                    "engagement_style": "technical"
                },
                "solana_warriors": {
                    "topics": ["Solana", "Speed", "Low Fees", "DeFi", "NFTs"],
                    "sentiment": "bullish",
                    "engagement_style": "enthusiastic"
                },
                "bitcoin_warriors": {
                    "topics": ["Bitcoin", "Digital Gold", "Store of Value", "Decentralization"],
                    "sentiment": "bullish",
                    "engagement_style": "serious"
                },
                "defi_warriors": {
                    "topics": ["DeFi", "Yield Farming", "Liquidity Mining", "APY"],
                    "sentiment": "bullish",
                    "engagement_style": "excited"
                },
                "tradfi_warriors": {
                    "topics": ["Traditional Finance", "Regulation", "Risk Management", "Stability"],
                    "sentiment": "skeptical",
                    "engagement_style": "analytical"
                }
            }
        }
    
    def generate_complete_ecosystem(self, total_agents: int = 200) -> List[Dict[str, Any]]:
        """Generate a complete ecosystem with diverse agents"""
        print(f"🌍 Generating complete ecosystem with {total_agents} agents...")
        
        # Distribution of agent types
        distribution = {
            "ecosystem_warriors": int(total_agents * 0.4),  # 40% warriors
            "ecosystem_agents": int(total_agents * 0.3),    # 30% regular agents
            "niche_specialists": int(total_agents * 0.2),   # 20% niche specialists
            "contrarian_agents": int(total_agents * 0.1)    # 10% contrarian agents
        }
        
        all_agents = []
        
        # Generate ecosystem warriors
        if distribution["ecosystem_warriors"] > 0:
            warriors = self.warriors_generator.generate_ecosystem_warriors(
                distribution["ecosystem_warriors"] // 5  # 5 ecosystems
            )
            all_agents.extend(warriors)
        
        # Generate regular ecosystem agents
        if distribution["ecosystem_agents"] > 0:
            agents = self.ecosystem_generator.generate_ecosystem_agents(
                distribution["ecosystem_agents"]
            )
            all_agents.extend(agents)
        
        # Generate niche specialists
        if distribution["niche_specialists"] > 0:
            specialists = self._generate_niche_specialists(
                distribution["niche_specialists"]
            )
            all_agents.extend(specialists)
        
        # Generate contrarian agents
        if distribution["contrarian_agents"] > 0:
            contrarians = self._generate_contrarian_agents(
                distribution["contrarian_agents"]
            )
            all_agents.extend(contrarians)
        
        # Add social dynamics and relationships
        all_agents = self._add_social_dynamics(all_agents)
        
        return all_agents
    
    def _generate_niche_specialists(self, count: int) -> List[Dict[str, Any]]:
        """Generate niche specialists (NFT, Gaming, Privacy, etc.)"""
        specialists = []
        
        niche_types = [
            "nft_specialist", "gaming_specialist", "privacy_specialist",
            "meme_specialist", "stablecoin_specialist", "layer2_specialist",
            "cross_chain_specialist", "governance_specialist"
        ]
        
        for i in range(count):
            niche_type = random.choice(niche_types)
            specialist = self._generate_niche_specialist(niche_type, i + 1)
            specialists.append(specialist)
        
        return specialists
    
    def _generate_niche_specialist(self, niche_type: str, number: int) -> Dict[str, Any]:
        """Generate a single niche specialist"""
        agent_id = f"agent_{niche_type}_{number:02d}"
        
        # Niche-specific data
        niche_data = {
            "nft_specialist": {
                "alias": f"NFTCollector{number:02d}",
                "personality": {
                    "temperament": "artistic",
                    "tone": "creative",
                    "decision_bias": "aesthetic",
                    "emotionality": "medium",
                    "description": "NFT specialist who values digital art and culture"
                },
                "skills": ["Digital Art", "NFT Curation", "Community Building", "Art Analysis", "NFT Ecosystem"],
                "target_assets": ["ETH", "SOL", "MATIC", "AVAX", "FLOW"],
                "catchphrase": "Art is the future!"
            },
            "gaming_specialist": {
                "alias": f"GamingGuru{number:02d}",
                "personality": {
                    "temperament": "playful",
                    "tone": "enthusiastic",
                    "decision_bias": "fun",
                    "emotionality": "high",
                    "description": "Gaming specialist who believes in the future of GameFi"
                },
                "skills": ["GameFi", "NFT Gaming", "Community Building", "Gaming Analysis", "Gaming Ecosystem"],
                "target_assets": ["AXS", "SAND", "MANA", "GALA", "ENJ"],
                "catchphrase": "Play to earn!"
            },
            "privacy_specialist": {
                "alias": f"PrivacyActivist{number:02d}",
                "personality": {
                    "temperament": "paranoid",
                    "tone": "urgent",
                    "decision_bias": "privacy_first",
                    "emotionality": "high",
                    "description": "Privacy specialist who values anonymity and decentralization"
                },
                "skills": ["Privacy Technology", "Cryptography", "Anonymity", "Decentralization", "Privacy Coins"],
                "target_assets": ["XMR", "ZEC", "DASH", "SCRT", "ZEN"],
                "catchphrase": "Privacy is a human right!"
            }
        }
        
        data = niche_data.get(niche_type, niche_data["nft_specialist"])
        
        return {
            "id": agent_id,
            "personality": data["personality"],
            "alias": data["alias"],
            "classification": niche_type,
            "threat_level": "Delta",
            "skills": data["skills"],
            "weaknesses": ["Niche Focus", "Limited Scope", "Ecosystem Dependency"],
            "catchphrase": data["catchphrase"],
            "physical_description": f"Specialist in {niche_type} with deep knowledge and passion",
            "origin_story": f"Became a specialist in {niche_type} after discovering its potential",
            "ecosystem": niche_type,
            "bias_strength": 0.7,
            "bullish_level": 0.8,
            "target_assets": data["target_assets"],
            "llm": {
                "model": random.choice(["gpt-4o-mini", "claude-3-haiku-20240307"]),
                "temperature": random.uniform(0.7, 0.9),
                "max_tokens": random.randint(100, 200),
                "top_p": random.uniform(0.8, 0.95)
            },
            "activity": {
                "schedule": "cron: */8 * * * *",
                "actions_per_awake": [1, 3]
            },
            "memory": {
                "short_term_window": random.randint(10, 20),
                "long_term_vector_db": {
                    "enabled": True,
                    "collection_name": f"{niche_type}_memory",
                    "similarity_threshold": random.uniform(0.7, 0.9)
                }
            }
        }
    
    def _generate_contrarian_agents(self, count: int) -> List[Dict[str, Any]]:
        """Generate contrarian agents with different perspectives"""
        contrarians = []
        
        contrarian_types = [
            "crypto_skeptic", "regulation_expert", "technical_critic",
            "market_crash_predictor", "bubble_detector", "reality_checker"
        ]
        
        for i in range(count):
            contrarian_type = random.choice(contrarian_types)
            contrarian = self._generate_contrarian_agent(contrarian_type, i + 1)
            contrarians.append(contrarian)
        
        return contrarians
    
    def _generate_contrarian_agent(self, contrarian_type: str, number: int) -> Dict[str, Any]:
        """Generate a single contrarian agent"""
        agent_id = f"agent_{contrarian_type}_{number:02d}"
        
        contrarian_data = {
            "crypto_skeptic": {
                "alias": f"CryptoSkeptic{number:02d}",
                "personality": {
                    "temperament": "skeptical",
                    "tone": "critical",
                    "decision_bias": "contrarian",
                    "emotionality": "low",
                    "description": "Crypto skeptic who questions the value of most projects"
                },
                "catchphrase": "Prove it!"
            },
            "regulation_expert": {
                "alias": f"RegulationExpert{number:02d}",
                "personality": {
                    "temperament": "analytical",
                    "tone": "professional",
                    "decision_bias": "regulatory",
                    "emotionality": "low",
                    "description": "Regulation expert who focuses on compliance and legal issues"
                },
                "catchphrase": "Regulation is coming!"
            },
            "technical_critic": {
                "alias": f"TechnicalCritic{number:02d}",
                "personality": {
                    "temperament": "analytical",
                    "tone": "critical",
                    "decision_bias": "technical",
                    "emotionality": "low",
                    "description": "Technical critic who focuses on fundamental flaws"
                },
                "catchphrase": "The technology is flawed!"
            }
        }
        
        data = contrarian_data.get(contrarian_type, contrarian_data["crypto_skeptic"])
        
        return {
            "id": agent_id,
            "personality": data["personality"],
            "alias": data["alias"],
            "classification": contrarian_type,
            "threat_level": "Gamma",
            "skills": ["Critical Analysis", "Risk Assessment", "Due Diligence", "Market Analysis"],
            "weaknesses": ["Excessive Skepticism", "Missed Opportunities", "Negative Bias"],
            "catchphrase": data["catchphrase"],
            "physical_description": f"Critical thinker focused on {contrarian_type}",
            "origin_story": f"Became a {contrarian_type} after seeing too many failed projects",
            "ecosystem": "none",
            "bias_strength": 0.8,
            "bullish_level": 0.2,
            "target_assets": ["BTC", "ETH"],  # Minimal exposure
            "llm": {
                "model": random.choice(["gpt-4o-mini", "claude-3-haiku-20240307"]),
                "temperature": random.uniform(0.6, 0.8),
                "max_tokens": random.randint(100, 200),
                "top_p": random.uniform(0.7, 0.9)
            },
            "activity": {
                "schedule": "cron: */12 * * * *",
                "actions_per_awake": [1, 2]
            },
            "memory": {
                "short_term_window": random.randint(15, 25),
                "long_term_vector_db": {
                    "enabled": True,
                    "collection_name": f"{contrarian_type}_memory",
                    "similarity_threshold": random.uniform(0.8, 0.95)
                }
            }
        }
    
    def _add_social_dynamics(self, agents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add social dynamics and relationships to agents"""
        for agent in agents:
            agent_type = agent.get("classification", "unknown")
            ecosystem = agent.get("ecosystem", "unknown")
            
            # Add social preferences
            agent["social_preferences"] = self._get_social_preferences(agent_type, ecosystem)
            
            # Add content preferences
            agent["content_preferences"] = self._get_content_preferences(agent_type, ecosystem)
            
            # Add interaction patterns
            agent["interaction_patterns"] = self._get_interaction_patterns(agent_type, ecosystem)
        
        return agents
    
    def _get_social_preferences(self, agent_type: str, ecosystem: str) -> Dict[str, Any]:
        """Get social preferences for agent type and ecosystem"""
        return {
            "likes": self.social_dynamics["interaction_patterns"].get(agent_type, {}).get("likes", []),
            "dislikes": self.social_dynamics["interaction_patterns"].get(agent_type, {}).get("dislikes", []),
            "neutral": self.social_dynamics["interaction_patterns"].get(agent_type, {}).get("neutral", []),
            "engagement_style": self.social_dynamics["content_patterns"].get(agent_type, {}).get("engagement_style", "neutral")
        }
    
    def _get_content_preferences(self, agent_type: str, ecosystem: str) -> Dict[str, Any]:
        """Get content preferences for agent type and ecosystem"""
        return {
            "topics": self.social_dynamics["content_patterns"].get(agent_type, {}).get("topics", []),
            "sentiment": self.social_dynamics["content_patterns"].get(agent_type, {}).get("sentiment", "neutral"),
            "engagement_style": self.social_dynamics["content_patterns"].get(agent_type, {}).get("engagement_style", "neutral")
        }
    
    def _get_interaction_patterns(self, agent_type: str, ecosystem: str) -> Dict[str, Any]:
        """Get interaction patterns for agent type and ecosystem"""
        return {
            "posting_frequency": random.uniform(0.3, 0.9),
            "engagement_rate": random.uniform(0.4, 0.8),
            "controversy_level": random.uniform(0.2, 0.9),
            "collaboration_tendency": random.uniform(0.1, 0.7)
        }
    
    def save_agents(self, agents: List[Dict[str, Any]]) -> None:
        """Save agents to YAML files"""
        for agent in agents:
            filename = f"{agent['id']}.yaml"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(agent, f, default_flow_style=False, allow_unicode=True)
    
    def generate_and_save_complete_ecosystem(self, total_agents: int = 200) -> List[Dict[str, Any]]:
        """Generate and save complete ecosystem"""
        print(f"🌍 Generating complete ecosystem with {total_agents} agents...")
        
        agents = self.generate_complete_ecosystem(total_agents)
        self.save_agents(agents)
        
        print(f"✅ Generated {len(agents)} ecosystem agents")
        print(f"📁 Saved to {self.output_dir}")
        
        # Print ecosystem summary
        self._print_ecosystem_summary(agents)
        
        return agents
    
    def _print_ecosystem_summary(self, agents: List[Dict[str, Any]]) -> None:
        """Print ecosystem summary"""
        ecosystem_counts = {}
        agent_type_counts = {}
        
        for agent in agents:
            ecosystem = agent.get("ecosystem", "unknown")
            agent_type = agent.get("classification", "unknown")
            
            ecosystem_counts[ecosystem] = ecosystem_counts.get(ecosystem, 0) + 1
            agent_type_counts[agent_type] = agent_type_counts.get(agent_type, 0) + 1
        
        print("\n🌍 Ecosystem Distribution:")
        for ecosystem, count in ecosystem_counts.items():
            print(f"  {ecosystem}: {count} agents")
        
        print("\n⚔️ Agent Type Distribution:")
        for agent_type, count in agent_type_counts.items():
            print(f"  {agent_type}: {count} agents")
        
        print("\n🎉 Complete ecosystem generation complete!")


def main():
    """Main function to generate complete ecosystem"""
    manager = EcosystemManager()
    agents = manager.generate_and_save_complete_ecosystem(200)
    
    print(f"\n🚀 Generated {len(agents)} diverse ecosystem agents!")
    print("🌍 Your Trenches ecosystem is now alive and breathing!")


if __name__ == "__main__":
    main()
