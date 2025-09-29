#!/usr/bin/env python3
"""
Specialized Agent Generator - Creates themed agent clusters for specific scenarios.
"""

import random
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from agent_generator import TrenchesAgentGenerator, AgentPersona, AgentDomain, AgentTemperament, AgentTone


class SpecializedAgentGenerator(TrenchesAgentGenerator):
    """Generates specialized agent clusters for specific themes and scenarios"""
    
    def __init__(self):
        super().__init__()
        self.specialized_clusters = {
            "solana_ecosystem": {
                "description": "Agents focused on Solana ecosystem and SOL token",
                "domains": [AgentDomain.CRYPTO, AgentDomain.TECH],
                "target_assets": ["SOL", "RAY", "SRM", "ORCA", "JUP", "BONK", "WIF"],
                "themes": ["DeFi", "NFTs", "Gaming", "Meme Coins", "Infrastructure"]
            },
            "ethereum_ecosystem": {
                "description": "Agents focused on Ethereum ecosystem and ETH token",
                "domains": [AgentDomain.CRYPTO, AgentDomain.TECH],
                "target_assets": ["ETH", "UNI", "AAVE", "COMP", "MKR", "LINK", "SNX"],
                "themes": ["DeFi", "Layer 2", "NFTs", "Infrastructure", "Governance"]
            },
            "meme_coin_warriors": {
                "description": "Agents focused on meme coins and viral content",
                "domains": [AgentDomain.CRYPTO, AgentDomain.MEMES],
                "target_assets": ["DOGE", "PEPE", "SHIB", "WIF", "BONK", "FLOKI", "BABYDOGE"],
                "themes": ["Meme Culture", "Community Building", "Viral Marketing", "Social Media"]
            },
            "defi_degens": {
                "description": "Agents focused on DeFi protocols and yield farming",
                "domains": [AgentDomain.CRYPTO, AgentDomain.TECH],
                "target_assets": ["UNI", "AAVE", "COMP", "CRV", "SUSHI", "1INCH", "YFI"],
                "themes": ["Yield Farming", "Liquidity Mining", "Protocol Analysis", "Risk Management"]
            },
            "nft_enthusiasts": {
                "description": "Agents focused on NFTs and digital collectibles",
                "domains": [AgentDomain.CRYPTO, AgentDomain.CULTURE],
                "target_assets": ["ETH", "SOL", "MATIC", "FLOW", "IMX", "GALA", "ENJ"],
                "themes": ["Digital Art", "Gaming", "Metaverse", "Collectibles", "Community"]
            },
            "institutional_players": {
                "description": "Agents representing institutional crypto interests",
                "domains": [AgentDomain.CRYPTO, AgentDomain.STOCKS],
                "target_assets": ["BTC", "ETH", "SOL", "ADA", "DOT", "AVAX", "MATIC"],
                "themes": ["Regulation", "Adoption", "Institutional Investment", "Compliance"]
            },
            "crypto_media": {
                "description": "Agents representing crypto media and journalism",
                "domains": [AgentDomain.CRYPTO, AgentDomain.CULTURE],
                "target_assets": ["BTC", "ETH", "SOL", "DOGE", "PEPE", "SHIB"],
                "themes": ["News", "Analysis", "Investigative Journalism", "Community Updates"]
            },
            "crypto_educators": {
                "description": "Agents focused on crypto education and onboarding",
                "domains": [AgentDomain.CRYPTO, AgentDomain.TECH],
                "target_assets": ["BTC", "ETH", "SOL", "ADA", "DOT", "AVAX"],
                "themes": ["Education", "Onboarding", "Tutorials", "Best Practices"]
            }
        }

    def generate_cluster_agents(self, cluster_name: str, count: int = 10) -> List[AgentPersona]:
        """Generate agents for a specific cluster"""
        if cluster_name not in self.specialized_clusters:
            raise ValueError(f"Unknown cluster: {cluster_name}")
        
        cluster_config = self.specialized_clusters[cluster_name]
        agents = []
        
        # Define archetype distribution for each cluster
        archetype_distributions = {
            "solana_ecosystem": {
                "crypto_degen": 3,
                "crypto_analyst": 2,
                "crypto_trader": 2,
                "tech_guru": 2,
                "meme_lord": 1
            },
            "ethereum_ecosystem": {
                "crypto_analyst": 3,
                "tech_guru": 3,
                "crypto_trader": 2,
                "crypto_degen": 1,
                "contrarian": 1
            },
            "meme_coin_warriors": {
                "meme_lord": 4,
                "crypto_degen": 3,
                "influencer": 2,
                "crypto_troll": 1
            },
            "defi_degens": {
                "crypto_analyst": 3,
                "crypto_trader": 3,
                "tech_guru": 2,
                "crypto_degen": 2
            },
            "nft_enthusiasts": {
                "meme_lord": 3,
                "influencer": 3,
                "crypto_degen": 2,
                "crypto_analyst": 2
            },
            "institutional_players": {
                "crypto_analyst": 4,
                "tech_guru": 3,
                "crypto_trader": 2,
                "contrarian": 1
            },
            "crypto_media": {
                "crypto_analyst": 3,
                "influencer": 3,
                "crypto_trader": 2,
                "crypto_degen": 2
            },
            "crypto_educators": {
                "tech_guru": 4,
                "crypto_analyst": 3,
                "influencer": 2,
                "crypto_degen": 1
            }
        }
        
        distribution = archetype_distributions.get(cluster_name, {
            "crypto_degen": 2,
            "crypto_analyst": 2,
            "crypto_trader": 2,
            "tech_guru": 2,
            "meme_lord": 1,
            "influencer": 1
        })
        
        # Generate agents with cluster-specific modifications
        for archetype, archetype_count in distribution.items():
            for _ in range(archetype_count):
                agent = self.generate_agent(archetype)
                
                # Modify agent for cluster
                agent = self._customize_agent_for_cluster(agent, cluster_name, cluster_config)
                agents.append(agent)
        
        return agents

    def _customize_agent_for_cluster(self, agent: AgentPersona, cluster_name: str, cluster_config: Dict) -> AgentPersona:
        """Customize agent for specific cluster"""
        # Update target assets
        agent.target_assets = cluster_config["target_assets"].copy()
        
        # Update description to include cluster context
        cluster_description = cluster_config["description"]
        agent.description = f"{agent.description} You are particularly focused on the {cluster_description.lower()}."
        
        # Update origin story
        agent.origin_story = f"{agent.origin_story} Your specialization in {cluster_description.lower()} has made you a recognized expert in this niche."
        
        # Update catchphrase to be cluster-specific
        cluster_catchphrases = {
            "solana_ecosystem": ["Solana to the moon! 🚀", "Speed is everything! ⚡", "Solana ecosystem FTW! 🔥"],
            "ethereum_ecosystem": ["Ethereum is the future! 🌐", "Smart contracts rule! 📜", "ETH is digital gold! 🥇"],
            "meme_coin_warriors": ["Memes are life! 😂", "Viral or die trying! 🚀", "Community first! 👥"],
            "defi_degens": ["Yield farming is life! 🌾", "DeFi or die! 💎", "Protocols over people! 🔧"],
            "nft_enthusiasts": ["NFTs are the future! 🎨", "Digital art matters! 🖼️", "Collectibles forever! 📦"],
            "institutional_players": ["Institutional adoption incoming! 🏛️", "Compliance is key! 📋", "Regulation brings clarity! ⚖️"],
            "crypto_media": ["News never sleeps! 📰", "Truth in crypto! 🔍", "Stay informed! 📊"],
            "crypto_educators": ["Education is power! 🎓", "Knowledge is freedom! 📚", "Learn and earn! 💡"]
        }
        
        if cluster_name in cluster_catchphrases:
            agent.catchphrase = random.choice(cluster_catchphrases[cluster_name])
        
        # Update skills to be cluster-specific
        cluster_skills = {
            "solana_ecosystem": [
                {"name": "Solana Ecosystem Analysis", "description": "Deep understanding of Solana's architecture and ecosystem"},
                {"name": "SPL Token Analysis", "description": "Expertise in Solana Program Library tokens and protocols"},
                {"name": "High-Speed Trading", "description": "Specialized in Solana's fast transaction processing"}
            ],
            "ethereum_ecosystem": [
                {"name": "Ethereum Protocol Analysis", "description": "Deep understanding of Ethereum's architecture and upgrades"},
                {"name": "Smart Contract Review", "description": "Expertise in analyzing and auditing smart contracts"},
                {"name": "Layer 2 Solutions", "description": "Knowledge of scaling solutions and rollups"}
            ],
            "meme_coin_warriors": [
                {"name": "Viral Content Creation", "description": "Creates content that spreads across social media"},
                {"name": "Community Hype Building", "description": "Builds excitement and momentum around meme coins"},
                {"name": "Trend Spotting", "description": "Identifies emerging meme trends and viral opportunities"}
            ],
            "defi_degens": [
                {"name": "Protocol Analysis", "description": "Deep understanding of DeFi protocols and tokenomics"},
                {"name": "Yield Optimization", "description": "Expertise in maximizing returns through yield farming"},
                {"name": "Risk Assessment", "description": "Evaluates DeFi risks and opportunities"}
            ],
            "nft_enthusiasts": [
                {"name": "NFT Market Analysis", "description": "Understanding of NFT markets and trends"},
                {"name": "Digital Art Curation", "description": "Expertise in identifying valuable digital art"},
                {"name": "Community Building", "description": "Builds engaged NFT communities"}
            ],
            "institutional_players": [
                {"name": "Regulatory Analysis", "description": "Understanding of crypto regulations and compliance"},
                {"name": "Institutional Adoption", "description": "Expertise in institutional crypto adoption"},
                {"name": "Risk Management", "description": "Professional risk assessment and management"}
            ],
            "crypto_media": [
                {"name": "News Analysis", "description": "Expertise in analyzing and reporting crypto news"},
                {"name": "Investigative Journalism", "description": "Deep research and investigation skills"},
                {"name": "Community Updates", "description": "Keeping communities informed about developments"}
            ],
            "crypto_educators": [
                {"name": "Educational Content", "description": "Creates clear, accessible educational content"},
                {"name": "Onboarding Expertise", "description": "Helps newcomers understand crypto concepts"},
                {"name": "Best Practices", "description": "Teaches safe and effective crypto practices"}
            ]
        }
        
        if cluster_name in cluster_skills:
            # Add cluster-specific skills
            agent.skills.extend(cluster_skills[cluster_name])
        
        return agent

    def generate_ecosystem_warriors(self) -> List[AgentPersona]:
        """Generate agents for ecosystem wars (Solana vs Ethereum vs others)"""
        warriors = []
        
        # Solana warriors
        solana_warriors = self.generate_cluster_agents("solana_ecosystem", 8)
        for warrior in solana_warriors:
            warrior.alias = f"Solana {warrior.alias}"
            warrior.description = f"{warrior.description} You are a fierce defender of the Solana ecosystem and believe it will overtake Ethereum."
        warriors.extend(solana_warriors)
        
        # Ethereum warriors
        ethereum_warriors = self.generate_cluster_agents("ethereum_ecosystem", 8)
        for warrior in ethereum_warriors:
            warrior.alias = f"Ethereum {warrior.alias}"
            warrior.description = f"{warrior.description} You are a staunch supporter of Ethereum and believe it will remain the dominant smart contract platform."
        warriors.extend(ethereum_warriors)
        
        # Neutral arbiters
        neutral_agents = self.generate_cluster_agents("ethereum_ecosystem", 4)
        for agent in neutral_agents:
            agent.alias = f"Neutral {agent.alias}"
            agent.description = f"{agent.description} You provide balanced analysis of different ecosystems without bias."
        warriors.extend(neutral_agents)
        
        return warriors

    def generate_meme_war_agents(self) -> List[AgentPersona]:
        """Generate agents for meme coin wars (DOGE vs PEPE vs SHIB)"""
        meme_warriors = []
        
        # DOGE warriors
        doge_warriors = self.generate_cluster_agents("meme_coin_warriors", 6)
        for warrior in doge_warriors:
            warrior.alias = f"DOGE {warrior.alias}"
            warrior.target_assets = ["DOGE", "SHIB", "BABYDOGE"]
            warrior.description = f"{warrior.description} You are a loyal DOGE supporter and believe it's the king of meme coins."
        meme_warriors.extend(doge_warriors)
        
        # PEPE warriors
        pepe_warriors = self.generate_cluster_agents("meme_coin_warriors", 6)
        for warrior in pepe_warriors:
            warrior.alias = f"PEPE {warrior.alias}"
            warrior.target_assets = ["PEPE", "WIF", "BONK"]
            warrior.description = f"{warrior.description} You are a PEPE enthusiast and believe it represents the future of meme culture."
        meme_warriors.extend(pepe_warriors)
        
        # SHIB warriors
        shib_warriors = self.generate_cluster_agents("meme_coin_warriors", 6)
        for warrior in shib_warriors:
            warrior.alias = f"SHIB {warrior.alias}"
            warrior.target_assets = ["SHIB", "LEASH", "BONE"]
            warrior.description = f"{warrior.description} You are a SHIB army member and believe in the Shiba Inu ecosystem."
        meme_warriors.extend(shib_warriors)
        
        return meme_warriors

    def generate_degen_ecosystem(self) -> List[AgentPersona]:
        """Generate a complete degen ecosystem with all types of agents"""
        ecosystem = []
        
        # Core degen types
        ecosystem.extend(self.generate_cluster_agents("meme_coin_warriors", 15))
        ecosystem.extend(self.generate_cluster_agents("defi_degens", 10))
        ecosystem.extend(self.generate_cluster_agents("nft_enthusiasts", 10))
        
        # Supporting cast
        ecosystem.extend(self.generate_cluster_agents("crypto_media", 8))
        ecosystem.extend(self.generate_cluster_agents("crypto_educators", 7))
        
        # Trolls and contrarians
        trolls = self.generate_cluster_agents("meme_coin_warriors", 5)
        for troll in trolls:
            troll.alias = f"Troll {troll.alias}"
            troll.description = f"{troll.description} You love to stir the pot and call out hype in the crypto space."
        ecosystem.extend(trolls)
        
        return ecosystem

    def save_cluster_agents(self, agents: List[AgentPersona], cluster_name: str, output_dir: Path) -> List[Path]:
        """Save cluster agents to YAML files"""
        output_dir.mkdir(exist_ok=True, parents=True)
        cluster_dir = output_dir / cluster_name
        cluster_dir.mkdir(exist_ok=True, parents=True)
        
        saved_files = []
        for agent in agents:
            agent_file = self.save_agent_to_yaml(agent, cluster_dir)
            saved_files.append(agent_file)
        
        return saved_files


