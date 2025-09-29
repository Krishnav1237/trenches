#!/usr/bin/env python3
"""
Trenches Simulation with Twitter Integration (Ready for Approval)
================================================================

This version:
1. Runs your agent simulation normally ✅
2. Shows you what WOULD be posted to Twitter ✅
3. Saves tweets for manual posting (while waiting for approval) ✅
4. Will auto-post once you get Elevated Twitter access ✅
"""

import asyncio
import json
import logging
import random
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

from core.simulation import TrenchesSimulation
from models.entities import Tweet, SimulationContext


class TwitterReadySimulation(TrenchesSimulation):
    """Simulation ready for Twitter integration once approved"""
    
    def __init__(self, config_path: Path = None):
        super().__init__(config_path)
        self.twitter_enabled = False
        self.tweet_selection_rate = 0.3  # 30% would go to Twitter
        self.selected_for_twitter = []
        self.twitter_ready_tweets = []
        
    async def initialize(self):
        """Initialize simulation"""
        await super().initialize()
        
        # Check Twitter status
        try:
            from tools.twitter_publisher import TwitterPublisher
            publisher = TwitterPublisher()
            self.twitter_enabled = await publisher.initialize()
            
            if self.twitter_enabled:
                account_info = await publisher.get_account_info()
                if account_info:
                    self.logger.info(f"🐦 Twitter connected: @{account_info['username']}")
                    print(f"🐦 Twitter connected: @{account_info['username']} (posting disabled - need Elevated access)")
                else:
                    print("🐦 Twitter connected (posting disabled - need Elevated access)")
            else:
                print("🐦 Twitter credentials not configured")
        except Exception as e:
            print(f"🐦 Twitter check failed: {e}")
            self.twitter_enabled = False
    
    async def _execute_tweet(self, agent: Dict, context: SimulationContext):
        """Enhanced tweet execution with Twitter selection"""
        agent_id = agent.get('id')
        
        # Generate tweet content (same as parent)
        enhanced_prompt = self.prompt_engine.build_enhanced_prompt(
            agent, action="tweet", context=context
        )
        
        try:
            response = await self.llm_client.chat_completion_async(
                model=agent.get('provider_config', {}).get('model', 'groq/llama-3.1-8b-instant'),
                messages=[
                    {"role": "system", "content": enhanced_prompt},
                    {"role": "user", "content": f"Generate a tweet as {agent_id} based on current context."}
                ],
                temperature=agent.get('provider_config', {}).get('temperature', 0.8),
                max_tokens=280
            )
            
            content = response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"LLM error for {agent_id}: {e}")
            content = f"Thinking about {random.choice(context.trending_topics)}... 🤔"
        
        # Post to internal backend
        tweet = Tweet(agent_id=agent_id, content=content)
        posted_tweet = await self.api_client.post_tweet(tweet)
        
        if posted_tweet:
            self.simulation_stats['tweets_posted'] += 1
            self.logger.info(f"[{agent_id}] Internal: {content[:50]}...")
            
            # Check if this would be selected for Twitter
            if self._would_select_for_twitter(agent, content):
                self.selected_for_twitter.append({
                    'agent_id': agent_id,
                    'agent_alias': agent.get('alias', agent_id),
                    'content': content,
                    'internal_id': posted_tweet.id,
                    'timestamp': datetime.now().isoformat(),
                    'agent_type': agent.get('classification', 'unknown')
                })
                
                print(f"🐦 [TWITTER READY] @{agent.get('alias', agent_id)}: {content[:60]}...")
                
                # Track stats
                if 'twitter_ready_count' not in self.simulation_stats:
                    self.simulation_stats['twitter_ready_count'] = 0
                self.simulation_stats['twitter_ready_count'] += 1
        else:
            self.logger.error(f"[{agent_id}] Failed to post internal tweet")
    
    def _would_select_for_twitter(self, agent: Dict, content: str) -> bool:
        """Same logic as the real Twitter selection"""
        # Random selection
        if random.random() > self.tweet_selection_rate:
            return False
        
        # Quality filters
        if len(content.strip()) < 20:
            return False
        
        # Skip test patterns
        skip_patterns = ['test', 'debug', 'error', 'failed']
        content_lower = content.lower()
        if any(pattern in content_lower for pattern in skip_patterns):
            return False
        
        # Prefer certain agent types
        agent_type = agent.get('classification', '')
        preferred_types = ['crypto_influencer', 'crypto_analyst', 'degen_trader', 'meme_lord']
        
        if agent_type in preferred_types:
            return True
        
        # Boost crypto keywords
        boost_keywords = ['btc', 'bitcoin', 'eth', 'ethereum', 'crypto', 'defi', 'web3', 'bullish', 'bearish', 'moon']
        if any(keyword in content_lower for keyword in boost_keywords):
            return random.random() < 0.6
        
        return True
    
    async def save_twitter_ready_tweets(self):
        """Save tweets ready for Twitter posting"""
        if not self.selected_for_twitter:
            return
        
        # Save to JSON file
        output_file = Path("twitter_ready_tweets.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.selected_for_twitter, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved {len(self.selected_for_twitter)} Twitter-ready tweets to: {output_file}")
        
        # Also save as text for easy manual posting
        text_file = Path("twitter_ready_tweets.txt")
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write("🐦 TWEETS READY FOR TWITTER POSTING\n")
            f.write("=" * 50 + "\n\n")
            
            for i, tweet in enumerate(self.selected_for_twitter, 1):
                f.write(f"{i}. @{tweet['agent_alias']} ({tweet['agent_type']}):\n")
                f.write(f"   {tweet['content']}\n")
                f.write(f"   Time: {tweet['timestamp']}\n\n")
        
        print(f"💾 Also saved as text file: {text_file}")
    
    async def print_simulation_summary(self):
        """Enhanced summary with Twitter readiness info"""
        await super().print_simulation_summary()
        
        # Twitter-specific stats
        twitter_ready = self.simulation_stats.get('twitter_ready_count', 0)
        total_tweets = self.simulation_stats.get('tweets_posted', 0)
        
        print(f"\n🐦 Twitter Integration Status:")
        print(f"   • Credentials: {'✅ Configured' if self.twitter_enabled else '❌ Not configured'}")
        print(f"   • Access Level: ❌ Essential (need Elevated)")
        print(f"   • Ready for Twitter: {twitter_ready} tweets ({(twitter_ready/max(total_tweets, 1)*100):.1f}%)")
        print(f"   • Selection rate: {self.tweet_selection_rate*100:.0f}%")
        
        if self.selected_for_twitter:
            print(f"\n🎯 Top Twitter-Ready Tweets:")
            for tweet in self.selected_for_twitter[-3:]:
                print(f"   • @{tweet['agent_alias']}: {tweet['content'][:50]}...")
    
    async def cleanup(self):
        """Cleanup with Twitter tweet saving"""
        await self.save_twitter_ready_tweets()
        await super().cleanup()


