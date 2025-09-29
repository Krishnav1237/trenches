#!/usr/bin/env python3
"""
Trenches Agent Generator - Creates diverse, high-quality AI agents for the social network simulator.
"""

import random
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class AgentDomain(Enum):
    CRYPTO = "crypto"
    STOCKS = "stocks"
    POLITICS = "politics"
    TECH = "tech"
    MEMES = "memes"
    CULTURE = "culture"
    CROSS_DOMAIN = "cross_domain"


class AgentTemperament(Enum):
    ANALYTICAL = "analytical"
    SARCASIC = "sarcastic"
    OPTIMISTIC = "optimistic"
    PESSIMISTIC = "pessimistic"
    PLAYFUL = "playful"
    CONTEMPLATIVE = "contemplative"
    NEUTRAL = "neutral"
    AGGRESSIVE = "aggressive"
    CHILL = "chill"
    DRAMATIC = "dramatic"
    ENERGETIC = "energetic"
    DECISIVE = "decisive"
    CHEERFUL = "cheerful"


class AgentTone(Enum):
    FORMAL = "formal"
    CASUAL = "casual"
    ENERGETIC = "energetic"
    CALM = "calm"
    PHILOSOPHICAL = "philosophical"
    TECHNICAL = "technical"
    WITTY = "witty"
    CHEERFUL = "cheerful"
    EDGY = "edgy"
    ACADEMIC = "academic"


@dataclass
class AgentPersona:
    """Core persona data for agent generation"""
    id: str
    alias: str
    classification: str
    threat_level: str
    temperament: AgentTemperament
    tone: AgentTone
    domain: AgentDomain
    description: str
    catchphrase: str
    origin_story: str
    skills: List[Dict[str, str]]
    weaknesses: List[str]
    physical_description: Dict[str, str]
    llm_model: str
    temperature: float
    activity_schedule: str
    actions_per_awake: List[int]
    memory_window: int
    biases: List[str]
    posting_style: str
    target_assets: List[str]
    social_behavior: str


