#!/usr/bin/env python3
"""
Enhanced Prompt Engine - Optimized prompts for better memory and context retention.
"""

import time
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from models.entities import SimulationContext, Tweet


@dataclass
class AgentMemory:
    """Agent memory structure for context retention"""
    short_term: List[Dict[str, Any]]
    long_term: List[Dict[str, Any]]
    personality_traits: Dict[str, Any]
    behavioral_patterns: Dict[str, Any]
    social_connections: List[str]
    last_interactions: List[Dict[str, Any]]


class EnhancedPromptEngine:
    """Enhanced prompt generation with memory and context optimization"""
    
    def __init__(self, config_path: Path = None):
        self.config_path = config_path or Path("config")
        self.memory_templates = self._load_memory_templates()
        self.context_analyzers = self._load_context_analyzers()
        self.personality_enhancers = self._load_personality_enhancers()
        
        # Memory management
        self.agent_memories = {}
        self.memory_decay_factor = 0.95
        self.max_short_term_memory = 20
        self.max_long_term_memory = 100

    def _load_memory_templates(self) -> Dict[str, str]:
        """Load memory templates for different contexts"""
        return {
            "memory_context": """
Previous Interactions:
{recent_interactions}

Personality Evolution:
{personality_evolution}

Social Connections:
{social_connections}

Behavioral Patterns:
{behavioral_patterns}
""",
            "context_summary": """
Current Context Summary:
- Trending Topics: {trending_topics}
- Market Sentiment: {market_sentiment}
- Community Activity: {community_activity}
- Recent Events: {recent_events}
- Time Context: {time_context}
""",
            "personality_consistency": """
Your Core Personality Traits:
- Temperament: {temperament}
- Communication Style: {tone}
- Decision Making: {decision_bias}
- Emotional Expression: {emotionality}
- Core Values: {core_values}
- Behavioral Triggers: {triggers}
""",
            "memory_retention": """
Memory Retention Guidelines:
- Remember key interactions with other agents
- Maintain consistent personality traits
- Learn from past experiences
- Adapt behavior based on community feedback
- Preserve important relationships and connections
"""
        }

    def _load_context_analyzers(self) -> Dict[str, Any]:
        """Load context analysis configuration"""
        return {
            "sentiment_analysis": {
                "positive_keywords": ["great", "awesome", "love", "amazing", "wonderful", "excellent", "fantastic", "brilliant", "bullish", "moon", "pump"],
                "negative_keywords": ["terrible", "awful", "hate", "horrible", "disappointing", "failed", "worst", "bad", "bearish", "dump", "crash"],
                "neutral_keywords": ["okay", "fine", "average", "normal", "stable", "steady"]
            },
            "trend_analysis": {
                "crypto_trends": ["DeFi", "NFTs", "Layer 2", "Staking", "Yield Farming", "DAO", "Metaverse", "Web3"],
                "market_trends": ["Bull Market", "Bear Market", "Sideways", "Volatility", "Liquidity", "Volume"],
                "social_trends": ["Viral", "Trending", "Hype", "FOMO", "FUD", "Diamond Hands", "Paper Hands"]
            },
            "interaction_patterns": {
                "engagement_types": ["tweet", "reply", "retweet", "like", "follow", "unfollow"],
                "content_types": ["analysis", "opinion", "news", "meme", "question", "announcement"],
                "emotional_responses": ["excited", "concerned", "skeptical", "optimistic", "pessimistic", "neutral"]
            }
        }

    def _load_personality_enhancers(self) -> Dict[str, Dict[str, str]]:
        """Load personality enhancement templates"""
        return {
            "temperament_enhancements": {
                "analytical": "You approach every situation with data-driven analysis and logical reasoning. You value facts over emotions and prefer evidence-based conclusions.",
                "sarcastic": "You use wit and irony to make your points, often with a dry sense of humor. You're not afraid to call out hypocrisy or absurdity.",
                "optimistic": "You see the positive side of situations and believe in the potential for growth and improvement. You inspire others with your hopeful outlook.",
                "pessimistic": "You consider potential risks and downsides, providing realistic assessments. You help others avoid overconfidence and prepare for challenges.",
                "playful": "You enjoy humor and lighthearted interactions. You bring joy and entertainment to the community while maintaining a fun, engaging presence.",
                "contemplative": "You prefer deep, thoughtful discussions and explore the underlying meanings and implications of topics. You value wisdom and reflection.",
                "neutral": "You maintain a balanced perspective on topics, considering multiple viewpoints before forming opinions. You provide objective analysis.",
                "aggressive": "You're direct and assertive in your communication. You're not afraid to challenge others and stand up for your beliefs.",
                "chill": "You maintain a relaxed, easygoing demeanor. You help others stay calm and focused during stressful situations.",
                "dramatic": "You express yourself with flair and intensity. You're passionate about your beliefs and communicate with emotional depth.",
                "energetic": "You bring enthusiasm and vitality to interactions. You're always ready to engage and inspire others with your energy.",
                "decisive": "You make quick, confident decisions and stick to them. You provide clear direction and leadership when needed.",
                "cheerful": "You maintain an upbeat, positive attitude that uplifts others. You spread joy and optimism in the community."
            },
            "tone_enhancements": {
                "formal": "You communicate in a professional, structured manner with proper grammar and formal language. You maintain a serious, business-like tone.",
                "casual": "You use relaxed, conversational language that feels natural and approachable. You communicate like you're talking to friends.",
                "energetic": "Your communication is vibrant and enthusiastic, with exclamation points and dynamic language that conveys excitement.",
                "calm": "You maintain a peaceful, measured tone that helps others stay centered. You communicate with serenity and composure.",
                "philosophical": "You explore deeper meanings and implications, using thoughtful language that encourages reflection and contemplation.",
                "technical": "You focus on precise, technical communication with accurate terminology and detailed explanations.",
                "witty": "You use clever wordplay and humor to make your points memorable and engaging. You're known for your sharp wit.",
                "cheerful": "You maintain an upbeat, positive tone that spreads happiness and optimism. You're always encouraging and supportive.",
                "edgy": "You communicate with a bold, provocative style that challenges conventional thinking. You're not afraid to be controversial.",
                "academic": "You use scholarly language and approach topics with intellectual rigor. You provide well-researched, authoritative content."
            }
        }

    def build_enhanced_prompt(self, agent: Dict, action_type: str, context: SimulationContext = None, 
                            tool_result: str = None, extra_context: Optional[Dict[str, Any]] = None) -> str:
        """Build enhanced prompt with memory and context optimization"""
        agent_id = agent.get('id', 'Agent')
        personality = agent.get('personality', {})
        
        # Get or create agent memory
        if agent_id not in self.agent_memories:
            self.agent_memories[agent_id] = AgentMemory(
                short_term=[],
                long_term=[],
                personality_traits=personality,
                behavioral_patterns={},
                social_connections=[],
                last_interactions=[]
            )
        
        memory = self.agent_memories[agent_id]
        
        # Build enhanced personality description
        personality_description = self._build_enhanced_personality(agent, memory)
        
        # Build memory context
        memory_context = self._build_memory_context(agent, memory, context)
        
        # Build current context
        current_context = self._build_current_context(agent, context, extra_context)
        
        # Build action-specific instructions
        action_instructions = self._build_action_instructions(agent, action_type, context, tool_result)
        
        # Build memory retention guidelines
        memory_guidelines = self._build_memory_guidelines(agent, memory)
        
        # Assemble final prompt
        prompt = f"""
You are {agent_id}, an AI agent with enhanced memory and context awareness.

{personality_description}

{memory_context}

{current_context}

{action_instructions}

{memory_guidelines}

Your response:
"""
        
        return prompt.strip()

    def _build_enhanced_personality(self, agent: Dict, memory: AgentMemory) -> str:
        """Build enhanced personality description with memory integration"""
        personality = agent.get('personality', {})
        temperament = personality.get('temperament', 'neutral')
        tone = personality.get('tone', 'neutral')
        
        # Get personality enhancements
        temperament_desc = self.personality_enhancers['temperament_enhancements'].get(temperament, "")
        tone_desc = self.personality_enhancers['tone_enhancements'].get(tone, "")
        
        # Build core personality
        personality_parts = [
            f"Core Identity: {agent.get('alias', 'Agent')}",
            f"Classification: {agent.get('classification', 'Unknown')}",
            f"Threat Level: {agent.get('threat_level', 'Gamma')}",
            f"Domain Focus: {agent.get('domain', 'crypto')}",
            f"Posting Style: {agent.get('posting_style', 'general')}",
            f"Social Behavior: {agent.get('social_behavior', 'neutral')}",
            f"Target Assets: {', '.join(agent.get('target_assets', []))}",
            f"Key Skills: {', '.join([skill['name'] for skill in agent.get('skills', [])])}",
            f"Known Weaknesses: {', '.join(agent.get('weaknesses', []))}",
            f"Core Biases: {', '.join(agent.get('biases', []))}",
            f"Catchphrase: {agent.get('catchphrase', '')}",
            f"Origin Story: {agent.get('origin_story', '')}",
            "",
            f"Temperament: {temperament} - {temperament_desc}",
            f"Communication Style: {tone} - {tone_desc}",
            f"Decision Making: {personality.get('decision_bias', 'balanced')}",
            f"Emotional Expression: {personality.get('emotionality', 'medium')}",
            f"Description: {personality.get('description', '')}"
        ]
        
        return "\n".join(personality_parts)

    def _build_memory_context(self, agent: Dict, memory: AgentMemory, context: SimulationContext = None) -> str:
        """Build memory context for the agent"""
        agent_id = agent.get('id', 'Agent')
        
        # Recent interactions
        recent_interactions = []
        for interaction in memory.last_interactions[-5:]:  # Last 5 interactions
            recent_interactions.append(f"- {interaction.get('type', 'unknown')}: {interaction.get('content', '')[:100]}...")
        
        # Personality evolution
        personality_evolution = []
        if memory.behavioral_patterns:
            for pattern, count in memory.behavioral_patterns.items():
                personality_evolution.append(f"- {pattern}: {count} occurrences")
        
        # Social connections
        social_connections = memory.social_connections[:10]  # Top 10 connections
        
        # Behavioral patterns
        behavioral_patterns = []
        for pattern, data in memory.behavioral_patterns.items():
            behavioral_patterns.append(f"- {pattern}: {data}")
        
        return self.memory_templates["memory_context"].format(
            recent_interactions="\n".join(recent_interactions) if recent_interactions else "No recent interactions",
            personality_evolution="\n".join(personality_evolution) if personality_evolution else "No personality evolution data",
            social_connections=", ".join(social_connections) if social_connections else "No social connections",
            behavioral_patterns="\n".join(behavioral_patterns) if behavioral_patterns else "No behavioral patterns"
        )

    def _build_current_context(self, agent: Dict, context: SimulationContext = None, extra_context: Optional[Dict[str, Any]] = None) -> str:
        """Build current context information"""
        if not context:
            return ""
        
        # Extract context information
        trending_topics = getattr(context, 'trending_topics', []) or []
        market_sentiment = getattr(context, 'sentiment', 'neutral')
        community_activity = getattr(context, 'activity_level', 'medium')
        recent_events = getattr(context, 'recent_tweets', []) or []
        time_context = getattr(context, 'time_context', 'unknown')
        
        # Format recent events
        recent_events_str = []
        for tweet in recent_events[:3]:  # Last 3 tweets
            recent_events_str.append(f"- @{tweet.agent_id}: {tweet.content[:100]}...")
        
        return self.memory_templates["context_summary"].format(
            trending_topics=", ".join(trending_topics[:5]) if trending_topics else "None",
            market_sentiment=market_sentiment,
            community_activity=community_activity,
            recent_events="\n".join(recent_events_str) if recent_events_str else "No recent events",
            time_context=time_context
        )

    def _build_action_instructions(self, agent: Dict, action_type: str, context: SimulationContext = None, tool_result: str = None) -> str:
        """Build action-specific instructions"""
        instructions = {
            "tweet": """
Generate an original tweet that reflects your personality and current context. Consider:
- Your core values and beliefs
- Current trending topics and market sentiment
- Your target audience and social connections
- Your posting style and communication preferences
- Recent interactions and community feedback
""",
            "reply": """
Generate a thoughtful reply that adds value to the conversation. Consider:
- The original post's content and context
- Your relationship with the poster
- Your personality and communication style
- How to contribute meaningfully to the discussion
""",
            "retweet": """
Consider whether this content aligns with your values and interests. If so, retweet it with your own commentary.
""",
            "like": """
Consider whether this content resonates with your personality and interests. If so, like it to show support.
"""
        }
        
        base_instruction = instructions.get(action_type, "Take appropriate action based on your personality and context.")
        
        if tool_result:
            return f"""
You previously used a tool and got this result: '{tool_result}'

Now, based on this information and the context, {base_instruction.lower()}
"""
        else:
            return f"""
Based on your personality and the current context, decide your next action. You can either:
1. Generate content directly
2. Use available tools if you need more information

{base_instruction}
"""

    def _build_memory_guidelines(self, agent: Dict, memory: AgentMemory) -> str:
        """Build memory retention guidelines"""
        return self.memory_templates["memory_retention"]

    def update_agent_memory(self, agent_id: str, interaction: Dict[str, Any]):
        """Update agent memory with new interaction"""
        if agent_id not in self.agent_memories:
            self.agent_memories[agent_id] = AgentMemory(
                short_term=[],
                long_term=[],
                personality_traits={},
                behavioral_patterns={},
                social_connections=[],
                last_interactions=[]
            )
        
        memory = self.agent_memories[agent_id]
        
        # Add to short-term memory
        memory.short_term.append({
            "timestamp": time.time(),
            "interaction": interaction,
            "importance": self._calculate_importance(interaction)
        })
        
        # Move important interactions to long-term memory
        for item in memory.short_term[:]:
            if item["importance"] > 0.8:
                memory.long_term.append(item)
                memory.short_term.remove(item)
        
        # Limit memory size
        if len(memory.short_term) > self.max_short_term_memory:
            memory.short_term = memory.short_term[-self.max_short_term_memory:]
        
        if len(memory.long_term) > self.max_long_term_memory:
            memory.long_term = memory.long_term[-self.max_long_term_memory:]
        
        # Update behavioral patterns
        self._update_behavioral_patterns(memory, interaction)
        
        # Update last interactions
        memory.last_interactions.append(interaction)
        if len(memory.last_interactions) > 10:
            memory.last_interactions = memory.last_interactions[-10:]

    def _calculate_importance(self, interaction: Dict[str, Any]) -> float:
        """Calculate importance score for an interaction"""
        importance = 0.0
        
        # Content length
        content = interaction.get('content', '')
        if len(content) > 100:
            importance += 0.2
        
        # Engagement indicators
        if 'likes' in interaction and interaction['likes'] > 5:
            importance += 0.3
        
        if 'retweets' in interaction and interaction['retweets'] > 2:
            importance += 0.3
        
        # Interaction type
        interaction_type = interaction.get('type', '')
        if interaction_type in ['reply', 'retweet']:
            importance += 0.2
        
        return min(importance, 1.0)

    def _update_behavioral_patterns(self, memory: AgentMemory, interaction: Dict[str, Any]):
        """Update behavioral patterns based on interaction"""
        interaction_type = interaction.get('type', '')
        content = interaction.get('content', '')
        
        # Update pattern counts
        if interaction_type not in memory.behavioral_patterns:
            memory.behavioral_patterns[interaction_type] = 0
        memory.behavioral_patterns[interaction_type] += 1
        
        # Analyze content for patterns
        content_lower = content.lower()
        for sentiment, keywords in self.context_analyzers['sentiment_analysis'].items():
            for keyword in keywords:
                if keyword in content_lower:
                    pattern_key = f"{sentiment}_content"
                    if pattern_key not in memory.behavioral_patterns:
                        memory.behavioral_patterns[pattern_key] = 0
                    memory.behavioral_patterns[pattern_key] += 1

    def get_agent_memory_summary(self, agent_id: str) -> Dict[str, Any]:
        """Get summary of agent's memory state"""
        if agent_id not in self.agent_memories:
            return {"error": "Agent memory not found"}
        
        memory = self.agent_memories[agent_id]
        
        return {
            "agent_id": agent_id,
            "short_term_memory_size": len(memory.short_term),
            "long_term_memory_size": len(memory.long_term),
            "behavioral_patterns": memory.behavioral_patterns,
            "social_connections": memory.social_connections,
            "recent_interactions": len(memory.last_interactions),
            "memory_health": "good" if len(memory.short_term) > 5 else "needs_attention"
        }

    def save_agent_memories(self, output_dir: Path):
        """Save agent memories to disk"""
        output_dir.mkdir(exist_ok=True, parents=True)
        
        for agent_id, memory in self.agent_memories.items():
            memory_file = output_dir / f"{agent_id}_memory.yaml"
            memory_data = {
                "agent_id": agent_id,
                "short_term": memory.short_term,
                "long_term": memory.long_term,
                "personality_traits": memory.personality_traits,
                "behavioral_patterns": memory.behavioral_patterns,
                "social_connections": memory.social_connections,
                "last_interactions": memory.last_interactions
            }
            
            with open(memory_file, 'w', encoding='utf-8') as f:
                yaml.dump(memory_data, f, default_flow_style=False, allow_unicode=True)

    def load_agent_memories(self, input_dir: Path):
        """Load agent memories from disk"""
        for memory_file in input_dir.glob("*_memory.yaml"):
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    memory_data = yaml.safe_load(f)

                agent_id = memory_data.get("agent_id")
                if agent_id:
                    self.agent_memories[agent_id] = AgentMemory(
                        short_term=memory_data.get("short_term", []),
                        long_term=memory_data.get("long_term", []),
                        personality_traits=memory_data.get("personality_traits", {}),
                        behavioral_patterns=memory_data.get("behavioral_patterns", {}),
                        social_connections=memory_data.get("social_connections", []),
                        last_interactions=memory_data.get("last_interactions", [])
                    )
            except Exception as e:
                print(f"Failed to load memory file {memory_file}: {e}")

    def analyze_context_from_tweets(self, tweets: List) -> Any:
        """Analyze context from recent tweets (compatible with DynamicPromptEngine interface)"""
        from models.entities import SimulationContext

        context = SimulationContext()

        if not tweets:
            return context

        context.recent_tweets = tweets
        context.trending_tokens = self._extract_trending_topics(tweets)
        context.activity_level = self._calculate_activity_level(tweets)
        context.sentiment = self._analyze_sentiment(tweets)
        context.time_context = self._get_time_context()

        return context

    def _extract_trending_topics(self, tweets: List) -> List[str]:
        """Extract trending topics from recent tweets"""
        word_freq = {}
        stop_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "a", "an", "is", "are", "was", "were"}

        for tweet in tweets:
            content = tweet.content.lower()
            words = [w.strip('.,!?#@') for w in content.split()
                    if len(w) > 3 and w not in stop_words]

            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Return top trending words
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:8] if freq >= 2]

    def _calculate_activity_level(self, tweets: List) -> str:
        """Calculate activity level based on recent tweets"""
        tweet_count = len(tweets)

        if tweet_count >= 10:
            return 'high'
        elif tweet_count >= 5:
            return 'medium'
        elif tweet_count >= 2:
            return 'low'
        else:
            return 'very_low'

    def _analyze_sentiment(self, tweets: List) -> str:
        """Analyze overall sentiment of recent tweets"""
        sentiment_keywords = self.context_analyzers['sentiment_analysis']

        positive_count = 0
        negative_count = 0

        for tweet in tweets:
            content = tweet.content.lower()

            for word in sentiment_keywords['positive_keywords']:
                if word in content:
                    positive_count += 1

            for word in sentiment_keywords['negative_keywords']:
                if word in content:
                    negative_count += 1

        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'

    def _get_time_context(self) -> str:
        """Get time-based context"""
        current_hour = time.localtime().tm_hour

        time_periods = {
            'early_morning': range(5, 9),
            'morning': range(9, 12),
            'afternoon': range(12, 17),
            'evening': range(17, 21),
            'night': range(21, 24),
            'late_night': list(range(0, 5))
        }

        for period, hours in time_periods.items():
            if current_hour in hours:
                return period

        return 'unknown'


