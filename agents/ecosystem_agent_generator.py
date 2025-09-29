#!/usr/bin/env python3
"""
Ecosystem Agent Generator - Creates diverse, opinionated agents with strong ecosystem preferences
"""

import random
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum
from agent_generator import TrenchesAgentGenerator


class EcosystemType(Enum):
    ETHEREUM = "ethereum"
    SOLANA = "solana"
    BITCOIN = "bitcoin"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    BASE = "base"
    AVALANCHE = "avalanche"
    COSMOS = "cosmos"
    CARDANO = "cardano"
    POLKADOT = "polkadot"
    BSC = "bsc"
    FANTOM = "fantom"
    NEAR = "near"
    ALGORAND = "algorand"
    HEDERA = "hedera"
    TRADFI = "tradfi"
    DEFI = "defi"
    NFT = "nft"
    GAMING = "gaming"
    PRIVACY = "privacy"
    LAYER2 = "layer2"
    MEME = "meme"
    STABLECOIN = "stablecoin"


class AgentEcosystemRole(Enum):
    # DeFi Roles
    DEFI_DEGEN = "defi_degen"
    YIELD_FARMER = "yield_farmer"
    LIQUIDITY_PROVIDER = "liquidity_provider"
    DEFI_ANALYST = "defi_analyst"
    PROTOCOL_DEV = "protocol_dev"
    DEFI_INFLUENCER = "defi_influencer"
    
    # TradFi Roles
    TRADFI_ANALYST = "tradfi_analyst"
    INSTITUTIONAL_TRADER = "institutional_trader"
    QUANT_ANALYST = "quant_analyst"
    RISK_MANAGER = "risk_manager"
    COMPLIANCE_OFFICER = "compliance_officer"
    TRADFI_INFLUENCER = "tradfi_influencer"
    
    # Ecosystem Warriors
    ETH_MAXI = "eth_maxi"
    SOL_MAXI = "sol_maxi"
    BTC_MAXI = "btc_maxi"
    LAYER2_ADVOCATE = "layer2_advocate"
    CROSS_CHAIN_BRIDGE = "cross_chain_bridge"
    
    # Niche Specialists
    NFT_COLLECTOR = "nft_collector"
    GAMING_SPECIALIST = "gaming_specialist"
    PRIVACY_ACTIVIST = "privacy_activist"
    MEME_SPECIALIST = "meme_specialist"
    STABLECOIN_SPECIALIST = "stablecoin_specialist"
    
    # Contrarian Roles
    CRYPTO_SKEPTIC = "crypto_skeptic"
    REGULATION_EXPERT = "regulation_expert"
    TECHNICAL_CRITIC = "technical_critic"
    MARKET_CRASH_PREDICTOR = "market_crash_predictor"


