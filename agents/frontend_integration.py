#!/usr/bin/env python3
"""
Frontend Integration - Connects the Trenches agent system with the React frontend.
"""

import asyncio
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from agent_generator import TrenchesAgentGenerator
from core.enhanced_prompt_engine import EnhancedPromptEngine
from core.simulation import TrenchesSimulation
from models.entities import SimulationContext, Tweet


class FrontendIntegration:
    """Integrates the Trenches agent system with the React frontend"""
    
    def __init__(self, config_path: Path = None):
        if config_path is None:
            config_path = Path("config")
        self.config_path = config_path
        self.agent_generator = TrenchesAgentGenerator()
        self.enhanced_prompt_engine = EnhancedPromptEngine(config_path)
        self.simulation = None
        
        # Frontend data structures
        self.frontend_agents = {}
        self.frontend_tweets = []
        self.agent_profiles = {}

    async def initialize_system(self):
        """Initialize the agent system for frontend integration"""
        print("🔗 Initializing Trenches agent system for frontend integration...")
        
        # Initialize simulation
        self.simulation = TrenchesSimulation(self.config_path)
        await self.simulation.__aenter__()
        await self.simulation.initialize()
        
        # Load agents
        self.simulation.agents = self.simulation.agent_manager.load_all_agents()
        print(f"✅ Loaded {len(self.simulation.agents)} agents")
        
        # Create frontend-compatible agent data
        await self._create_frontend_agents()
        
        print("🎉 Frontend integration initialized successfully!")

    async def _create_frontend_agents(self):
        """Create frontend-compatible agent data"""
        for agent_id, agent in self.simulation.agents.items():
            # Create frontend-compatible agent profile
            frontend_agent = {
                "id": agent_id,
                "username": agent.get("alias", agent_id),
                "displayName": agent.get("alias", agent_id),
                "avatar": self._generate_agent_avatar(agent),
                "bio": agent.get("personality", {}).get("description", ""),
                "followers": self._generate_follower_count(agent),
                "following": self._generate_following_count(agent),
                "postsCount": 0,  # Will be updated as agents post
                "verified": agent.get("threat_level") in ["Alpha", "Beta"],
                "personality": {
                    "temperament": agent.get("personality", {}).get("temperament", "neutral"),
                    "tone": agent.get("personality", {}).get("tone", "neutral"),
                    "domain": agent.get("domain", "crypto"),
                    "catchphrase": agent.get("catchphrase", ""),
                    "target_assets": agent.get("target_assets", [])
                },
                "activity": {
                    "schedule": agent.get("activity", {}).get("schedule", "cron: */5 * * * *"),
                    "actions_per_awake": agent.get("activity", {}).get("actions_per_awake", [1, 2])
                }
            }
            
            self.frontend_agents[agent_id] = frontend_agent
            self.agent_profiles[agent_id] = frontend_agent

    def _generate_agent_avatar(self, agent: Dict) -> str:
        """Generate avatar URL for agent"""
        # Use different avatar based on agent type
        avatar_map = {
            "crypto_degen": "pfp1.png",
            "crypto_analyst": "pfp2.png", 
            "crypto_trader": "pfp3.png",
            "crypto_troll": "pfp4.png",
            "tech_guru": "pfp5.png",
            "meme_lord": "pfp6.png",
            "contrarian": "pfp1.png",
            "influencer": "pfp2.png"
        }
        
        agent_type = agent.get("id", "").split("_")[1] if "_" in agent.get("id", "") else "crypto_degen"
        return f"/src/assets/{avatar_map.get(agent_type, 'pfp1.png')}"

    def _generate_follower_count(self, agent: Dict) -> int:
        """Generate realistic follower count based on agent type"""
        import random
        
        agent_type = agent.get("id", "").split("_")[1] if "_" in agent.get("id", "") else "crypto_degen"
        
        follower_ranges = {
            "crypto_degen": (100, 5000),
            "crypto_analyst": (1000, 10000),
            "crypto_trader": (500, 8000),
            "crypto_troll": (200, 3000),
            "tech_guru": (2000, 15000),
            "meme_lord": (500, 12000),
            "contrarian": (300, 4000),
            "influencer": (1000, 20000)
        }
        
        min_followers, max_followers = follower_ranges.get(agent_type, (100, 1000))
        return random.randint(min_followers, max_followers)

    def _generate_following_count(self, agent: Dict) -> int:
        """Generate realistic following count"""
        import random
        followers = self._generate_follower_count(agent)
        # Following is typically 10-50% of followers
        return random.randint(followers // 10, followers // 2)

    async def generate_agent_tweets(self, count: int = 20) -> List[Dict]:
        """Generate tweets from agents for the frontend"""
        tweets = []
        
        # Select active agents
        active_agents = list(self.simulation.agents.values())[:min(count, len(self.simulation.agents))]
        
        for agent in active_agents:
            try:
                # Create context
                context = SimulationContext(
                    trending_topics=["BTC", "ETH", "SOL", "DOGE", "PEPE"],
                    activity_level="high",
                    sentiment="positive",
                    time_context="afternoon"
                )
                
                # Generate tweet content
                prompt = self.enhanced_prompt_engine.build_enhanced_prompt(
                    agent, "tweet", context
                )
                
                # For demo purposes, create realistic tweet content
                tweet_content = self._generate_realistic_tweet(agent, context)
                
                # Create frontend-compatible tweet
                tweet = {
                    "id": f"tweet_{len(tweets) + 1}",
                    "agent_id": agent.get("id"),
                    "content": tweet_content,
                    "thread_id": None,
                    "likes": self._generate_engagement_count("likes"),
                    "retweets": self._generate_engagement_count("retweets"),
                    "created_at": self._generate_timestamp(),
                    "user": self.frontend_agents.get(agent.get("id"), {
                        "id": agent.get("id"),
                        "username": agent.get("alias", agent.get("id")),
                        "displayName": agent.get("alias", agent.get("id")),
                        "avatar": self._generate_agent_avatar(agent)
                    })
                }
                
                tweets.append(tweet)
                
            except Exception as e:
                print(f"Error generating tweet for {agent.get('id')}: {e}")
                continue
        
        return tweets

    def _generate_realistic_tweet(self, agent: Dict, context: SimulationContext) -> str:
        """Generate realistic tweet content based on agent personality"""
        import random
        
        agent_type = agent.get("id", "").split("_")[1] if "_" in agent.get("id", "") else "crypto_degen"
        temperament = agent.get("personality", {}).get("temperament", "neutral")
        tone = agent.get("personality", {}).get("tone", "neutral")
        target_assets = agent.get("target_assets", ["BTC", "ETH"])
        
        # Select random asset
        asset = random.choice(target_assets)
        
        # Generate content based on agent type and personality
        content_templates = {
            "crypto_degen": [
                f"{asset} is going to the moon! 🚀",
                f"Diamond hands! {asset} to $100k! 💎",
                f"Just bought more {asset}. This is the way! 🚀",
                f"{asset} breaking resistance! Time to load up! 📈",
                f"WAGMI! {asset} is the future! 🌙"
            ],
            "crypto_analyst": [
                f"Technical analysis shows {asset} is forming a bullish pattern.",
                f"{asset} RSI is at 65, indicating healthy momentum.",
                f"Market structure for {asset} remains intact above key support.",
                f"Volume analysis suggests {asset} is building for a breakout.",
                f"Fibonacci retracement levels for {asset} show strong support at current levels."
            ],
            "crypto_trader": [
                f"Scalping {asset} on the 5m chart. Risk management is key.",
                f"Entry: {asset} at support. Stop loss set. Target: +5%",
                f"{asset} showing strong momentum. Adding to position.",
                f"Market volatility in {asset} creating opportunities.",
                f"Position sizing for {asset} based on risk tolerance."
            ],
            "crypto_troll": [
                f"Another {asset} moon boy calling the top. Classic.",
                f"{asset} will dump 50% by next week. Mark my words.",
                f"Everyone's bullish on {asset}. Time to short?",
                f"{asset} hype is getting out of control. Reality check needed.",
                f"Wake up, {asset} holders. This is a bubble."
            ],
            "tech_guru": [
                f"The technology behind {asset} is revolutionary.",
                f"{asset} represents the future of decentralized systems.",
                f"Blockchain innovation in {asset} ecosystem is impressive.",
                f"Technical architecture of {asset} is sound and scalable.",
                f"Open source development in {asset} community is thriving."
            ],
            "meme_lord": [
                f"{asset} memes are getting spicy! 🔥",
                f"Community for {asset} is absolutely wild! 😂",
                f"Viral {asset} content incoming! 📱",
                f"{asset} culture is unmatched! 🎭",
                f"Memes about {asset} are pure gold! 🏆"
            ],
            "contrarian": [
                f"Everyone's bullish on {asset}. I'm skeptical.",
                f"{asset} hype doesn't match the fundamentals.",
                f"Contrarian take: {asset} is overvalued.",
                f"While others FOMO into {asset}, I'm staying cautious.",
                f"{asset} narrative seems too good to be true."
            ],
            "influencer": [
                f"Excited about the {asset} community! Together we rise! 💪",
                f"{asset} represents the future of finance. Join the movement! 🌟",
                f"Building wealth with {asset}. Education is key! 📚",
                f"{asset} community is amazing! Grateful to be part of it! 🙏",
                f"Success with {asset} comes from patience and discipline! ⏰"
            ]
        }
        
        templates = content_templates.get(agent_type, [f"Talking about {asset} today."])
        return random.choice(templates)

    def _generate_engagement_count(self, engagement_type: str) -> int:
        """Generate realistic engagement counts"""
        import random
        
        if engagement_type == "likes":
            return random.randint(0, 500)
        elif engagement_type == "retweets":
            return random.randint(0, 100)
        else:
            return random.randint(0, 50)

    def _generate_timestamp(self) -> str:
        """Generate realistic timestamp"""
        import random
        from datetime import datetime, timedelta
        
        # Random time within last 24 hours
        now = datetime.now()
        random_hours = random.randint(0, 24)
        timestamp = now - timedelta(hours=random_hours)
        return timestamp.isoformat()

    async def create_frontend_data_files(self):
        """Create data files for the frontend"""
        print("📁 Creating frontend data files...")
        
        # Create agents data
        agents_data = {
            "agents": list(self.frontend_agents.values()),
            "total_agents": len(self.frontend_agents),
            "agent_types": self._get_agent_type_distribution()
        }
        
        # Create tweets data
        tweets_data = await self.generate_agent_tweets(50)
        
        # Save to files
        frontend_data_dir = Path("frontend_data")
        frontend_data_dir.mkdir(exist_ok=True)
        
        # Save agents
        with open(frontend_data_dir / "agents.json", "w", encoding="utf-8") as f:
            json.dump(agents_data, f, indent=2)
        
        # Save tweets
        with open(frontend_data_dir / "tweets.json", "w", encoding="utf-8") as f:
            json.dump(tweets_data, f, indent=2)
        
        # Create API integration file
        await self._create_api_integration_file()
        
        print(f"✅ Frontend data files created in {frontend_data_dir}")

    def _get_agent_type_distribution(self) -> Dict[str, int]:
        """Get distribution of agent types"""
        distribution = {}
        for agent in self.frontend_agents.values():
            agent_type = agent["id"].split("_")[1] if "_" in agent["id"] else "unknown"
            distribution[agent_type] = distribution.get(agent_type, 0) + 1
        return distribution

    async def _create_api_integration_file(self):
        """Create API integration file for the frontend"""
        api_integration = """
// Trenches Agent System API Integration
// This file connects the frontend with the Trenches agent system

const TRENCHES_API_BASE = 'http://localhost:8080';

// Agent API endpoints
export const agentAPI = {
  // Get all agents
  getAgents: async () => {
    const response = await fetch(`${TRENCHES_API_BASE}/profiles`);
    return response.json();
  },
  
  // Get agent by ID
  getAgent: async (id) => {
    const response = await fetch(`${TRENCHES_API_BASE}/profiles/${id}`);
    return response.json();
  },
  
  // Get agent tweets
  getAgentTweets: async (agentId) => {
    const response = await fetch(`${TRENCHES_API_BASE}/tweets?agent_id=${agentId}`);
    return response.json();
  }
};

// Tweet API endpoints
export const tweetAPI = {
  // Get all tweets
  getTweets: async () => {
    const response = await fetch(`${TRENCHES_API_BASE}/tweets`);
    return response.json();
  },
  
  // Get timeline
  getTimeline: async (limit = 20) => {
    const response = await fetch(`${TRENCHES_API_BASE}/timeline?limit=${limit}`);
    return response.json();
  },
  
  // Create tweet
  createTweet: async (agentId, content, threadId = null) => {
    const response = await fetch(`${TRENCHES_API_BASE}/tweets`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent_id: agentId, content, thread_id: threadId })
    });
    return response.json();
  },
  
  // Like tweet
  likeTweet: async (tweetId) => {
    const response = await fetch(`${TRENCHES_API_BASE}/tweets/${tweetId}/likes`, {
      method: 'POST'
    });
    return response.json();
  },
  
  // Retweet
  retweet: async (tweetId) => {
    const response = await fetch(`${TRENCHES_API_BASE}/tweets/${tweetId}/retweets`, {
      method: 'POST'
    });
    return response.json();
  }
};

// Statistics API
export const statsAPI = {
  // Get agent statistics
  getAgentStats: async () => {
    const response = await fetch(`${TRENCHES_API_BASE}/stats`);
    return response.json();
  },
  
  // Get metrics
  getMetrics: async () => {
    const response = await fetch(`${TRENCHES_API_BASE}/metrics`);
    return response.json();
  }
};

// Real-time updates (WebSocket integration)
export const realtimeAPI = {
  connect: () => {
    // WebSocket connection for real-time updates
    const ws = new WebSocket('ws://localhost:8080/ws');
    return ws;
  }
};
"""
        
        with open("frontend_data/api_integration.js", "w", encoding="utf-8") as f:
            f.write(api_integration)

    async def run_agent_simulation(self, duration_minutes: int = 5):
        """Run agent simulation to generate content for frontend"""
        print(f"🤖 Running agent simulation for {duration_minutes} minutes...")
        
        try:
            # Run simulation
            await self.simulation.run_simulation()
            
            # Get generated tweets
            recent_tweets = await self.simulation.api_client.get_timeline(limit=100)
            
            # Convert to frontend format
            frontend_tweets = []
            for tweet in recent_tweets:
                frontend_tweet = {
                    "id": str(tweet.id),
                    "agent_id": tweet.agent_id,
                    "content": tweet.content,
                    "thread_id": tweet.thread_id,
                    "likes": tweet.likes,
                    "retweets": tweet.retweets,
                    "created_at": datetime.now().isoformat(),
                    "user": self.frontend_agents.get(tweet.agent_id, {
                        "id": tweet.agent_id,
                        "username": tweet.agent_id,
                        "displayName": tweet.agent_id,
                        "avatar": "/src/assets/pfp1.png"
                    })
                }
                frontend_tweets.append(frontend_tweet)
            
            # Save updated tweets
            with open("frontend_data/tweets.json", "w", encoding="utf-8") as f:
                json.dump(frontend_tweets, f, indent=2)
            
            print(f"✅ Generated {len(frontend_tweets)} tweets for frontend")
            
        except Exception as e:
            print(f"❌ Simulation error: {e}")

    async def cleanup(self):
        """Cleanup resources"""
        if self.simulation:
            await self.simulation.__aexit__(None, None, None)


async def main():
    """Main function to set up frontend integration"""
    integration = FrontendIntegration()
    
    try:
        # Initialize system
        await integration.initialize_system()
        
        # Create frontend data files
        await integration.create_frontend_data_files()
        
        # Run simulation to generate content
        await integration.run_agent_simulation(duration_minutes=2)
        
        print("\n🎉 Frontend integration complete!")
        print("📁 Frontend data files created in frontend_data/")
        print("🔗 Use the API integration file to connect your React frontend")
        
    except Exception as e:
        print(f"❌ Integration error: {e}")
    finally:
        await integration.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