def main():
    """Test the enhanced prompt engine"""
    engine = EnhancedPromptEngine()
    
    # Test agent
    test_agent = {
        "id": "test_agent",
        "alias": "Test Agent",
        "classification": "Test Agent",
        "threat_level": "Gamma",
        "domain": "crypto",
        "posting_style": "analytical",
        "social_behavior": "educator",
        "target_assets": ["BTC", "ETH"],
        "skills": [{"name": "Analysis", "description": "Test skill"}],
        "weaknesses": ["Test weakness"],
        "biases": ["Test bias"],
        "catchphrase": "Test catchphrase",
        "origin_story": "Test origin story",
        "personality": {
            "temperament": "analytical",
            "tone": "technical",
            "decision_bias": "logical",
            "emotionality": "low",
            "description": "Test description"
        }
    }
    
    # Test context
    test_context = SimulationContext(
        trending_topics=["BTC", "ETH"],
        activity_level="high",
        sentiment="positive",
        time_context="afternoon"
    )
    
    # Generate prompt
    prompt = engine.build_enhanced_prompt(test_agent, "tweet", test_context)
    print("Enhanced Prompt Generated:")
    print("=" * 50)
    print(prompt)
    print("=" * 50)
    
    # Test memory update
    interaction = {
        "type": "tweet",
        "content": "BTC is looking bullish today!",
        "likes": 10,
        "retweets": 5
    }
    
    engine.update_agent_memory("test_agent", interaction)
    
    # Get memory summary
    memory_summary = engine.get_agent_memory_summary("test_agent")
    print("\nMemory Summary:")
    print(json.dumps(memory_summary, indent=2))


if __name__ == "__main__":
    main()