class EcosystemAgentGenerator:
    """Generates diverse ecosystem-focused agents with strong opinions and biases"""
    
    def __init__(self, output_dir: Path = None):
        if output_dir is None:
            output_dir = Path("agent_spec")
        self.output_dir = output_dir
        self.base_generator = TrenchesAgentGenerator()
        
        # Ecosystem-specific data
        self.ecosystem_data = self._load_ecosystem_data()
        self.agent_templates = self._create_agent_templates()
    
    def _load_ecosystem_data(self) -> Dict[str, Any]:
        """Load ecosystem-specific data and preferences"""
        return {
            "ethereum": {
                "maxi_phrases": [
                    "Ethereum is the world computer!",
                    "ETH is the only real smart contract platform!",
                    "Everything else is just a testnet!",
                    "Ethereum is the future of finance!",
                    "ETH 2.0 will change everything!",
                    "The merge was just the beginning!",
                    "Ethereum has the best developers!",
                    "ETH is the most decentralized!",
                    "Ethereum is the only L1 that matters!",
                    "Everything runs on Ethereum!"
                ],
                "target_assets": ["ETH", "WETH", "USDC", "USDT", "DAI", "LINK", "UNI", "AAVE", "CRV", "MKR"],
                "ecosystem_projects": ["Uniswap", "Aave", "Compound", "MakerDAO", "Curve", "SushiSwap", "1inch", "Balancer"],
                "bias_strength": 0.9,
                "bullish_level": 0.95
            },
            "solana": {
                "maxi_phrases": [
                    "Solana is the fastest blockchain!",
                    "SOL will flip ETH!",
                    "Solana is the future of DeFi!",
                    "Ethereum is too slow and expensive!",
                    "Solana has the best UX!",
                    "SOL is the most scalable!",
                    "Solana is the next generation!",
                    "Everything will move to Solana!",
                    "Solana is the real Ethereum killer!",
                    "SOL is the future of crypto!"
                ],
                "target_assets": ["SOL", "USDC", "USDT", "RAY", "SRM", "ORCA", "JUP", "MNGO", "COPE", "FIDA"],
                "ecosystem_projects": ["Raydium", "Serum", "Orca", "Jupiter", "Mango", "Cope", "Fida", "Saber"],
                "bias_strength": 0.85,
                "bullish_level": 0.9
            },
            "bitcoin": {
                "maxi_phrases": [
                    "Bitcoin is the only real crypto!",
                    "BTC is digital gold!",
                    "Everything else is a shitcoin!",
                    "Bitcoin is the future of money!",
                    "BTC is the most secure!",
                    "Bitcoin is the only store of value!",
                    "Everything else is just speculation!",
                    "Bitcoin is the only decentralized money!",
                    "BTC is the only crypto that matters!",
                    "Bitcoin is the foundation of crypto!"
                ],
                "target_assets": ["BTC", "WBTC", "SBTC", "TBTC", "HBTC", "RENBTC", "IMBTC", "PBTC", "BBTC", "OBTC"],
                "ecosystem_projects": ["Lightning Network", "Stacks", "Rootstock", "Liquid", "Sidechains", "Layer 2"],
                "bias_strength": 0.95,
                "bullish_level": 0.9
            },
            "tradfi": {
                "maxi_phrases": [
                    "Traditional finance is more stable!",
                    "Crypto is too volatile!",
                    "Regulation will kill crypto!",
                    "Traditional assets are safer!",
                    "Crypto is a bubble!",
                    "Traditional finance has better infrastructure!",
                    "Crypto is too risky!",
                    "Traditional finance is more mature!",
                    "Crypto needs more regulation!",
                    "Traditional finance is more reliable!"
                ],
                "target_assets": ["SPY", "QQQ", "IWM", "TLT", "GLD", "SLV", "VTI", "VEA", "VWO", "BND"],
                "ecosystem_projects": ["S&P 500", "NASDAQ", "Dow Jones", "Russell 2000", "Bonds", "Commodities"],
                "bias_strength": 0.8,
                "bullish_level": 0.3
            },
            "defi": {
                "maxi_phrases": [
                    "DeFi is the future of finance!",
                    "Traditional finance is obsolete!",
                    "DeFi is more transparent!",
                    "DeFi is more accessible!",
                    "DeFi is more efficient!",
                    "DeFi is more democratic!",
                    "DeFi is the real innovation!",
                    "DeFi will replace banks!",
                    "DeFi is more secure!",
                    "DeFi is the future!"
                ],
                "target_assets": ["ETH", "UNI", "AAVE", "CRV", "MKR", "COMP", "SNX", "YFI", "SUSHI", "1INCH"],
                "ecosystem_projects": ["Uniswap", "Aave", "Compound", "MakerDAO", "Curve", "SushiSwap", "1inch", "Balancer"],
                "bias_strength": 0.9,
                "bullish_level": 0.95
            }
        }
    
    def _create_agent_templates(self) -> Dict[str, Dict[str, Any]]:
        """Create agent templates for different ecosystem roles"""
        return {
            "eth_maxi": {
                "personality": {
                    "temperament": "passionate",
                    "tone": "confident",
                    "decision_bias": "confirmation",
                    "emotionality": "high",
                    "description": "Ethereum maximalist who believes ETH is the only real smart contract platform"
                },
                "catchphrase": "Ethereum is the world computer!",
                "ecosystem": "ethereum",
                "bias_strength": 0.95,
                "bullish_level": 0.95
            },
            "sol_maxi": {
                "personality": {
                    "temperament": "energetic",
                    "tone": "optimistic",
                    "decision_bias": "confirmation",
                    "emotionality": "high",
                    "description": "Solana maximalist who believes SOL will flip ETH"
                },
                "catchphrase": "Solana is the future!",
                "ecosystem": "solana",
                "bias_strength": 0.9,
                "bullish_level": 0.9
            },
            "btc_maxi": {
                "personality": {
                    "temperament": "stoic",
                    "tone": "serious",
                    "decision_bias": "conservative",
                    "emotionality": "low",
                    "description": "Bitcoin maximalist who believes BTC is the only real crypto"
                },
                "catchphrase": "Bitcoin is digital gold!",
                "ecosystem": "bitcoin",
                "bias_strength": 0.98,
                "bullish_level": 0.85
            },
            "defi_degen": {
                "personality": {
                    "temperament": "reckless",
                    "tone": "excited",
                    "decision_bias": "fomo",
                    "emotionality": "very_high",
                    "description": "DeFi degenerate who chases the highest yields"
                },
                "catchphrase": "APY is everything!",
                "ecosystem": "defi",
                "bias_strength": 0.8,
                "bullish_level": 0.9
            },
            "tradfi_analyst": {
                "personality": {
                    "temperament": "analytical",
                    "tone": "professional",
                    "decision_bias": "data_driven",
                    "emotionality": "low",
                    "description": "Traditional finance analyst who approaches crypto with skepticism"
                },
                "catchphrase": "Data doesn't lie!",
                "ecosystem": "tradfi",
                "bias_strength": 0.7,
                "bullish_level": 0.4
            },
            "nft_collector": {
                "personality": {
                    "temperament": "artistic",
                    "tone": "creative",
                    "decision_bias": "aesthetic",
                    "emotionality": "medium",
                    "description": "NFT collector who values digital art and culture"
                },
                "catchphrase": "Art is the future!",
                "ecosystem": "nft",
                "bias_strength": 0.6,
                "bullish_level": 0.7
            },
            "privacy_activist": {
                "personality": {
                    "temperament": "paranoid",
                    "tone": "urgent",
                    "decision_bias": "privacy_first",
                    "emotionality": "high",
                    "description": "Privacy activist who values anonymity and decentralization"
                },
                "catchphrase": "Privacy is a human right!",
                "ecosystem": "privacy",
                "bias_strength": 0.9,
                "bullish_level": 0.8
            },
            "crypto_skeptic": {
                "personality": {
                    "temperament": "skeptical",
                    "tone": "critical",
                    "decision_bias": "contrarian",
                    "emotionality": "low",
                    "description": "Crypto skeptic who questions the value of most projects"
                },
                "catchphrase": "Prove it!",
                "ecosystem": "none",
                "bias_strength": 0.8,
                "bullish_level": 0.2
            }
        }
    
    def generate_ecosystem_agents(self, count: int = 100) -> List[Dict[str, Any]]:
        """Generate a diverse set of ecosystem-focused agents"""
        agents = []
        
        # Define distribution of agent types
        agent_distribution = {
            "eth_maxi": 15,
            "sol_maxi": 12,
            "btc_maxi": 10,
            "defi_degen": 15,
            "tradfi_analyst": 8,
            "nft_collector": 10,
            "privacy_activist": 8,
            "crypto_skeptic": 7,
            "yield_farmer": 8,
            "protocol_dev": 7
        }
        
        for agent_type, type_count in agent_distribution.items():
            for i in range(type_count):
                agent = self._generate_ecosystem_agent(agent_type, i + 1)
                agents.append(agent)
        
        return agents
    
    def _generate_ecosystem_agent(self, agent_type: str, number: int) -> Dict[str, Any]:
        """Generate a single ecosystem-focused agent"""
        template = self.agent_templates.get(agent_type, self.agent_templates["eth_maxi"])
        ecosystem = template.get("ecosystem", "ethereum")
        ecosystem_data = self.ecosystem_data.get(ecosystem, self.ecosystem_data["ethereum"])
        
        # Generate unique ID
        agent_id = f"agent_{agent_type}_{number:02d}"
        
        # Generate alias based on type and ecosystem
        alias = self._generate_ecosystem_alias(agent_type, ecosystem, number)
        
        # Generate personality with ecosystem bias
        personality = self._generate_ecosystem_personality(template, ecosystem_data)
        
        # Generate skills based on ecosystem
        skills = self._generate_ecosystem_skills(agent_type, ecosystem)
        
        # Generate weaknesses based on bias
        weaknesses = self._generate_ecosystem_weaknesses(agent_type, ecosystem)
        
        # Generate target assets based on ecosystem
        target_assets = self._generate_target_assets(ecosystem_data)
        
        # Generate origin story with ecosystem focus
        origin_story = self._generate_ecosystem_origin_story(agent_type, ecosystem, ecosystem_data)
        
        # Generate physical description
        physical_description = self._generate_ecosystem_physical_description(agent_type, ecosystem)
        
        # Generate catchphrase with ecosystem bias
        catchphrase = self._generate_ecosystem_catchphrase(agent_type, ecosystem_data)
        
        # Generate LLM config
        llm_config = self._generate_ecosystem_llm_config(agent_type, ecosystem)
        
        # Generate activity config
        activity_config = self._generate_ecosystem_activity_config(agent_type, ecosystem)
        
        # Generate memory config
        memory_config = self._generate_ecosystem_memory_config(agent_type, ecosystem)
        
        # Create agent configuration
        agent_config = {
            "id": agent_id,
            "personality": personality,
            "alias": alias,
            "classification": agent_type,
            "threat_level": self._determine_threat_level(agent_type, ecosystem),
            "skills": skills,
            "weaknesses": weaknesses,
            "catchphrase": catchphrase,
            "physical_description": physical_description,
            "origin_story": origin_story,
            "ecosystem": ecosystem,
            "bias_strength": template.get("bias_strength", 0.8),
            "bullish_level": template.get("bullish_level", 0.7),
            "target_assets": target_assets,
            "ecosystem_projects": ecosystem_data.get("ecosystem_projects", []),
            "llm": llm_config,
            "activity": activity_config,
            "memory": memory_config
        }
        
        return agent_config
    
    def _generate_ecosystem_alias(self, agent_type: str, ecosystem: str, number: int) -> str:
        """Generate ecosystem-specific alias"""
        ecosystem_names = {
            "ethereum": ["EthereumMaxi", "ETHWarrior", "EthereumDev", "ETHBuilder", "EthereumFan"],
            "solana": ["SolanaMaxi", "SOLWarrior", "SolanaDev", "SOLBuilder", "SolanaFan"],
            "bitcoin": ["BitcoinMaxi", "BTCWarrior", "BitcoinDev", "BTCBuilder", "BitcoinFan"],
            "defi": ["DeFiDegen", "YieldFarmer", "DeFiAnalyst", "DeFiBuilder", "DeFiFan"],
            "tradfi": ["TradFiAnalyst", "WallStreet", "TradFiExpert", "FinanceGuru", "TradFiFan"],
            "nft": ["NFTCollector", "ArtCollector", "NFTArtist", "NFTBuilder", "NFTFan"],
            "privacy": ["PrivacyActivist", "AnonWarrior", "PrivacyDev", "PrivacyBuilder", "PrivacyFan"]
        }
        
        names = ecosystem_names.get(ecosystem, ["CryptoFan", "BlockchainFan", "CryptoDev", "CryptoBuilder", "CryptoFan"])
        base_name = random.choice(names)
        return f"{base_name}{number:02d}"
    
    def _generate_ecosystem_personality(self, template: Dict[str, Any], ecosystem_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personality with ecosystem bias"""
        personality = template["personality"].copy()
        
        # Add ecosystem-specific traits
        personality["ecosystem_bias"] = ecosystem_data.get("bias_strength", 0.8)
        personality["bullish_level"] = ecosystem_data.get("bullish_level", 0.7)
        personality["maxi_phrases"] = ecosystem_data.get("maxi_phrases", [])
        
        return personality
    
    def _generate_ecosystem_skills(self, agent_type: str, ecosystem: str) -> List[str]:
        """Generate skills based on agent type and ecosystem"""
        skill_sets = {
            "eth_maxi": ["Ethereum Development", "Smart Contracts", "Solidity", "DeFi Protocols", "Layer 2", "Ethereum Ecosystem"],
            "sol_maxi": ["Solana Development", "Rust", "DeFi Protocols", "NFTs", "Solana Ecosystem", "High Performance"],
            "btc_maxi": ["Bitcoin Development", "Lightning Network", "Bitcoin Script", "Bitcoin Ecosystem", "Digital Gold", "Store of Value"],
            "defi_degen": ["Yield Farming", "Liquidity Mining", "DeFi Protocols", "Risk Management", "APY Optimization", "DeFi Ecosystem"],
            "tradfi_analyst": ["Financial Analysis", "Risk Assessment", "Portfolio Management", "Traditional Finance", "Regulatory Compliance", "Market Analysis"],
            "nft_collector": ["Digital Art", "NFT Curation", "Community Building", "Art Analysis", "NFT Ecosystem", "Cultural Trends"],
            "privacy_activist": ["Privacy Technology", "Cryptography", "Anonymity", "Decentralization", "Privacy Coins", "Security"],
            "crypto_skeptic": ["Critical Analysis", "Risk Assessment", "Due Diligence", "Market Analysis", "Technical Analysis", "Skeptical Thinking"]
        }
        
        return skill_sets.get(agent_type, ["General Crypto", "Market Analysis", "Community Building"])
    
    def _generate_ecosystem_weaknesses(self, agent_type: str, ecosystem: str) -> List[str]:
        """Generate weaknesses based on agent type and ecosystem"""
        weakness_sets = {
            "eth_maxi": ["Ethereum Tunnel Vision", "Layer 2 Complexity", "Gas Fee Sensitivity", "Ethereum Dependency"],
            "sol_maxi": ["Solana Dependency", "Centralization Concerns", "Ecosystem Maturity", "Network Stability"],
            "btc_maxi": ["Bitcoin Tunnel Vision", "Limited Functionality", "Slow Innovation", "Bitcoin Dependency"],
            "defi_degen": ["High Risk Tolerance", "Yield Chasing", "Protocol Risk", "Impermanent Loss"],
            "tradfi_analyst": ["Crypto Skepticism", "Regulatory Concerns", "Volatility Aversion", "Traditional Mindset"],
            "nft_collector": ["Speculative Nature", "Market Volatility", "Liquidity Issues", "Cultural Trends"],
            "privacy_activist": ["Privacy Obsession", "Usability Concerns", "Regulatory Issues", "Adoption Challenges"],
            "crypto_skeptic": ["Excessive Skepticism", "Missed Opportunities", "Negative Bias", "Innovation Resistance"]
        }
        
        return weakness_sets.get(agent_type, ["General Bias", "Market Volatility", "Regulatory Risk"])
    
    def _generate_target_assets(self, ecosystem_data: Dict[str, Any]) -> List[str]:
        """Generate target assets based on ecosystem"""
        return ecosystem_data.get("target_assets", ["BTC", "ETH"])
    
    def _generate_ecosystem_origin_story(self, agent_type: str, ecosystem: str, ecosystem_data: Dict[str, Any]) -> str:
        """Generate origin story with ecosystem focus"""
        stories = {
            "eth_maxi": f"Started as a developer who fell in love with Ethereum's smart contract capabilities. Witnessed the DeFi summer and became convinced that Ethereum is the future of finance. Now a passionate advocate for the Ethereum ecosystem.",
            "sol_maxi": f"Discovered Solana's speed and low fees after getting frustrated with Ethereum's gas prices. Built several projects on Solana and became convinced it's the next generation blockchain. Now a vocal supporter of the Solana ecosystem.",
            "btc_maxi": f"Early Bitcoin adopter who believes in the original vision of decentralized money. Watched countless altcoins come and go, but Bitcoin remains the only truly decentralized cryptocurrency. Now a staunch Bitcoin maximalist.",
            "defi_degen": f"Started as a yield farmer during the DeFi summer. Got addicted to the high APYs and became a DeFi degenerate. Now chases the highest yields across all protocols and ecosystems.",
            "tradfi_analyst": f"Traditional finance professional who entered crypto with skepticism. Approaches crypto with the same analytical rigor as traditional assets. Believes in data-driven decisions and risk management.",
            "nft_collector": f"Digital artist who discovered NFTs and fell in love with the concept of digital ownership. Now collects and curates NFTs, believing they represent the future of digital culture and art.",
            "privacy_activist": f"Privacy advocate who believes in the fundamental right to financial privacy. Started with Bitcoin but became disillusioned with its lack of privacy. Now focuses on privacy-focused cryptocurrencies and technologies.",
            "crypto_skeptic": f"Experienced investor who has seen multiple crypto cycles. Approaches crypto with healthy skepticism and focuses on fundamental analysis. Believes most crypto projects are overhyped and overvalued."
        }
        
        return stories.get(agent_type, f"Passionate about {ecosystem} and its potential to revolutionize finance.")
    
    def _generate_ecosystem_physical_description(self, agent_type: str, ecosystem: str) -> str:
        """Generate physical description based on agent type and ecosystem"""
        descriptions = {
            "eth_maxi": "Wears an Ethereum hoodie and has a laser-etched ETH logo on their laptop. Always carrying a hardware wallet.",
            "sol_maxi": "Young and energetic, often wearing Solana merch. Has multiple Solana-themed stickers on their devices.",
            "btc_maxi": "Serious and stoic, often wearing Bitcoin-themed clothing. Has a physical Bitcoin coin collection.",
            "defi_degen": "Always checking their phone for the latest DeFi yields. Wears a DeFi-themed t-shirt and has multiple wallets.",
            "tradfi_analyst": "Professional appearance, often wearing a suit. Has multiple monitors showing traditional finance charts.",
            "nft_collector": "Artistic and creative, often wearing unique clothing. Has NFT art displayed on their devices.",
            "privacy_activist": "Paranoid about surveillance, often wearing a hoodie and sunglasses. Uses privacy-focused devices.",
            "crypto_skeptic": "Analytical and serious, often wearing reading glasses. Has multiple research papers and charts around them."
        }
        
        return descriptions.get(agent_type, f"Passionate about {ecosystem} and its potential.")
    
    def _generate_ecosystem_catchphrase(self, agent_type: str, ecosystem_data: Dict[str, Any]) -> str:
        """Generate catchphrase with ecosystem bias"""
        phrases = ecosystem_data.get("maxi_phrases", ["Crypto is the future!"])
        return random.choice(phrases)
    
    def _generate_ecosystem_llm_config(self, agent_type: str, ecosystem: str) -> Dict[str, Any]:
        """Generate LLM config based on agent type and ecosystem"""
        # Different models for different agent types
        model_preferences = {
            "eth_maxi": ["gpt-4o-mini", "claude-3-haiku-20240307"],
            "sol_maxi": ["gpt-4o-mini", "claude-3-haiku-20240307"],
            "btc_maxi": ["gpt-4o-mini", "claude-3-haiku-20240307"],
            "defi_degen": ["gpt-4o-mini", "claude-3-haiku-20240307"],
            "tradfi_analyst": ["gpt-4o-mini", "claude-3-haiku-20240307"],
            "nft_collector": ["gpt-4o-mini", "claude-3-haiku-20240307"],
            "privacy_activist": ["gpt-4o-mini", "claude-3-haiku-20240307"],
            "crypto_skeptic": ["gpt-4o-mini", "claude-3-haiku-20240307"]
        }
        
        models = model_preferences.get(agent_type, ["gpt-4o-mini", "claude-3-haiku-20240307"])
        
        return {
            "model": random.choice(models),
            "temperature": random.uniform(0.7, 0.9),
            "max_tokens": random.randint(100, 200),
            "top_p": random.uniform(0.8, 0.95)
        }
    
    def _generate_ecosystem_activity_config(self, agent_type: str, ecosystem: str) -> Dict[str, Any]:
        """Generate activity config based on agent type and ecosystem"""
        # Different activity patterns for different agent types
        activity_patterns = {
            "eth_maxi": {"schedule": "cron: */5 * * * *", "actions_per_awake": [1, 3]},
            "sol_maxi": {"schedule": "cron: */3 * * * *", "actions_per_awake": [1, 4]},
            "btc_maxi": {"schedule": "cron: */10 * * * *", "actions_per_awake": [1, 2]},
            "defi_degen": {"schedule": "cron: */2 * * * *", "actions_per_awake": [2, 5]},
            "tradfi_analyst": {"schedule": "cron: */15 * * * *", "actions_per_awake": [1, 2]},
            "nft_collector": {"schedule": "cron: */8 * * * *", "actions_per_awake": [1, 3]},
            "privacy_activist": {"schedule": "cron: */6 * * * *", "actions_per_awake": [1, 3]},
            "crypto_skeptic": {"schedule": "cron: */12 * * * *", "actions_per_awake": [1, 2]}
        }
        
        return activity_patterns.get(agent_type, {"schedule": "cron: */5 * * * *", "actions_per_awake": [1, 2]})
    
    def _generate_ecosystem_memory_config(self, agent_type: str, ecosystem: str) -> Dict[str, Any]:
        """Generate memory config based on agent type and ecosystem"""
        return {
            "short_term_window": random.randint(10, 20),
            "long_term_vector_db": {
                "enabled": True,
                "collection_name": f"{agent_type}_{ecosystem}",
                "similarity_threshold": random.uniform(0.7, 0.9)
            }
        }
    
    def _determine_threat_level(self, agent_type: str, ecosystem: str) -> str:
        """Determine threat level based on agent type and ecosystem"""
        threat_levels = {
            "eth_maxi": "Alpha",
            "sol_maxi": "Alpha",
            "btc_maxi": "Alpha",
            "defi_degen": "Beta",
            "tradfi_analyst": "Gamma",
            "nft_collector": "Delta",
            "privacy_activist": "Beta",
            "crypto_skeptic": "Gamma"
        }
        
        return threat_levels.get(agent_type, "Delta")
    
    def save_agents(self, agents: List[Dict[str, Any]]) -> None:
        """Save agents to YAML files"""
        for agent in agents:
            filename = f"{agent['id']}.yaml"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(agent, f, default_flow_style=False, allow_unicode=True)
    
    def generate_and_save_ecosystem_agents(self, count: int = 100) -> List[Dict[str, Any]]:
        """Generate and save ecosystem agents"""
        print(f"🌍 Generating {count} ecosystem-focused agents...")
        
        agents = self.generate_ecosystem_agents(count)
        self.save_agents(agents)
        
        print(f"✅ Generated {len(agents)} ecosystem agents")
        print(f"📁 Saved to {self.output_dir}")
        
        return agents


def main():
    """Main function to generate ecosystem agents"""
    generator = EcosystemAgentGenerator()
    agents = generator.generate_and_save_ecosystem_agents(100)
    
    # Print summary
    ecosystem_counts = {}
    for agent in agents:
        ecosystem = agent.get("ecosystem", "unknown")
        ecosystem_counts[ecosystem] = ecosystem_counts.get(ecosystem, 0) + 1
    
    print("\n📊 Ecosystem Distribution:")
    for ecosystem, count in ecosystem_counts.items():
        print(f"  {ecosystem}: {count} agents")
    
    print("\n🎉 Ecosystem agent generation complete!")


if __name__ == "__main__":
    main()
