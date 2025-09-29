#!/usr/bin/env python3
"""
Ecosystem Warriors Generator - Creates passionate, opinionated agents with strong ecosystem biases
"""

import random
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from ecosystem_agent_generator import EcosystemAgentGenerator, EcosystemType, AgentEcosystemRole


class EcosystemWarriorsGenerator:
    """Generates passionate ecosystem warriors with strong opinions and biases"""
    
    def __init__(self, output_dir: Path = None):
        if output_dir is None:
            output_dir = Path("agent_spec")
        self.output_dir = output_dir
        self.base_generator = EcosystemAgentGenerator(output_dir)
        
        # Warrior-specific data
        self.warrior_data = self._load_warrior_data()
    
    def _load_warrior_data(self) -> Dict[str, Any]:
        """Load warrior-specific data and battle phrases"""
        return {
            "ethereum_warriors": {
                "battle_phrases": [
                    "Ethereum is the only real smart contract platform!",
                    "Everything else is just a testnet!",
                    "ETH 2.0 will change everything!",
                    "Ethereum has the best developers!",
                    "The merge was just the beginning!",
                    "Ethereum is the future of finance!",
                    "ETH is the most decentralized!",
                    "Everything runs on Ethereum!",
                    "Ethereum is the world computer!",
                    "ETH is the only L1 that matters!"
                ],
                "enemy_ecosystems": ["solana", "bsc", "polygon", "avalanche"],
                "allied_ecosystems": ["arbitrum", "optimism", "base", "polygon"],
                "target_assets": ["ETH", "WETH", "USDC", "USDT", "DAI", "LINK", "UNI", "AAVE", "CRV", "MKR"],
                "ecosystem_projects": ["Uniswap", "Aave", "Compound", "MakerDAO", "Curve", "SushiSwap", "1inch", "Balancer"],
                "bias_strength": 0.95,
                "bullish_level": 0.98
            },
            "solana_warriors": {
                "battle_phrases": [
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
                "enemy_ecosystems": ["ethereum", "bitcoin", "bsc", "polygon"],
                "allied_ecosystems": ["raydium", "serum", "orca"],
                "target_assets": ["SOL", "USDC", "USDT", "RAY", "SRM", "ORCA", "JUP", "MNGO", "COPE", "FIDA"],
                "ecosystem_projects": ["Raydium", "Serum", "Orca", "Jupiter", "Mango", "Cope", "Fida", "Saber"],
                "bias_strength": 0.9,
                "bullish_level": 0.95
            },
            "bitcoin_warriors": {
                "battle_phrases": [
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
                "enemy_ecosystems": ["ethereum", "solana", "bsc", "polygon", "avalanche"],
                "allied_ecosystems": ["lightning", "stacks", "rootstock"],
                "target_assets": ["BTC", "WBTC", "SBTC", "TBTC", "HBTC", "RENBTC", "IMBTC", "PBTC", "BBTC", "OBTC"],
                "ecosystem_projects": ["Lightning Network", "Stacks", "Rootstock", "Liquid", "Sidechains", "Layer 2"],
                "bias_strength": 0.98,
                "bullish_level": 0.9
            },
            "defi_warriors": {
                "battle_phrases": [
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
                "enemy_ecosystems": ["tradfi", "traditional_finance"],
                "allied_ecosystems": ["ethereum", "arbitrum", "optimism", "polygon"],
                "target_assets": ["ETH", "UNI", "AAVE", "CRV", "MKR", "COMP", "SNX", "YFI", "SUSHI", "1INCH"],
                "ecosystem_projects": ["Uniswap", "Aave", "Compound", "MakerDAO", "Curve", "SushiSwap", "1inch", "Balancer"],
                "bias_strength": 0.9,
                "bullish_level": 0.95
            },
            "tradfi_warriors": {
                "battle_phrases": [
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
                "enemy_ecosystems": ["ethereum", "solana", "bitcoin", "defi"],
                "allied_ecosystems": ["traditional_finance", "regulated_finance"],
                "target_assets": ["SPY", "QQQ", "IWM", "TLT", "GLD", "SLV", "VTI", "VEA", "VWO", "BND"],
                "ecosystem_projects": ["S&P 500", "NASDAQ", "Dow Jones", "Russell 2000", "Bonds", "Commodities"],
                "bias_strength": 0.8,
                "bullish_level": 0.3
            }
        }
    
    def generate_ecosystem_warriors(self, count_per_ecosystem: int = 20) -> List[Dict[str, Any]]:
        """Generate passionate ecosystem warriors"""
        warriors = []
        
        # Generate warriors for each ecosystem
        for ecosystem, data in self.warrior_data.items():
            for i in range(count_per_ecosystem):
                warrior = self._generate_ecosystem_warrior(ecosystem, i + 1, data)
                warriors.append(warrior)
        
        return warriors
    
    def _generate_ecosystem_warrior(self, ecosystem: str, number: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a single ecosystem warrior"""
        # Generate unique ID
        agent_id = f"agent_{ecosystem}_warrior_{number:02d}"
        
        # Generate alias based on ecosystem
        alias = self._generate_warrior_alias(ecosystem, number)
        
        # Generate personality with warrior traits
        personality = self._generate_warrior_personality(ecosystem, data)
        
        # Generate skills based on ecosystem
        skills = self._generate_warrior_skills(ecosystem, data)
        
        # Generate weaknesses based on bias
        weaknesses = self._generate_warrior_weaknesses(ecosystem, data)
        
        # Generate target assets based on ecosystem
        target_assets = data.get("target_assets", ["BTC", "ETH"])
        
        # Generate origin story with warrior focus
        origin_story = self._generate_warrior_origin_story(ecosystem, data)
        
        # Generate physical description
        physical_description = self._generate_warrior_physical_description(ecosystem, data)
        
        # Generate catchphrase with warrior bias
        catchphrase = self._generate_warrior_catchphrase(ecosystem, data)
        
        # Generate LLM config
        llm_config = self._generate_warrior_llm_config(ecosystem, data)
        
        # Generate activity config
        activity_config = self._generate_warrior_activity_config(ecosystem, data)
        
        # Generate memory config
        memory_config = self._generate_warrior_memory_config(ecosystem, data)
        
        # Create warrior configuration
        warrior_config = {
            "id": agent_id,
            "personality": personality,
            "alias": alias,
            "classification": f"{ecosystem}_warrior",
            "threat_level": "Alpha",
            "skills": skills,
            "weaknesses": weaknesses,
            "catchphrase": catchphrase,
            "physical_description": physical_description,
            "origin_story": origin_story,
            "ecosystem": ecosystem.replace("_warriors", ""),
            "bias_strength": data.get("bias_strength", 0.9),
            "bullish_level": data.get("bullish_level", 0.9),
            "target_assets": target_assets,
            "ecosystem_projects": data.get("ecosystem_projects", []),
            "enemy_ecosystems": data.get("enemy_ecosystems", []),
            "allied_ecosystems": data.get("allied_ecosystems", []),
            "battle_phrases": data.get("battle_phrases", []),
            "llm": llm_config,
            "activity": activity_config,
            "memory": memory_config
        }
        
        return warrior_config
    
    def _generate_warrior_alias(self, ecosystem: str, number: int) -> str:
        """Generate warrior-specific alias"""
        warrior_names = {
            "ethereum_warriors": ["EthereumMaxi", "ETHWarrior", "EthereumDev", "ETHBuilder", "EthereumFan", "ETHGuardian"],
            "solana_warriors": ["SolanaMaxi", "SOLWarrior", "SolanaDev", "SOLBuilder", "SolanaFan", "SOLGuardian"],
            "bitcoin_warriors": ["BitcoinMaxi", "BTCWarrior", "BitcoinDev", "BTCBuilder", "BitcoinFan", "BTCGuardian"],
            "defi_warriors": ["DeFiDegen", "YieldFarmer", "DeFiAnalyst", "DeFiBuilder", "DeFiFan", "DeFiGuardian"],
            "tradfi_warriors": ["TradFiAnalyst", "WallStreet", "TradFiExpert", "FinanceGuru", "TradFiFan", "TradFiGuardian"]
        }
        
        names = warrior_names.get(ecosystem, ["CryptoWarrior", "BlockchainWarrior", "CryptoDev", "CryptoBuilder", "CryptoFan", "CryptoGuardian"])
        base_name = random.choice(names)
        return f"{base_name}{number:02d}"
    
    def _generate_warrior_personality(self, ecosystem: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personality with warrior traits"""
        personality_traits = {
            "ethereum_warriors": {
                "temperament": "passionate",
                "tone": "confident",
                "decision_bias": "confirmation",
                "emotionality": "very_high",
                "description": "Ethereum maximalist warrior who believes ETH is the only real smart contract platform"
            },
            "solana_warriors": {
                "temperament": "energetic",
                "tone": "optimistic",
                "decision_bias": "confirmation",
                "emotionality": "very_high",
                "description": "Solana maximalist warrior who believes SOL will flip ETH"
            },
            "bitcoin_warriors": {
                "temperament": "stoic",
                "tone": "serious",
                "decision_bias": "conservative",
                "emotionality": "high",
                "description": "Bitcoin maximalist warrior who believes BTC is the only real crypto"
            },
            "defi_warriors": {
                "temperament": "reckless",
                "tone": "excited",
                "decision_bias": "fomo",
                "emotionality": "very_high",
                "description": "DeFi warrior who believes DeFi will replace traditional finance"
            },
            "tradfi_warriors": {
                "temperament": "analytical",
                "tone": "professional",
                "decision_bias": "data_driven",
                "emotionality": "low",
                "description": "Traditional finance warrior who approaches crypto with skepticism"
            }
        }
        
        base_personality = personality_traits.get(ecosystem, {
            "temperament": "passionate",
            "tone": "confident",
            "decision_bias": "confirmation",
            "emotionality": "high",
            "description": f"Passionate {ecosystem} warrior"
        })
        
        # Add warrior-specific traits
        base_personality["ecosystem_bias"] = data.get("bias_strength", 0.9)
        base_personality["bullish_level"] = data.get("bullish_level", 0.9)
        base_personality["battle_phrases"] = data.get("battle_phrases", [])
        base_personality["enemy_ecosystems"] = data.get("enemy_ecosystems", [])
        base_personality["allied_ecosystems"] = data.get("allied_ecosystems", [])
        
        return base_personality
    
    def _generate_warrior_skills(self, ecosystem: str, data: Dict[str, Any]) -> List[str]:
        """Generate skills based on ecosystem"""
        skill_sets = {
            "ethereum_warriors": ["Ethereum Development", "Smart Contracts", "Solidity", "DeFi Protocols", "Layer 2", "Ethereum Ecosystem", "Ethereum Advocacy"],
            "solana_warriors": ["Solana Development", "Rust", "DeFi Protocols", "NFTs", "Solana Ecosystem", "High Performance", "Solana Advocacy"],
            "bitcoin_warriors": ["Bitcoin Development", "Lightning Network", "Bitcoin Script", "Bitcoin Ecosystem", "Digital Gold", "Store of Value", "Bitcoin Advocacy"],
            "defi_warriors": ["Yield Farming", "Liquidity Mining", "DeFi Protocols", "Risk Management", "APY Optimization", "DeFi Ecosystem", "DeFi Advocacy"],
            "tradfi_warriors": ["Financial Analysis", "Risk Assessment", "Portfolio Management", "Traditional Finance", "Regulatory Compliance", "Market Analysis", "TradFi Advocacy"]
        }
        
        return skill_sets.get(ecosystem, ["General Crypto", "Market Analysis", "Community Building", "Ecosystem Advocacy"])
    
    def _generate_warrior_weaknesses(self, ecosystem: str, data: Dict[str, Any]) -> List[str]:
        """Generate weaknesses based on ecosystem bias"""
        weakness_sets = {
            "ethereum_warriors": ["Ethereum Tunnel Vision", "Layer 2 Complexity", "Gas Fee Sensitivity", "Ethereum Dependency", "Ecosystem Bias"],
            "solana_warriors": ["Solana Dependency", "Centralization Concerns", "Ecosystem Maturity", "Network Stability", "Ecosystem Bias"],
            "bitcoin_warriors": ["Bitcoin Tunnel Vision", "Limited Functionality", "Slow Innovation", "Bitcoin Dependency", "Ecosystem Bias"],
            "defi_warriors": ["High Risk Tolerance", "Yield Chasing", "Protocol Risk", "Impermanent Loss", "Ecosystem Bias"],
            "tradfi_warriors": ["Crypto Skepticism", "Regulatory Concerns", "Volatility Aversion", "Traditional Mindset", "Ecosystem Bias"]
        }
        
        return weakness_sets.get(ecosystem, ["General Bias", "Market Volatility", "Regulatory Risk", "Ecosystem Bias"])
    
    def _generate_warrior_origin_story(self, ecosystem: str, data: Dict[str, Any]) -> str:
        """Generate origin story with warrior focus"""
        stories = {
            "ethereum_warriors": "Started as a developer who fell in love with Ethereum's smart contract capabilities. Witnessed the DeFi summer and became convinced that Ethereum is the future of finance. Now a passionate warrior for the Ethereum ecosystem, fighting against all competitors.",
            "solana_warriors": "Discovered Solana's speed and low fees after getting frustrated with Ethereum's gas prices. Built several projects on Solana and became convinced it's the next generation blockchain. Now a vocal warrior for the Solana ecosystem, ready to battle Ethereum maximalists.",
            "bitcoin_warriors": "Early Bitcoin adopter who believes in the original vision of decentralized money. Watched countless altcoins come and go, but Bitcoin remains the only truly decentralized cryptocurrency. Now a staunch Bitcoin warrior, defending against all altcoin shills.",
            "defi_warriors": "Started as a yield farmer during the DeFi summer. Got addicted to the high APYs and became a DeFi degenerate. Now a passionate warrior for DeFi, fighting against traditional finance and centralized systems.",
            "tradfi_warriors": "Traditional finance professional who entered crypto with skepticism. Approaches crypto with the same analytical rigor as traditional assets. Now a warrior for traditional finance, fighting against crypto hype and volatility."
        }
        
        return stories.get(ecosystem, f"Passionate about {ecosystem} and its potential to revolutionize finance. Now a warrior for the ecosystem.")
    
    def _generate_warrior_physical_description(self, ecosystem: str, data: Dict[str, Any]) -> str:
        """Generate physical description based on ecosystem"""
        descriptions = {
            "ethereum_warriors": "Wears an Ethereum hoodie and has a laser-etched ETH logo on their laptop. Always carrying a hardware wallet and ready to defend Ethereum against all competitors.",
            "solana_warriors": "Young and energetic, often wearing Solana merch. Has multiple Solana-themed stickers on their devices and is always ready to battle Ethereum maximalists.",
            "bitcoin_warriors": "Serious and stoic, often wearing Bitcoin-themed clothing. Has a physical Bitcoin coin collection and is ready to defend Bitcoin against all altcoin shills.",
            "defi_warriors": "Always checking their phone for the latest DeFi yields. Wears a DeFi-themed t-shirt and has multiple wallets, ready to fight traditional finance.",
            "tradfi_warriors": "Professional appearance, often wearing a suit. Has multiple monitors showing traditional finance charts and is ready to defend traditional finance against crypto hype."
        }
        
        return descriptions.get(ecosystem, f"Passionate about {ecosystem} and its potential. Ready to defend the ecosystem against all competitors.")
    
    def _generate_warrior_catchphrase(self, ecosystem: str, data: Dict[str, Any]) -> str:
        """Generate catchphrase with warrior bias"""
        phrases = data.get("battle_phrases", ["Crypto is the future!"])
        return random.choice(phrases)
    
    def _generate_warrior_llm_config(self, ecosystem: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate LLM config for warriors"""
        return {
            "model": random.choice(["gpt-4o-mini", "claude-3-haiku-20240307"]),
            "temperature": random.uniform(0.8, 0.95),  # Higher temperature for more passionate responses
            "max_tokens": random.randint(150, 250),
            "top_p": random.uniform(0.85, 0.95)
        }
    
    def _generate_warrior_activity_config(self, ecosystem: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate activity config for warriors"""
        return {
            "schedule": "cron: */3 * * * *",  # More active than regular agents
            "actions_per_awake": [2, 5]  # More actions per session
        }
    
    def _generate_warrior_memory_config(self, ecosystem: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate memory config for warriors"""
        return {
            "short_term_window": random.randint(15, 25),
            "long_term_vector_db": {
                "enabled": True,
                "collection_name": f"{ecosystem}_warrior_memory",
                "similarity_threshold": random.uniform(0.8, 0.95)
            }
        }
    
    def save_warriors(self, warriors: List[Dict[str, Any]]) -> None:
        """Save warriors to YAML files"""
        for warrior in warriors:
            filename = f"{warrior['id']}.yaml"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(warrior, f, default_flow_style=False, allow_unicode=True)
    
    def generate_and_save_warriors(self, count_per_ecosystem: int = 20) -> List[Dict[str, Any]]:
        """Generate and save ecosystem warriors"""
        print(f"⚔️ Generating {count_per_ecosystem} warriors per ecosystem...")
        
        warriors = self.generate_ecosystem_warriors(count_per_ecosystem)
        self.save_warriors(warriors)
        
        print(f"✅ Generated {len(warriors)} ecosystem warriors")
        print(f"📁 Saved to {self.output_dir}")
        
        return warriors


def main():
    """Main function to generate ecosystem warriors"""
    generator = EcosystemWarriorsGenerator()
    warriors = generator.generate_and_save_warriors(20)
    
    # Print summary
    ecosystem_counts = {}
    for warrior in warriors:
        ecosystem = warrior.get("ecosystem", "unknown")
        ecosystem_counts[ecosystem] = ecosystem_counts.get(ecosystem, 0) + 1
    
    print("\n⚔️ Ecosystem Warriors Distribution:")
    for ecosystem, count in ecosystem_counts.items():
        print(f"  {ecosystem}: {count} warriors")
    
    print("\n🎉 Ecosystem warriors generation complete!")


if __name__ == "__main__":
    main()
