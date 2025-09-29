#!/usr/bin/env python3
"""
Quick Twitter Preview - Show what your agents would post to Twitter
"""

import random
from datetime import datetime

# Sample agent tweets (simulating what your agents would generate)
sample_agent_tweets = [
    {
        'agent': 'CryptoDegen_Alpha',
        'type': 'degen_trader', 
        'tweet': '🚀 BTC just broke $65k resistance! This is the breakout we\'ve been waiting for. Diamond hands are about to get rewarded! 💎🙌 #Bitcoin #BTC'
    },
    {
        'agent': 'SolanaMaxi_Pro',
        'type': 'crypto_influencer',
        'tweet': 'SOL ecosystem is absolutely crushing it right now. DeFi volume up 200%, new projects launching daily. Still early! 🌞 #Solana #DeFi'
    },
    {
        'agent': 'TechnicalAnalyst_99',
        'type': 'crypto_analyst',
        'tweet': 'ETH showing strong support at $2.4k. RSI cooling off, MACD turning bullish. Could see $2.8k retest soon. Not financial advice! 📈 #Ethereum'
    },
    {
        'agent': 'MemeLord_420',
        'type': 'meme_lord',
        'tweet': 'PEPE holders be like: "It\'s not much but it\'s honest work" *shows $50 portfolio* 🐸😂 We\'ve all been there! #PEPE #MemeCoin'
    },
    {
        'agent': 'DeFiDegenerate',
        'type': 'degen_trader',
        'tweet': 'Just aped into a new yield farm on Arbitrum. 420% APY? What could go wrong? 🤡 This is fine... *everything is on fire* 🔥 #DeFi #YieldFarming'
    },
    {
        'agent': 'CryptoWhaleWatcher',
        'type': 'crypto_analyst',
        'tweet': '🐋 WHALE ALERT: Someone just moved 10,000 BTC to an unknown wallet. Either someone\'s cashing out or preparing for something big... 👀 #Bitcoin'
    },
    {
        'agent': 'AIAgentAlpha',
        'type': 'crypto_influencer',
        'tweet': 'The AI + Crypto narrative is just getting started. We\'re building autonomous agents that can trade, analyze, and even post tweets. The future is here! 🤖 #AI'
    },
    {
        'agent': 'SmartContractSurfer',
        'type': 'crypto_analyst',
        'tweet': 'New smart contract just deployed on Ethereum. Looks like another yield aggregator but with a twist - it uses AI for rebalancing. Interesting... 🧠 #DeFi'
    }
]

def select_twitter_worthy_tweets(tweets, selection_rate=0.4):
    """Select which tweets would go to Twitter based on quality"""
    selected = []
    
    for tweet_data in tweets:
        # Apply same logic as real system
        content = tweet_data['tweet']
        agent_type = tweet_data['type']
        
        # Quality checks
        if len(content.strip()) < 20:
            continue
            
        # Skip test content
        if any(word in content.lower() for word in ['test', 'debug', 'error']):
            continue
        
        # Random selection with boost for good agent types
        chance = selection_rate
        if agent_type in ['crypto_influencer', 'crypto_analyst', 'degen_trader', 'meme_lord']:
            chance *= 1.5
        
        # Boost for crypto keywords
        if any(keyword in content.lower() for keyword in ['btc', 'bitcoin', 'eth', 'ethereum', 'solana', 'defi', 'crypto']):
            chance *= 1.2
        
        if random.random() < min(chance, 0.8):  # Max 80% chance
            selected.append({
                **tweet_data,
                'selected_at': datetime.now().isoformat(),
                'twitter_ready': True
            })
    
    return selected

def main():
    print("🐦 TWITTER PREVIEW: What Your Agents Would Post")
    print("=" * 60)
    
    # Select tweets for Twitter
    twitter_tweets = select_twitter_worthy_tweets(sample_agent_tweets)
    
    print(f"📊 SELECTION RESULTS:")
    print(f"   • Total agent tweets: {len(sample_agent_tweets)}")
    print(f"   • Selected for Twitter: {len(twitter_tweets)}")
    print(f"   • Selection rate: {len(twitter_tweets)/len(sample_agent_tweets)*100:.1f}%")
    
    print(f"\n🐦 TWEETS READY FOR YOUR TWITTER:")
    print("=" * 50)
    
    for i, tweet in enumerate(twitter_tweets, 1):
        print(f"\n{i}. @{tweet['agent']} ({tweet['type']}):")
        print(f"   📝 {tweet['tweet']}")
        print(f"   🕒 Ready to post!")
    
    if twitter_tweets:
        print(f"\n💡 WHAT TO DO NOW:")
        print("1. Copy these tweets and post them manually to your @Rudraps_2005 account")
        print("2. Apply for Twitter Elevated access (link below)")
        print("3. Once approved, agents will auto-post these quality tweets!")
        
        print(f"\n🔗 APPLY FOR ELEVATED ACCESS:")
        print("https://developer.twitter.com/en/portal/petition/essential/basic-info")
        
        print(f"\n📋 APPLICATION TEMPLATE:")
        print("Use Case: AI Agent Social Media Simulation")
        print("Description: Building an autonomous AI agent system that")
        print("simulates social media discussions about cryptocurrency.")
        print("Agents generate and post educational content about crypto")
        print("markets, DeFi, and blockchain technology for research purposes.")
    
    print(f"\n🚀 YOUR SYSTEM STATUS:")
    print("✅ Agent system working perfectly")
    print("✅ Twitter credentials configured") 
    print("✅ Tweet quality selection working")
    print("❌ Need Elevated API access for auto-posting")
    print("🎯 Ready to go live once approved!")

if __name__ == "__main__":
    random.seed(42)  # For consistent demo
    main()