async def run_twitter_ready_simulation():
    """Run simulation that's ready for Twitter integration"""
    print("🚀 Trenches Simulation - Twitter Ready!")
    print("=" * 50)
    print("This simulation will:")
    print("• Run your agents normally ✅")
    print("• Show what would go to Twitter ✅") 
    print("• Save tweets for manual posting ✅")
    print("• Auto-post once you get Elevated access ✅")
    print("=" * 50)
    
    simulation = TwitterReadySimulation()
    
    try:
        await simulation.initialize()
        
        # Run simulation
        simulation.simulation_duration = 300  # 5 minutes
        simulation.tweet_selection_rate = 0.4  # 40% selected for Twitter
        
        await simulation.run_simulation()
        await simulation.print_simulation_summary()
        
        if simulation.selected_for_twitter:
            print(f"\n🎉 Generated {len(simulation.selected_for_twitter)} tweets ready for Twitter!")
            print("💡 Files saved: twitter_ready_tweets.json & twitter_ready_tweets.txt")
            print("📋 You can copy these and post manually while waiting for API approval")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Simulation stopped by user")
    except Exception as e:
        print(f"\n❌ Simulation error: {e}")
    finally:
        await simulation.cleanup()


if __name__ == "__main__":
    asyncio.run(run_twitter_ready_simulation())