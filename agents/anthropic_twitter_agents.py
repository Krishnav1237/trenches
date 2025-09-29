#!/usr/bin/env python3
"""
🚀 Trenches Agent System with X Integration - Anthropic Powered!
==============================================================

This connects your Anthropic-powered agents directly to X (Twitter).
Your agents will generate tweets using Claude and post them to your X account!
"""

import os
import asyncio
import json
import logging
import random
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import tweepy
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AnthropicTwitterAgent:
    """AI Agent powered by Anthropic that posts to Twitter"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Twitter setup
        self.twitter_client = None
        self.last_tweet_time = {}
        self.rate_limit_delay = 5  # 5 seconds between tweets
        
        # Anthropic setup
        self.anthropic_client = None
        
        # Agent personalities
        self.agent_personas = {
            'CryptoDegen_Alpha': {
                'personality': 'Aggressive crypto trader who loves high-risk plays and moon missions',
                'style': 'Uses lots of rocket emojis, diamond hands, degenerate slang',
                'topics': ['Bitcoin', 'altcoins', 'DeFi', 'yield farming', 'meme coins']
            },
            'SolanaMaxi_Pro': {
                'personality': 'Solana ecosystem expert and maximalist',
                'style': 'Professional but enthusiastic, uses sun emoji, technical analysis',
                'topics': ['Solana', 'SOL', 'Solana DeFi', 'Solana NFTs', 'ecosystem updates']
            },
            'AIAgentAlpha': {
                'personality': 'AI and crypto intersection expert, futuristic thinker',
                'style': 'Tech-focused, uses robot emoji, talks about future trends',
                'topics': ['AI + Crypto', 'autonomous agents', 'machine learning', 'future tech']
            },
            'TechnicalAnalyst_99': {
                'personality': 'Chart analysis expert, data-driven trader',
                'style': 'Uses chart emojis, technical terms, analytical language',
                'topics': ['technical analysis', 'price action', 'support/resistance', 'indicators']
            },
            'MemeLord_420': {
                'personality': 'Meme coin specialist with humor and sarcasm',
                'style': 'Funny, uses meme references, frog emoji, self-deprecating humor',
                'topics': ['meme coins', 'PEPE', 'DOGE', 'community', 'crypto humor']
            }
        }
    
    async def initialize(self) -> bool:
        """Initialize Twitter and Anthropic clients"""
        # Initialize Twitter
        twitter_success = await self._init_twitter()
        
        # Initialize Anthropic
        anthropic_success = await self._init_anthropic()
        
        return twitter_success and anthropic_success
    
    async def _init_twitter(self) -> bool:
        """Initialize Twitter API"""
        try:
            api_key = os.getenv('TWITTER_API_KEY')
            api_secret = os.getenv('TWITTER_API_SECRET')
            access_token = os.getenv('TWITTER_ACCESS_TOKEN')
            access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
            
            if not all([api_key, api_secret, access_token, access_token_secret, bearer_token]):
                self.logger.error("Missing Twitter API credentials")
                return False
            
            self.twitter_client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret,
                wait_on_rate_limit=True
            )
            
            # Test connection
            me = self.twitter_client.get_me()
            print(f"🐦 ✅ Connected to X: @{me.data.username}")
            return True
            
        except Exception as e:
            self.logger.error(f"Twitter initialization failed: {e}")
            return False
    
    async def _init_anthropic(self) -> bool:
        """Initialize Anthropic API"""
        try:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                self.logger.error("Missing Anthropic API key")
                return False
            
            self.anthropic_client = anthropic.Anthropic(api_key=api_key)
            
            # Test connection with a simple request
            test_response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Say 'AI connected'"}]
            )
            
            print(f"🤖 ✅ Connected to Anthropic: {test_response.content[0].text}")
            return True
            
        except Exception as e:
            self.logger.error(f"Anthropic initialization failed: {e}")
            return False
    
    async def generate_agent_tweet(self, agent_name: str, context: Optional[Dict] = None) -> str:
        """Generate a tweet using Anthropic for a specific agent"""
        if agent_name not in self.agent_personas:
            agent_name = random.choice(list(self.agent_personas.keys()))
        
        persona = self.agent_personas[agent_name]
        
        # Build prompt for Claude
        prompt = f"""You are {agent_name}, a crypto AI agent with this personality:
        
Personality: {persona['personality']}
Style: {persona['style']}
Topics: {', '.join(persona['topics'])}

Current crypto context:
- BTC is trading around $65,000
- Alt season might be starting
- DeFi yields are attractive
- AI + Crypto narrative is growing

Generate a single engaging crypto tweet (under 280 characters) that:
1. Matches your personality perfectly
2. Is relevant to current crypto trends
3. Uses your signature style and emojis
4. Sounds natural and engaging
5. Includes relevant hashtags

