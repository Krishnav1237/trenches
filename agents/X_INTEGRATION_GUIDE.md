# 🐦 X (Twitter) Integration for Trenches Agents

## 📋 Complete Setup Guide

Your Trenches agents can now automatically post to your X (Twitter) account! Here's everything you need to do:

### 1. **Get X API Access**

1. Go to [developer.twitter.com](https://developer.twitter.com)
2. Apply for a Developer Account (free)
3. Create a new App/Project
4. Generate your API credentials:
   - API Key (Consumer Key)
   - API Key Secret (Consumer Secret)
   - Access Token
   - Access Token Secret
   - Bearer Token

⚠️ **Important**: Make sure to set your app permissions to **"Read and Write"** so it can post tweets!

### 2. **Install Dependencies**

```powershell
cd agents
pip install tweepy
```

### 3. **Add API Credentials**

Create or update your `.env` file in the root directory with:

```env
# X (Twitter) API Configuration
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here
```

### 4. **Test the Integration**

```powershell
cd agents
python twitter_setup.py
```

This will:
- ✅ Check your API credentials
- ✅ Test the connection to X
- ✅ Optionally post a test tweet
- ✅ Show your account info

### 5. **Run Enhanced Simulation**

```powershell
cd agents
python enhanced_simulation.py
```

This will:
- 🤖 Run your regular agent simulation
- 🐦 Automatically select ~30% of tweets to publish to X
- 📊 Show you stats on what was published

## ⚙️ **How It Works**

### Smart Tweet Selection
The system automatically selects which tweets to publish to X based on:

- **Quality filters**: Skips test/debug tweets
- **Agent types**: Prefers tweets from influencers, analysts, traders
- **Content boost**: Higher chance for crypto-related content
- **Rate limiting**: Respects X API limits

### Publishing Options

You can control:
- **Selection rate**: What % of tweets go to X (default: 30%)
- **Agent attribution**: Whether to add agent names to tweets
- **Quality filters**: Enable/disable content filtering
- **Rate limiting**: Delay between tweets

### Example Tweet Flow

```
1. Agent generates tweet: "BTC looking bullish! 🚀 This breakout could be huge #Bitcoin"
2. Posted to internal Trenches backend ✅
3. Quality check passes ✅  
4. Selected for X publishing (30% chance) ✅
5. Posted to your X account ✅
6. URL logged: https://twitter.com/yourhandle/status/123456789
```

## 🎛️ **Configuration Options**

Edit `enhanced_simulation.py` to customize:

```python
# Tweet selection rate (0.0 to 1.0)
simulation.tweet_selection_rate = 0.4  # 40% of tweets go to X

# Rate limiting (seconds between tweets)
simulation.twitter_publisher.rate_limit_delay = 2

# Agent attribution
def _add_agent_attribution(self, content: str, agent_id: str) -> str:
    # Option 1: No attribution (default)
    return content
    
    # Option 2: Add hashtag
    # return f"{content} #TrenchesAI"
    
    # Option 3: Add agent signature  
    # return f"{content}\\n\\n- {agent_id}"
```

## 📊 **Monitoring & Stats**

The enhanced simulation shows:
- Total tweets posted to internal backend
- Number published to X
- Publication success rate
- Recent X publications with URLs
- Account stats (followers, etc.)

## 🔧 **Troubleshooting**

### Common Issues:

**❌ "Failed to initialize Twitter API"**
- Check your API credentials in `.env`
- Ensure permissions are "Read and Write"
- Verify your app is approved by X

**❌ "Rate limit exceeded"**
- Increase `rate_limit_delay` in configuration
- Reduce `tweet_selection_rate`
- Wait for rate limit to reset (15 minutes)

**❌ "Forbidden" error**
- Check app permissions (needs Read + Write)
- Verify your developer account is approved
- Ensure access tokens match your account

### Debug Steps:

1. **Test credentials**: `python twitter_setup.py`
2. **Check permissions**: Go to your X Developer Portal
3. **View logs**: Check console output for detailed errors
4. **Manual test**: Try posting a single tweet first

## 🚀 **Advanced Usage**

### Manual Tweet Publishing

```python
from tools.twitter_publisher import publish_to_twitter

# Publish a single tweet
result = await publish_to_twitter(
    agent_id="my_agent",
    content="Manual tweet from my agent! 🤖",
    reply_to_id=None  # Optional: reply to a tweet
)

if result['success']:
    print(f"Published: {result['tweet_info']['url']}")
```

### Custom Selection Logic

Edit `_should_publish_to_twitter()` in `enhanced_simulation.py`:

```python
def _should_publish_to_twitter(self, agent: Dict, content: str) -> bool:
    # Custom logic here
    if "BREAKING" in content.upper():
        return True  # Always publish breaking news
    
    if len(content) > 200:
        return False  # Skip long tweets
    
    return random.random() < 0.3  # 30% chance otherwise
```

## 📈 **Next Steps**

1. **Monitor Performance**: Watch your X engagement metrics
2. **Adjust Settings**: Fine-tune selection rate and filters
3. **Scale Up**: Increase to more agents once stable
4. **Add Features**: Custom hashtags, media uploads, etc.

## 🎯 **Pro Tips**

- Start with a low selection rate (10-20%) to test
- Monitor your X analytics to see what content performs best
- Consider different strategies for different agent types
- Use quality filters to maintain your account's reputation
- Respect X's rate limits to avoid getting banned

---

**🎉 Your agents are now ready to take over X (Twitter)!**

Run `python enhanced_simulation.py` and watch the magic happen! 🚀