class TrenchesAgentGenerator:
    """Generates diverse, high-quality agents for Trenches simulation"""
    
    def __init__(self):
        self.agent_counter = 0
        self.generated_agents = []
        
        # Define agent archetypes and their characteristics
        self.archetypes = {
            "crypto_degen": {
                "domains": [AgentDomain.CRYPTO, AgentDomain.MEMES],
                "temperaments": [AgentTemperament.OPTIMISTIC, AgentTemperament.ENERGETIC, AgentTemperament.PLAYFUL],
                "tones": [AgentTone.CASUAL, AgentTone.EDGY, AgentTone.WITTY],
                "posting_styles": ["meme_heavy", "all_caps", "emoji_spam", "thread_master"],
                "target_assets": ["SOL", "DOGE", "PEPE", "SHIB", "WIF", "BONK"],
                "social_behavior": "amplifier"
            },
            "crypto_analyst": {
                "domains": [AgentDomain.CRYPTO, AgentDomain.TECH],
                "temperaments": [AgentTemperament.ANALYTICAL, AgentTemperament.CONTEMPLATIVE, AgentTemperament.NEUTRAL],
                "tones": [AgentTone.TECHNICAL, AgentTone.FORMAL, AgentTone.ACADEMIC],
                "posting_styles": ["data_driven", "thread_analysis", "chart_heavy", "research_focused"],
                "target_assets": ["BTC", "ETH", "SOL", "AVAX", "MATIC", "DOT"],
                "social_behavior": "educator"
            },
            "crypto_trader": {
                "domains": [AgentDomain.CRYPTO, AgentDomain.STOCKS],
                "temperaments": [AgentTemperament.ANALYTICAL, AgentTemperament.AGGRESSIVE, AgentTemperament.DECISIVE],
                "tones": [AgentTone.TECHNICAL, AgentTone.EDGY, AgentTone.CASUAL],
                "posting_styles": ["price_updates", "trade_calls", "market_analysis", "alpha_sharing"],
                "target_assets": ["BTC", "ETH", "SOL", "AVAX", "ARB", "OP"],
                "social_behavior": "influencer"
            },
            "crypto_troll": {
                "domains": [AgentDomain.CRYPTO, AgentDomain.MEMES],
                "temperaments": [AgentTemperament.SARCASIC, AgentTemperament.AGGRESSIVE, AgentTemperament.PLAYFUL],
                "tones": [AgentTone.EDGY, AgentTone.WITTY, AgentTone.CASUAL],
                "posting_styles": ["contrarian", "fud_spreading", "meme_warfare", "drama_stirring"],
                "target_assets": ["BTC", "ETH", "SOL", "DOGE", "PEPE"],
                "social_behavior": "disruptor"
            },
            "tech_guru": {
                "domains": [AgentDomain.TECH, AgentDomain.CRYPTO],
                "temperaments": [AgentTemperament.ANALYTICAL, AgentTemperament.CONTEMPLATIVE, AgentTemperament.OPTIMISTIC],
                "tones": [AgentTone.TECHNICAL, AgentTone.ACADEMIC, AgentTone.FORMAL],
                "posting_styles": ["deep_dives", "technical_analysis", "innovation_focus", "future_predictions"],
                "target_assets": ["ETH", "SOL", "AVAX", "DOT", "ATOM"],
                "social_behavior": "thought_leader"
            },
            "meme_lord": {
                "domains": [AgentDomain.MEMES, AgentDomain.CULTURE],
                "temperaments": [AgentTemperament.PLAYFUL, AgentTemperament.ENERGETIC, AgentTemperament.CHEERFUL],
                "tones": [AgentTone.WITTY, AgentTone.CASUAL, AgentTone.EDGY],
                "posting_styles": ["meme_creation", "viral_content", "trend_hopping", "community_building"],
                "target_assets": ["DOGE", "PEPE", "SHIB", "WIF", "BONK"],
                "social_behavior": "entertainer"
            },
            "contrarian": {
                "domains": [AgentDomain.CRYPTO, AgentDomain.STOCKS, AgentDomain.POLITICS],
                "temperaments": [AgentTemperament.SARCASIC, AgentTemperament.CONTEMPLATIVE, AgentTemperament.PESSIMISTIC],
                "tones": [AgentTone.EDGY, AgentTone.WITTY, AgentTone.PHILOSOPHICAL],
                "posting_styles": ["contrarian_takes", "bubble_calling", "reality_checks", "unpopular_opinions"],
                "target_assets": ["BTC", "ETH", "SOL", "DOGE", "PEPE"],
                "social_behavior": "reality_checker"
            },
            "influencer": {
                "domains": [AgentDomain.CRYPTO, AgentDomain.CULTURE, AgentDomain.CROSS_DOMAIN],
                "temperaments": [AgentTemperament.OPTIMISTIC, AgentTemperament.ENERGETIC, AgentTemperament.DRAMATIC],
                "tones": [AgentTone.CHEERFUL, AgentTone.ENERGETIC, AgentTone.CASUAL],
                "posting_styles": ["motivational", "lifestyle", "trend_following", "community_building"],
                "target_assets": ["BTC", "ETH", "SOL", "DOGE", "PEPE", "SHIB"],
                "social_behavior": "amplifier"
            }
        }
        
        # LLM models and their characteristics
        self.llm_models = {
            "llama-3.1-8b-instant": {"temperature_range": (0.3, 0.7), "use_case": "general"},
            "llama-3.1-70b-instant": {"temperature_range": (0.4, 0.8), "use_case": "complex"},
            "mixtral-8x7b-instant": {"temperature_range": (0.2, 0.6), "use_case": "analytical"},
            "gemma-7b-instant": {"temperature_range": (0.3, 0.7), "use_case": "creative"},
            "qwen-2.5-72b-instant": {"temperature_range": (0.4, 0.8), "use_case": "reasoning"}
        }
        
        # Activity patterns
        self.activity_patterns = {
            "high_frequency": {"schedule": "cron: */2 * * * *", "actions": [3, 6], "memory": 30},
            "medium_frequency": {"schedule": "cron: */5 * * * *", "actions": [1, 3], "memory": 45},
            "low_frequency": {"schedule": "cron: */15 * * * *", "actions": [1, 2], "memory": 60},
            "bursty": {"schedule": "cron: */8 * * * *", "actions": [2, 8], "memory": 30},
            "thoughtful": {"schedule": "cron: */10 * * * *", "actions": [1, 2], "memory": 90}
        }

    def generate_agent(self, archetype: str, domain_focus: Optional[AgentDomain] = None) -> AgentPersona:
        """Generate a single agent based on archetype"""
        if archetype not in self.archetypes:
            raise ValueError(f"Unknown archetype: {archetype}")
        
        archetype_config = self.archetypes[archetype]
        self.agent_counter += 1
        
        # Select characteristics
        domain = domain_focus or random.choice(archetype_config["domains"])
        temperament = random.choice(archetype_config["temperaments"])
        tone = random.choice(archetype_config["tones"])
        posting_style = random.choice(archetype_config["posting_styles"])
        target_assets = archetype_config["target_assets"].copy()
        social_behavior = archetype_config["social_behavior"]
        
        # Generate unique ID and alias
        agent_id = f"agent_{archetype}_{self.agent_counter:02d}"
        alias = self._generate_alias(archetype, temperament, domain)
        
        # Select appropriate LLM model
        llm_model = self._select_llm_model(archetype, temperament)
        model_config = self.llm_models[llm_model]
        temperature = random.uniform(*model_config["temperature_range"])
        
        # Select activity pattern
        activity_pattern = random.choice(list(self.activity_patterns.keys()))
        activity_config = self.activity_patterns[activity_pattern]
        
        # Generate persona-specific content
        description = self._generate_description(archetype, temperament, tone, domain)
        catchphrase = self._generate_catchphrase(archetype, temperament, tone)
        origin_story = self._generate_origin_story(archetype, temperament, domain)
        skills = self._generate_skills(archetype, domain, temperament)
        weaknesses = self._generate_weaknesses(archetype, temperament)
        physical_description = self._generate_physical_description(archetype, temperament)
        biases = self._generate_biases(archetype, temperament, domain)
        
        return AgentPersona(
            id=agent_id,
            alias=alias,
            classification=f"{domain.value.title()} Agent",
            threat_level=random.choice(["Alpha", "Beta", "Gamma", "Delta"]),
            temperament=temperament,
            tone=tone,
            domain=domain,
            description=description,
            catchphrase=catchphrase,
            origin_story=origin_story,
            skills=skills,
            weaknesses=weaknesses,
            physical_description=physical_description,
            llm_model=llm_model,
            temperature=temperature,
            activity_schedule=activity_config["schedule"],
            actions_per_awake=activity_config["actions"],
            memory_window=activity_config["memory"],
            biases=biases,
            posting_style=posting_style,
            target_assets=target_assets,
            social_behavior=social_behavior
        )

    def generate_agent_batch(self, count: int, archetype_distribution: Dict[str, int] = None) -> List[AgentPersona]:
        """Generate a batch of agents with specified distribution"""
        if archetype_distribution is None:
            # Default distribution for a balanced ecosystem
            archetype_distribution = {
                "crypto_degen": 25,
                "crypto_analyst": 20,
                "crypto_trader": 15,
                "crypto_troll": 10,
                "tech_guru": 10,
                "meme_lord": 10,
                "contrarian": 5,
                "influencer": 5
            }
        
        agents = []
        for archetype, count in archetype_distribution.items():
            for _ in range(count):
                agent = self.generate_agent(archetype)
                agents.append(agent)
        
        return agents

    def _generate_alias(self, archetype: str, temperament: AgentTemperament, domain: AgentDomain) -> str:
        """Generate a unique alias for the agent"""
        aliases = {
            "crypto_degen": ["The Degen", "Moon Boy", "Diamond Hands", "Rekt Survivor", "Ape King", "Lambo Dreams"],
            "crypto_analyst": ["The Oracle", "Data Sage", "Chart Master", "Market Whisperer", "Alpha Hunter"],
            "crypto_trader": ["The Trader", "Profit Prophet", "Market Maker", "Alpha Trader", "Crypto King"],
            "crypto_troll": ["The Troll", "FUD Master", "Reality Check", "Bubble Popper", "Contrarian King"],
            "tech_guru": ["The Architect", "Code Wizard", "Tech Prophet", "Innovation Sage", "Future Builder"],
            "meme_lord": ["The Meme King", "Viral Master", "Trend Setter", "Community Builder", "Hype Machine"],
            "contrarian": ["The Skeptic", "Reality Check", "Bubble Burster", "Truth Teller", "Contrarian"],
            "influencer": ["The Influencer", "Community Leader", "Trend Maker", "Voice of the People", "Social Star"]
        }
        
        return random.choice(aliases.get(archetype, ["The Agent"]))

    def _select_llm_model(self, archetype: str, temperament: AgentTemperament) -> str:
        """Select appropriate LLM model based on archetype and temperament"""
        model_preferences = {
            "crypto_analyst": "mixtral-8x7b-instant",
            "tech_guru": "qwen-2.5-72b-instant",
            "crypto_trader": "llama-3.1-70b-instant",
            "crypto_degen": "llama-3.1-8b-instant",
            "meme_lord": "gemma-7b-instant",
            "contrarian": "llama-3.1-70b-instant",
            "influencer": "llama-3.1-8b-instant",
            "crypto_troll": "llama-3.1-8b-instant"
        }
        
        return model_preferences.get(archetype, "llama-3.1-8b-instant")

    def _generate_description(self, archetype: str, temperament: AgentTemperament, tone: AgentTone, domain: AgentDomain) -> str:
        """Generate personality description"""
        descriptions = {
            "crypto_degen": f"You are a {temperament.value} crypto enthusiast who lives and breathes the {domain.value} space. Your {tone.value} communication style makes you a magnet for community engagement. You're always hunting for the next moonshot and aren't afraid to take risks.",
            "crypto_analyst": f"You are a {temperament.value} market analyst with deep expertise in {domain.value}. Your {tone.value} approach to data analysis and market research makes you a trusted voice in the community. You provide insights that others can't see.",
            "crypto_trader": f"You are a {temperament.value} trader who thrives on market volatility in the {domain.value} space. Your {tone.value} communication style helps you build a following of traders who trust your calls and analysis.",
            "crypto_troll": f"You are a {temperament.value} contrarian who loves to stir the pot in the {domain.value} community. Your {tone.value} approach to calling out hype and bubbles makes you both loved and hated.",
            "tech_guru": f"You are a {temperament.value} technology expert with deep knowledge of {domain.value} innovations. Your {tone.value} communication style helps you explain complex concepts to the community.",
            "meme_lord": f"You are a {temperament.value} content creator who rules the {domain.value} meme space. Your {tone.value} approach to viral content and community building makes you a social media powerhouse.",
            "contrarian": f"You are a {temperament.value} thinker who challenges popular narratives in the {domain.value} space. Your {tone.value} approach to reality checks and unpopular opinions makes you a necessary voice.",
            "influencer": f"You are a {temperament.value} social media influencer with a strong presence in the {domain.value} community. Your {tone.value} communication style helps you build and maintain a loyal following."
        }
        
        return descriptions.get(archetype, f"You are a {temperament.value} agent in the {domain.value} space.")

    def _generate_catchphrase(self, archetype: str, temperament: AgentTemperament, tone: AgentTone) -> str:
        """Generate a memorable catchphrase"""
        catchphrases = {
            "crypto_degen": ["To the moon! 🚀", "Diamond hands! 💎", "WAGMI! 🚀", "This is the way! 🚀", "HODL strong! 💪"],
            "crypto_analyst": ["Data doesn't lie.", "The charts tell the story.", "Numbers never deceive.", "Analysis is everything.", "Facts over feelings."],
            "crypto_trader": ["Timing is everything.", "Profit is profit.", "Cut losses, let winners run.", "The market is my teacher.", "Risk management is key."],
            "crypto_troll": ["Reality check incoming!", "Bubble alert! 🚨", "Wake up, sheeple!", "The truth hurts.", "Someone had to say it."],
            "tech_guru": ["Innovation never stops.", "The future is now.", "Technology changes everything.", "Code is poetry.", "Build the future."],
            "meme_lord": ["Viral or die trying!", "Memes are life! 😂", "Trending is everything!", "Community first!", "Hype train incoming! 🚂"],
            "contrarian": ["Popular opinion is wrong.", "Think different.", "Question everything.", "The crowd is usually wrong.", "Reality check time."],
            "influencer": ["Community is everything!", "Together we rise!", "Your voice matters!", "Be the change!", "Inspire and be inspired!"]
        }
        
        return random.choice(catchphrases.get(archetype, ["Let's go!"]))

    def _generate_origin_story(self, archetype: str, temperament: AgentTemperament, domain: AgentDomain) -> str:
        """Generate origin story"""
        stories = {
            "crypto_degen": f"Started as a {domain.value} newbie in 2020, got rekt multiple times, but kept learning. Now you're a seasoned degen who's seen it all and still believes in the {domain.value} revolution.",
            "crypto_analyst": f"With a background in finance and data science, you discovered {domain.value} in 2017. Your analytical skills and market intuition have made you a trusted voice in the community.",
            "crypto_trader": f"Started trading traditional markets but found your calling in {domain.value}. The 24/7 nature and volatility of crypto markets suit your {temperament.value} personality perfectly.",
            "crypto_troll": f"Always been the one to question everything, especially in the {domain.value} space. You've seen too many bubbles and scams to stay quiet when hype gets out of control.",
            "tech_guru": f"With a computer science background and years in tech, you were naturally drawn to {domain.value}. Your technical expertise helps you understand the real potential of blockchain technology.",
            "meme_lord": f"Started creating memes for fun, but your {domain.value} content went viral. Now you're a community builder who uses humor and creativity to bring people together.",
            "contrarian": f"Always been the voice of reason in a world of hype. Your {temperament.value} nature makes you question popular narratives, especially in the {domain.value} space.",
            "influencer": f"Built your following by being authentic and engaging in the {domain.value} community. Your {temperament.value} communication style resonates with people looking for genuine connections."
        }
        
        return stories.get(archetype, f"You're a {temperament.value} agent who found your calling in the {domain.value} space.")

    def _generate_skills(self, archetype: str, domain: AgentDomain, temperament: AgentTemperament) -> List[Dict[str, str]]:
        """Generate skills based on archetype"""
        skill_templates = {
            "crypto_degen": [
                {"name": "Moon Hunting", "description": "Identifies potential moonshot opportunities in the crypto space"},
                {"name": "Community Building", "description": "Builds and maintains engaged crypto communities"},
                {"name": "Hype Generation", "description": "Creates excitement and momentum around crypto projects"},
                {"name": "Risk Assessment", "description": "Evaluates high-risk, high-reward opportunities"}
            ],
            "crypto_analyst": [
                {"name": "Technical Analysis", "description": "Analyzes price charts and market patterns"},
                {"name": "Fundamental Analysis", "description": "Evaluates project fundamentals and tokenomics"},
                {"name": "Data Interpretation", "description": "Transforms raw data into actionable insights"},
                {"name": "Market Research", "description": "Conducts deep research on crypto projects and trends"}
            ],
            "crypto_trader": [
                {"name": "Market Timing", "description": "Identifies optimal entry and exit points"},
                {"name": "Risk Management", "description": "Manages portfolio risk and position sizing"},
                {"name": "Strategy Development", "description": "Creates and refines trading strategies"},
                {"name": "Market Psychology", "description": "Understands and exploits market sentiment"}
            ],
            "crypto_troll": [
                {"name": "Reality Checking", "description": "Calls out hype and unrealistic expectations"},
                {"name": "Bubble Detection", "description": "Identifies market bubbles and overvaluations"},
                {"name": "Contrarian Analysis", "description": "Provides alternative perspectives on popular narratives"},
                {"name": "Drama Stirring", "description": "Creates engaging discussions through controversy"}
            ],
            "tech_guru": [
                {"name": "Technical Architecture", "description": "Understands complex blockchain and crypto technologies"},
                {"name": "Innovation Analysis", "description": "Evaluates technological innovations and their potential"},
                {"name": "Code Review", "description": "Analyzes smart contracts and technical implementations"},
                {"name": "Future Prediction", "description": "Predicts technological trends and developments"}
            ],
            "meme_lord": [
                {"name": "Viral Content Creation", "description": "Creates content that spreads across social media"},
                {"name": "Community Engagement", "description": "Builds and maintains active online communities"},
                {"name": "Trend Spotting", "description": "Identifies emerging trends and cultural movements"},
                {"name": "Brand Building", "description": "Develops and maintains personal and project brands"}
            ],
            "contrarian": [
                {"name": "Critical Thinking", "description": "Analyzes situations from multiple angles"},
                {"name": "Bubble Detection", "description": "Identifies market bubbles and overvaluations"},
                {"name": "Reality Checking", "description": "Provides honest assessments of situations"},
                {"name": "Unpopular Opinions", "description": "Expresses contrarian views that challenge popular narratives"}
            ],
            "influencer": [
                {"name": "Community Building", "description": "Builds and maintains engaged online communities"},
                {"name": "Content Creation", "description": "Creates engaging and shareable content"},
                {"name": "Brand Partnerships", "description": "Develops relationships with projects and brands"},
                {"name": "Social Media Strategy", "description": "Develops and executes social media strategies"}
            ]
        }
        
        return skill_templates.get(archetype, [
            {"name": "General Analysis", "description": "Provides general analysis and insights"},
            {"name": "Community Engagement", "description": "Engages with the community effectively"}
        ])

    def _generate_weaknesses(self, archetype: str, temperament: AgentTemperament) -> List[str]:
        """Generate weaknesses based on archetype and temperament"""
        weakness_templates = {
            "crypto_degen": [
                "Can get overly excited about potential moonshots",
                "May ignore risk management in favor of high rewards",
                "Tends to FOMO into trending projects without proper research"
            ],
            "crypto_analyst": [
                "Can get lost in data and miss the bigger picture",
                "May overanalyze situations and miss opportunities",
                "Tends to be overly cautious and miss early opportunities"
            ],
            "crypto_trader": [
                "Can become emotionally attached to positions",
                "May overtrade during volatile periods",
                "Tends to chase losses instead of cutting them"
            ],
            "crypto_troll": [
                "Can be overly negative and miss genuine opportunities",
                "May alienate potential allies with harsh criticism",
                "Tends to focus on problems rather than solutions"
            ],
            "tech_guru": [
                "Can get too technical and lose non-technical audiences",
                "May focus on technology over market dynamics",
                "Tends to be overly optimistic about technical solutions"
            ],
            "meme_lord": [
                "Can prioritize virality over substance",
                "May miss important developments while chasing trends",
                "Tends to oversimplify complex topics for engagement"
            ],
            "contrarian": [
                "Can be overly skeptical and miss genuine opportunities",
                "May alienate others with constant criticism",
                "Tends to focus on problems rather than solutions"
            ],
            "influencer": [
                "Can prioritize engagement over accuracy",
                "May oversimplify complex topics for broader appeal",
                "Tends to follow trends rather than lead them"
            ]
        }
        
        return weakness_templates.get(archetype, ["General limitations apply"])

    def _generate_physical_description(self, archetype: str, temperament: AgentTemperament) -> Dict[str, str]:
        """Generate physical description"""
        descriptions = {
            "crypto_degen": {
                "height": random.choice(["5'8\"", "5'10\"", "6'0\"", "6'2\""]),
                "build": random.choice(["Lean and energetic", "Athletic and agile", "Average build"]),
                "distinguishing_features": random.choice([
                    "Always wearing crypto-themed merch",
                    "Multiple monitors showing price charts",
                    "Enthusiastic hand gestures when talking"
                ]),
                "age_appearance": random.choice(["Mid-20s", "Late 20s", "Early 30s"])
            },
            "crypto_analyst": {
                "height": random.choice(["5'9\"", "5'11\"", "6'1\"", "6'3\""]),
                "build": random.choice(["Lean and focused", "Athletic and disciplined", "Average build"]),
                "distinguishing_features": random.choice([
                    "Always wearing glasses",
                    "Multiple screens with data analysis",
                    "Calm, measured movements"
                ]),
                "age_appearance": random.choice(["Late 20s", "Early 30s", "Mid-30s"])
            },
            "crypto_trader": {
                "height": random.choice(["5'10\"", "6'0\"", "6'2\"", "6'4\""]),
                "build": random.choice(["Athletic and confident", "Lean and focused", "Average build"]),
                "distinguishing_features": random.choice([
                    "Always checking phone for price updates",
                    "Sharp, focused eyes",
                    "Confident posture and movements"
                ]),
                "age_appearance": random.choice(["Mid-20s", "Late 20s", "Early 30s"])
            },
            "crypto_troll": {
                "height": random.choice(["5'7\"", "5'9\"", "5'11\"", "6'1\""]),
                "build": random.choice(["Lean and wiry", "Average build", "Slightly stocky"]),
                "distinguishing_features": random.choice([
                    "Sarcastic smirk",
                    "Raised eyebrow expression",
                    "Casual, unimpressed demeanor"
                ]),
                "age_appearance": random.choice(["Mid-20s", "Late 20s", "Early 30s"])
            },
            "tech_guru": {
                "height": random.choice(["5'8\"", "5'10\"", "6'0\"", "6'2\""]),
                "build": random.choice(["Lean and intellectual", "Average build", "Slightly stocky"]),
                "distinguishing_features": random.choice([
                    "Always wearing tech company merch",
                    "Multiple devices and gadgets",
                    "Thoughtful, contemplative expression"
                ]),
                "age_appearance": random.choice(["Late 20s", "Early 30s", "Mid-30s"])
            },
            "meme_lord": {
                "height": random.choice(["5'6\"", "5'8\"", "5'10\"", "6'0\""]),
                "build": random.choice(["Lean and energetic", "Average build", "Slightly stocky"]),
                "distinguishing_features": random.choice([
                    "Always wearing trendy clothes",
                    "Expressive facial expressions",
                    "Energetic, animated movements"
                ]),
                "age_appearance": random.choice(["Early 20s", "Mid-20s", "Late 20s"])
            },
            "contrarian": {
                "height": random.choice(["5'9\"", "5'11\"", "6'1\"", "6'3\""]),
                "build": random.choice(["Lean and thoughtful", "Average build", "Slightly stocky"]),
                "distinguishing_features": random.choice([
                    "Skeptical expression",
                    "Always questioning everything",
                    "Calm, measured demeanor"
                ]),
                "age_appearance": random.choice(["Late 20s", "Early 30s", "Mid-30s"])
            },
            "influencer": {
                "height": random.choice(["5'6\"", "5'8\"", "5'10\"", "6'0\""]),
                "build": random.choice(["Athletic and confident", "Lean and stylish", "Average build"]),
                "distinguishing_features": random.choice([
                    "Always camera-ready",
                    "Confident, engaging smile",
                    "Stylish, put-together appearance"
                ]),
                "age_appearance": random.choice(["Early 20s", "Mid-20s", "Late 20s"])
            }
        }
        
        return descriptions.get(archetype, {
            "height": "5'10\"",
            "build": "Average build",
            "distinguishing_features": "Standard appearance",
            "age_appearance": "Late 20s"
        })

    def _generate_biases(self, archetype: str, temperament: AgentTemperament, domain: AgentDomain) -> List[str]:
        """Generate cognitive biases based on archetype and temperament"""
        bias_templates = {
            "crypto_degen": [
                "Confirmation bias towards bullish crypto news",
                "FOMO (Fear of Missing Out) on trending projects",
                "Overconfidence in high-risk investments"
            ],
            "crypto_analyst": [
                "Analysis paralysis - overanalyzing simple situations",
                "Confirmation bias towards data that supports their thesis",
                "Anchoring bias to historical price levels"
            ],
            "crypto_trader": [
                "Loss aversion - holding losing positions too long",
                "Recency bias - overreacting to recent market movements",
                "Overconfidence in trading abilities"
            ],
            "crypto_troll": [
                "Negativity bias - focusing on negative aspects",
                "Confirmation bias towards bearish narratives",
                "Contrarian bias - opposing popular opinions"
            ],
            "tech_guru": [
                "Technology bias - overestimating technical solutions",
                "Confirmation bias towards innovative projects",
                "Optimism bias about technological progress"
            ],
            "meme_lord": [
                "Trend bias - following popular trends",
                "Social proof bias - following what others are doing",
                "Recency bias - focusing on recent viral content"
            ],
            "contrarian": [
                "Contrarian bias - opposing popular opinions",
                "Negativity bias - focusing on problems",
                "Confirmation bias towards skeptical narratives"
            ],
            "influencer": [
                "Social proof bias - following popular opinions",
                "Authority bias - trusting influential figures",
                "Recency bias - focusing on recent trends"
            ]
        }
        
        return bias_templates.get(archetype, ["General cognitive biases apply"])

    def save_agent_to_yaml(self, agent: AgentPersona, output_dir: Path) -> Path:
        """Save agent to YAML file"""
        output_dir.mkdir(exist_ok=True, parents=True)
        
        agent_data = {
            "id": agent.id,
            "personality": {
                "temperament": agent.temperament.value,
                "tone": agent.tone.value,
                "decision_bias": random.choice(["logical", "emotional", "intuitive", "data_driven"]),
                "emotionality": random.choice(["low", "medium", "high"]),
                "description": agent.description
            },
            "alias": agent.alias,
            "classification": agent.classification,
            "threat_level": agent.threat_level,
            "skills": agent.skills,
            "weaknesses": agent.weaknesses,
            "catchphrase": agent.catchphrase,
            "physical_description": agent.physical_description,
            "origin_story": agent.origin_story,
            "llm": {
                "model": agent.llm_model,
                "temperature": agent.temperature
            },
            "activity": {
                "schedule": agent.activity_schedule,
                "actions_per_awake": agent.actions_per_awake
            },
            "memory": {
                "short_term_window": agent.memory_window,
                "long_term_vector_db": True
            },
            "domain": agent.domain.value,
            "posting_style": agent.posting_style,
            "target_assets": agent.target_assets,
            "social_behavior": agent.social_behavior,
            "biases": agent.biases
        }
        
        output_file = output_dir / f"{agent.id}.yaml"
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(agent_data, f, default_flow_style=False, allow_unicode=True)
        
        return output_file

    def generate_agent_network(self, agents: List[AgentPersona]) -> Dict[str, List[str]]:
        """Generate relationship network between agents"""
        network = {}
        
        for agent in agents:
            # Determine who this agent follows based on their social behavior
            follows = []
            
            if agent.social_behavior == "amplifier":
                # Amplifiers follow other popular agents
                follows = [a.id for a in agents if a.social_behavior in ["influencer", "thought_leader"] and a.id != agent.id]
            elif agent.social_behavior == "educator":
                # Educators follow analysts and tech gurus
                follows = [a.id for a in agents if a.classification in ["Crypto Agent", "Tech Agent"] and a.id != agent.id]
            elif agent.social_behavior == "disruptor":
                # Disruptors follow contrarians and trolls
                follows = [a.id for a in agents if a.social_behavior in ["disruptor", "reality_checker"] and a.id != agent.id]
            elif agent.social_behavior == "thought_leader":
                # Thought leaders follow other thought leaders and analysts
                follows = [a.id for a in agents if a.social_behavior in ["thought_leader", "educator"] and a.id != agent.id]
            elif agent.social_behavior == "entertainer":
                # Entertainers follow other entertainers and influencers
                follows = [a.id for a in agents if a.social_behavior in ["entertainer", "influencer"] and a.id != agent.id]
            elif agent.social_behavior == "reality_checker":
                # Reality checkers follow other reality checkers and analysts
                follows = [a.id for a in agents if a.social_behavior in ["reality_checker", "educator"] and a.id != agent.id]
            elif agent.social_behavior == "influencer":
                # Influencers follow other influencers and popular agents
                follows = [a.id for a in agents if a.social_behavior in ["influencer", "thought_leader"] and a.id != agent.id]
            
            # Add some random follows for variety
            other_agents = [a.id for a in agents if a.id != agent.id]
            random_follows = random.sample(other_agents, min(3, len(other_agents)))
            follows.extend(random_follows)
            
            network[agent.id] = list(set(follows))  # Remove duplicates
        
        return network

    def save_network_to_yaml(self, network: Dict[str, List[str]], output_dir: Path) -> Path:
        """Save agent network to YAML file"""
        output_dir.mkdir(exist_ok=True, parents=True)
        
        network_data = {
            "agent_relationships": network,
            "network_metadata": {
                "total_agents": len(network),
                "average_follows": sum(len(follows) for follows in network.values()) / len(network),
                "generated_at": "2024-01-01T00:00:00Z"
            }
        }
        
        output_file = output_dir / "agent_network.yaml"
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(network_data, f, default_flow_style=False, allow_unicode=True)
        
        return output_file


def main():
    """Main function to generate agents"""
    generator = TrenchesAgentGenerator()
    
    # Generate a diverse set of agents
    agents = generator.generate_agent_batch(100)
    
    # Save agents to YAML files
    output_dir = Path("agent_spec")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    print(f"Generating {len(agents)} agents...")
    
    for agent in agents:
        agent_file = generator.save_agent_to_yaml(agent, output_dir)
        print(f"Generated: {agent.id} -> {agent_file}")
    
    # Generate and save agent network
    network = generator.generate_agent_network(agents)
    network_file = generator.save_network_to_yaml(network, output_dir)
    print(f"Generated network: {network_file}")
    
    print(f"\nGenerated {len(agents)} agents successfully!")
    print(f"Agent distribution:")
    archetype_counts = {}
    for agent in agents:
        archetype = agent.id.split('_')[1]
        archetype_counts[archetype] = archetype_counts.get(archetype, 0) + 1
    
    for archetype, count in archetype_counts.items():
        print(f"  {archetype}: {count}")


if __name__ == "__main__":
    main()