Tweet:"""

        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                temperature=0.8,
                messages=[{"role": "user", "content": prompt}]
            )
            
            tweet_content = response.content[0].text.strip()
            
            # Clean up the response
            if tweet_content.startswith('"') and tweet_content.endswith('"'):
                tweet_content = tweet_content[1:-1]
            
            # Ensure it's under 280 characters
            if len(tweet_content) > 280:
                tweet_content = tweet_content[:277] + "..."
            
            return tweet_content
            
        except Exception as e:
            self.logger.error(f"Failed to generate tweet for {agent_name}: {e}")
            # Fallback tweet
            return f"The crypto markets are looking interesting today! 🚀 #{random.choice(['Bitcoin', 'Crypto', 'DeFi'])}"
    
    async def post_agent_tweet(self, agent_name: str, content: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Generate and post a tweet from an agent"""
        if not self.twitter_client or not self.anthropic_client:
            self.logger.error("Clients not initialized")
            return None
        
        try:
            # Generate content if not provided
            if not content:
                content = await self.generate_agent_tweet(agent_name)
            
            # Rate limiting
            await self._check_rate_limit(agent_name)
            
            # Post to Twitter
            response = self.twitter_client.create_tweet(text=content)
            
            self.last_tweet_time[agent_name] = datetime.now()
            
            if response.data:
                tweet_id = response.data['id']
                tweet_info = {
                    'id': tweet_id,
                    'text': content,
                    'agent_name': agent_name,
                    'created_at': datetime.now().isoformat(),
                    'url': f"https://twitter.com/Rudraps_2005/status/{tweet_id}"
                }
                
                print(f"🤖 {agent_name} → 🐦 X: {content[:50]}...")
                print(f"🔗 {tweet_info['url']}")
                return tweet_info
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to post tweet for {agent_name}: {e}")
            return None
    
    async def _check_rate_limit(self, agent_name: str):
        """Rate limiting between tweets"""
        last_time = self.last_tweet_time.get(agent_name)
        if last_time:
            time_diff = (datetime.now() - last_time).total_seconds()
            if time_diff < self.rate_limit_delay:
                sleep_time = self.rate_limit_delay - time_diff
                print(f"⏰ Rate limiting: waiting {sleep_time:.1f}s...")
                await asyncio.sleep(sleep_time)
    
    async def run_agent_simulation(self, duration_minutes: int = 10, tweets_per_cycle: int = 3):
        """Run a continuous agent simulation posting to X"""
        print(f"🚀 Starting {duration_minutes}-minute agent simulation!")
        print(f"📊 Target: {tweets_per_cycle} tweets per cycle")
        print("=" * 60)
        
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        cycle = 1
        total_tweets = 0
        
        while datetime.now() < end_time:
            print(f"\n🔄 Cycle {cycle} - {datetime.now().strftime('%H:%M:%S')}")
            
            # Select random agents for this cycle
            selected_agents = random.sample(list(self.agent_personas.keys()), 
                                          min(tweets_per_cycle, len(self.agent_personas)))
            
            cycle_tweets = 0
            for agent_name in selected_agents:
                result = await self.post_agent_tweet(agent_name)
                if result:
                    cycle_tweets += 1
                    total_tweets += 1
                
                # Small delay between tweets in same cycle
                await asyncio.sleep(2)
            
            print(f"✅ Cycle {cycle} complete: {cycle_tweets}/{len(selected_agents)} tweets posted")
            
            cycle += 1
            
            # Wait before next cycle (adjust based on desired frequency)
            cycle_delay = 120  # 2 minutes between cycles
            remaining_time = (end_time - datetime.now()).total_seconds()
            
            if remaining_time > cycle_delay:
                print(f"💤 Waiting {cycle_delay}s until next cycle...")
                await asyncio.sleep(cycle_delay)
            elif remaining_time > 0:
                await asyncio.sleep(remaining_time)
            else:
                break
        
        print(f"\n🎉 Simulation Complete!")
        print(f"📊 Total tweets posted: {total_tweets}")
        print(f"🔗 Check your X account: https://twitter.com/Rudraps_2005")


# Quick demo function
async def demo_anthropic_twitter_agents():
    """Demo your Anthropic-powered Twitter agents"""
    print("🤖 ANTHROPIC → X AGENT DEMO")
    print("=" * 40)
    
    agent_system = AnthropicTwitterAgent()
    
    if not await agent_system.initialize():
        print("❌ Failed to initialize agent system")
        return
    
    # Demo each agent type
    agent_names = ['CryptoDegen_Alpha', 'SolanaMaxi_Pro', 'AIAgentAlpha']
    
    print(f"\n🚀 Posting from {len(agent_names)} different agents...")
    
    for i, agent_name in enumerate(agent_names, 1):
        print(f"\n--- Agent {i}/{len(agent_names)}: {agent_name} ---")
        result = await agent_system.post_agent_tweet(agent_name)
        
        if result:
            print(f"✅ Success!")
        else:
            print(f"❌ Failed")
        
        # Wait between agents
        if i < len(agent_names):
            await asyncio.sleep(3)
    
    print(f"\n🎉 Demo complete! Check your X account for the new tweets!")


if __name__ == "__main__":
    print("🕳️ TRENCHES AGENT SYSTEM - X INTEGRATION")
    print("=" * 50)
    print("Choose your option:")
    print("1. Quick Demo (3 tweets from different agents)")
    print("2. Full Simulation (10 minutes of agent activity)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(demo_anthropic_twitter_agents())
    elif choice == "2":
        agent_system = AnthropicTwitterAgent()
        asyncio.run(agent_system.initialize())
        asyncio.run(agent_system.run_agent_simulation(duration_minutes=10, tweets_per_cycle=2))
    else:
        print("Invalid choice. Running quick demo...")
        asyncio.run(demo_anthropic_twitter_agents())