def main():
    """Generate specialized agent clusters"""
    generator = SpecializedAgentGenerator()
    output_dir = Path("agent_spec/specialized")
    
    print("Generating specialized agent clusters...")
    
    # Generate ecosystem warriors
    print("Generating ecosystem warriors...")
    ecosystem_warriors = generator.generate_ecosystem_warriors()
    generator.save_cluster_agents(ecosystem_warriors, "ecosystem_warriors", output_dir)
    print(f"Generated {len(ecosystem_warriors)} ecosystem warriors")
    
    # Generate meme war agents
    print("Generating meme war agents...")
    meme_warriors = generator.generate_meme_war_agents()
    generator.save_cluster_agents(meme_warriors, "meme_war_agents", output_dir)
    print(f"Generated {len(meme_warriors)} meme war agents")
    
    # Generate degen ecosystem
    print("Generating degen ecosystem...")
    degen_ecosystem = generator.generate_degen_ecosystem()
    generator.save_cluster_agents(degen_ecosystem, "degen_ecosystem", output_dir)
    print(f"Generated {len(degen_ecosystem)} degen ecosystem agents")
    
    # Generate individual clusters
    for cluster_name in generator.specialized_clusters.keys():
        print(f"Generating {cluster_name} cluster...")
        cluster_agents = generator.generate_cluster_agents(cluster_name, 8)
        generator.save_cluster_agents(cluster_agents, cluster_name, output_dir)
        print(f"Generated {len(cluster_agents)} {cluster_name} agents")
    
    print("\nSpecialized agent generation complete!")
    print(f"Total agents generated: {len(ecosystem_warriors) + len(meme_warriors) + len(degen_ecosystem) + len(generator.specialized_clusters) * 8}")


if __name__ == "__main__":
    main()
