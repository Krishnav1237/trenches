#!/usr/bin/env python3
"""
Enhanced Trenches Simulation with X (Twitter) Integration
=========================================================

This enhanced simulation posts agent tweets to both the internal Trenches backend
AND your actual X (Twitter) account.
"""

import asyncio
import logging
import random
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

from core.simulation import TrenchesSimulation
from models.entities import Tweet, SimulationContext
from tools.twitter_publisher import TwitterPublisher


class EnhancedTrenchesSimulation(TrenchesSimulation):
    """Enhanced simulation with X (Twitter) integration"""
    
    def __init__(self, config_path: Path = None):
        super().__init__(config_path)
        self.twitter_publisher = TwitterPublisher()
        self.twitter_enabled = False
        self.tweet_selection_rate = 0.3  # 30% of tweets go to X
        self.published_tweets = []
        
    async def initialize(self):
        """Initialize the enhanced simulation with Twitter"""
        # Initialize base simulation
        await super().initialize()
        
        # Initialize Twitter publisher
        try:
            self.twitter_enabled = await self.twitter_publisher.initialize()
            if self.twitter_enabled:
                account_info = await self.twitter_publisher.get_account_info()
                if account_info:
                    self.logger.info(f"🐦 Connected to X as @{account_info['username']} ({account_info['followers_count']} followers)")
                else:
                    self.logger.info("🐦 Connected to X (Twitter)")
            else:
                self.logger.warning("🐦 Twitter integration disabled - missing credentials")
        except Exception as e:
            self.logger.error(f"Failed to initialize Twitter: {e}")
            self.twitter_enabled = False
    
    async def _execute_tweet(self, agent: Dict, context: SimulationContext):
        """Enhanced tweet execution with optional Twitter publishing"""
        agent_id = agent.get('id')
        
        # Get the enhanced prompt and generate content (from parent class)
        enhanced_prompt = self.prompt_engine.build_enhanced_prompt(
            agent, action="tweet", context=context
        )
        
        # Generate the tweet content using LLM
        try:
            response = await self.llm_client.chat_completion_async(
                model=agent.get('provider_config', {}).get('model', 'groq/llama-3.1-8b-instant'),
                messages=[
                    {"role": "system", "content": enhanced_prompt},
                    {"role": "user", "content": f"Generate a tweet as {agent_id} based on current context and your personality."}
                ],
                temperature=agent.get('provider_config', {}).get('temperature', 0.8),
                max_tokens=280
            )
            
            thought = response.choices[0].message.content.strip()
            
            # Process tool calls if any (inherited from parent)
            content = await self._process_tool_calls(agent, thought, context)
            
        except Exception as e:
            self.logger.error(f"LLM error for {agent_id}: {e}")
            content = f"Thinking about {random.choice(context.trending_topics)}... 🤔"
        
        # Post to internal backend first
        tweet = Tweet(agent_id=agent_id, content=content)
        posted_tweet = await self.api_client.post_tweet(tweet)
        
        if posted_tweet:
            self.simulation_stats['tweets_posted'] += 1
            self.logger.info(f"[{agent_id}] Internal tweet: {content[:50]}...")
            
            # Decide whether to also publish to X (Twitter)
            if self.twitter_enabled and self._should_publish_to_twitter(agent, content):
                await self._publish_to_twitter(agent_id, content, posted_tweet.id)
        else:
            self.logger.error(f"[{agent_id}] Failed to post internal tweet")
    
    def _should_publish_to_twitter(self, agent: Dict, content: str) -> bool:
        """Determine if tweet should be published to X (Twitter)"""
        # Random selection based on rate
        if random.random() > self.tweet_selection_rate:
            return False
        
        # Quality filters
        # Skip very short tweets
        if len(content.strip()) < 20:
            return False
        
        # Skip tweets with certain patterns you might not want on X
        skip_patterns = [
            'test',
            'debug',
            'error',
            'failed',
            '🧪',  # test emoji
        ]
        
        content_lower = content.lower()
        if any(pattern in content_lower for pattern in skip_patterns):
            return False
        
        # Prefer tweets from certain agent types
        agent_type = agent.get('classification', '')
        preferred_types = ['crypto_influencer', 'crypto_analyst', 'degen_trader', 'meme_lord']
        
        if agent_type in preferred_types:
            return True
        
        # Higher chance for tweets with certain keywords
        boost_keywords = [
            'btc', 'bitcoin', 'eth', 'ethereum', 'crypto', 'defi', 'web3',
            'bullish', 'bearish', 'moon', 'diamond', 'hands', 'hodl'
        ]
        
        if any(keyword in content_lower for keyword in boost_keywords):
            return random.random() < 0.6  # 60% chance for boosted content
        
        return True
    
    async def _publish_to_twitter(self, agent_id: str, content: str, internal_tweet_id: int):
        """Publish tweet to X (Twitter)"""
        try:
            result = await self.twitter_publisher.publish_tweet(agent_id, content)
            
            if result:
                self.published_tweets.append({
                    'agent_id': agent_id,
                    'content': content,
                    'internal_id': internal_tweet_id,
                    'twitter_id': result['id'],
                    'twitter_url': result['url'],
                    'published_at': datetime.now().isoformat()
                })
                
                self.logger.info(f"🐦 [X] {agent_id}: Published to Twitter - {result['url']}")
                
                # Track in stats
                if 'twitter_tweets_published' not in self.simulation_stats:
                    self.simulation_stats['twitter_tweets_published'] = 0
                self.simulation_stats['twitter_tweets_published'] += 1
                
            else:
                self.logger.warning(f"🐦 [X] {agent_id}: Failed to publish to Twitter")
                
        except Exception as e:
            self.logger.error(f"Twitter publishing error for {agent_id}: {e}")
    
    async def _process_tool_calls(self, agent: Dict, thought: str, context: SimulationContext) -> str:
        """Process tool calls and return final content (inherited from parent)"""
        # This is the same logic as in the parent class
        # but we'll keep it simple for now
        try:
            import json
            tool_call = json.loads(thought)
            
            if 'tool' in tool_call and 'action' in tool_call:
                tool_name = tool_call['tool']
                if tool_name in self.available_tools:
                    # Execute tool and return result
                    tool_result = await self.available_tools[tool_name](**tool_call.get('parameters', {}))
                    return f"Just checked {tool_name}: {str(tool_result)[:100]}..."
                else:
                    return "I was thinking about using a tool, but changed my mind."
            else:
                return thought
        except (json.JSONDecodeError, AttributeError):
            return thought
    
    async def get_twitter_stats(self) -> Dict:
        """Get Twitter publishing statistics"""
        if not self.twitter_enabled:
            return {'twitter_enabled': False}
        
        account_info = await self.twitter_publisher.get_account_info()
        
        return {
            'twitter_enabled': True,
            'account_info': account_info,
            'published_tweets_count': len(self.published_tweets),
            'selection_rate': self.tweet_selection_rate,
            'recent_publications': self.published_tweets[-5:] if self.published_tweets else []
        }
    
    async def print_simulation_summary(self):
        """Enhanced simulation summary including Twitter stats"""
        await super().print_simulation_summary()
        
        # Twitter-specific stats
        if self.twitter_enabled:
            twitter_count = self.simulation_stats.get('twitter_tweets_published', 0)
            total_tweets = self.simulation_stats.get('tweets_posted', 0)
            
            print(f"\n🐦 X (Twitter) Integration:")
            print(f"   • Published to X: {twitter_count} tweets")
            print(f"   • Publication rate: {(twitter_count/max(total_tweets, 1)*100):.1f}%")
            
            if self.published_tweets:
                print(f"   • Recent X publications:")
                for pub in self.published_tweets[-3:]:
                    print(f"     - @{pub['agent_id']}: {pub['content'][:40]}...")
                    print(f"       {pub['twitter_url']}")
        else:
            print(f"\n🐦 X (Twitter) Integration: Disabled")


# Updated run script
async def run_enhanced_simulation():
    """Run the enhanced simulation with Twitter integration"""
    print("🚀 Starting Enhanced Trenches Simulation with X Integration")
    print("=" * 60)
    
    # Initialize enhanced simulation
    simulation = EnhancedTrenchesSimulation()
    
    try:
        await simulation.initialize()
        
        # Set simulation parameters
        simulation.simulation_duration = 300  # 5 minutes
        simulation.tweet_selection_rate = 0.4  # 40% of tweets go to X
        
        # Run the simulation
        await simulation.run_simulation()
        
        # Print results
        await simulation.print_simulation_summary()
        
        # Show Twitter-specific stats
        twitter_stats = await simulation.get_twitter_stats()
        if twitter_stats['twitter_enabled']:
            print(f"\n🎯 Twitter Publishing Results:")
            print(f"   Account: @{twitter_stats['account_info']['username']}")
            print(f"   Published: {twitter_stats['published_tweets_count']} tweets")
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Simulation stopped by user")
    except Exception as e:
        print(f"\n❌ Simulation error: {e}")
    finally:
        await simulation.cleanup()


if __name__ == "__main__":
    asyncio.run(run_enhanced_simulation())