# core/simulation.py

"""Main simulation coordinator for the Trenches agent system."""
import os
import asyncio
import logging
import time
import random
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
import json
import itertools
from datetime import datetime

from models.config import SimulationConfig, LLMConfig
from models.entities import Tweet, ActionType
from core.simulation_context import SimulationContext, LiquidityInfo, WalletSnapshot
from core.api_client import TrenchesAPIClient
from core.enhanced_prompt_engine import EnhancedPromptEngine
from core.action_engine import ActionProbabilityEngine
from core.llm_client import LLMClient
from core.agent_manager import AgentManager

from tools.news_sources import get_aggregated_news, detect_trending_tokens
from tools.dex_screener import get_liquidity_pool_info

# Optional Neo4j integration
try:
    from core.neo4j_service import Neo4jSocialGraph
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    logging.warning("Neo4j driver not installed. Social graph tracking disabled.")  

SYMBOL_NORMALIZATION = {
    "BITCOIN": "BTC",
    "BTC": "BTC",
    "ETHEREUM": "ETH",
    "ETH": "ETH",
    "SOLANA": "SOL",
    "SOL": "SOL",
    "DOGECOIN": "DOGE",
    "DOGE": "DOGE",
    "CARDANO": "ADA",
    "ADA": "ADA",
    "POLKADOT": "DOT",
    "DOT": "DOT",
    "LITECOIN": "LTC",
    "LTC": "LTC",
    "XRP": "XRP",
    "SHIBA": "SHIB",
    "SHIB": "SHIB",
    "PEPE": "PEPE",
    "BNB": "BNB",
    "BLOCKDAG": "BDAG",  
}


class TrenchesSimulation:
    """Main simulation coordinator"""

    def __init__(self, config_path: Path = None):
        if config_path is None:
            config_path = Path("config")
        self.config_path = config_path
        self.config_path.mkdir(exist_ok=True, parents=True)

        self.sim_config = SimulationConfig.from_file(config_path / "simulation.yaml")
        self.llm_config = LLMConfig.from_env_and_file(config_path / "llm.yaml")

        self.agent_manager = AgentManager(config_path)
        self.prompt_engine = EnhancedPromptEngine(config_path)
        self.action_engine = ActionProbabilityEngine(config_path)
        self.llm_client = LLMClient(self.llm_config)
        self.api_client: Optional[TrenchesAPIClient] = None
        self.tools: Dict[str, Callable] = {}

        # Neo4j social graph (optional)
        self.social_graph: Optional[Neo4jSocialGraph] = None
        if NEO4J_AVAILABLE:
            neo4j_enabled = os.getenv('NEO4J_ENABLED', 'true').lower() == 'true'
            if neo4j_enabled:
                self.social_graph = Neo4jSocialGraph()

        self.agents = {}
        self.simulation_stats = {
            'tweets_posted': 0, 'likes_given': 0, 'retweets_made': 0,
            'replies_posted': 0, 'start_time': None, 'end_time': None
        }

        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        logging.basicConfig(
            level=getattr(logging, log_level, logging.INFO),
            format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def register_tools(self, tools: Dict[str, Callable]):
        self.tools = tools
        self.logger.info(f"Registered tools: {list(self.tools.keys())}")

    async def __aenter__(self):
        self.api_client = TrenchesAPIClient(self.sim_config)
        await self.api_client.__aenter__()  # type: ignore
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.api_client:
            await self.api_client.__aexit__(exc_type, exc_val, exc_tb)  # type: ignore

    async def initialize(self):
        """Initialize the simulation"""
        if not self.llm_client.validate_api_key():
            raise ValueError("Invalid or missing Groq API key")
        self.agents = self.agent_manager.load_all_agents()
        if not self.agents:
            raise ValueError("No agents loaded for simulation")
        self.llm_config.discover_models_from_agents(self.agents)
        self.logger.info(f"🤖 Discovered models: {', '.join(self.llm_config.available_models)}")
        if not await self.api_client.health_check():
            self.logger.error(f"Backend unavailable at {self.sim_config.backend_url}")
            self.logger.info("💡 Start the backend with: cd backend && go run main.go")
            raise ConnectionError("Backend not available")
        self.logger.info("Connected to Trenches backend")

        # Initialize Neo4j social graph
        if self.social_graph:
            try:
                if self.social_graph.connect():
                    self.social_graph.initialize_schema()
                    # Register all agents in the graph
                    for agent in self.agents.values():
                        self.social_graph.create_or_update_agent(agent)
                    self.logger.info(f"📊 Neo4j social graph initialized with {len(self.agents)} agents")
                else:
                    self.logger.warning("⚠️ Neo4j connection failed. Social graph tracking disabled.")
                    self.social_graph = None
            except Exception as e:
                self.logger.warning(f"⚠️ Neo4j initialization error: {e}. Social graph tracking disabled.")
                self.social_graph = None

        self.logger.info(f"Simulation initialized with {len(self.agents)} agents")
        await self._ensure_agent_profiles()

    async def _ensure_agent_profiles(self):
        """Ensure all agents have profiles in the backend"""
        existing_profiles = await self.api_client.get_profiles()
        if existing_profiles is None:
            existing_profiles = []
        existing_usernames = {p.username for p in existing_profiles}
        for agent in self.agents.values():
            agent_id = agent.get('id')
            if agent_id not in existing_usernames:
                profile = self.agent_manager.get_agent_profile(agent)
                created_profile = await self.api_client.create_profile(profile)
                if created_profile:
                    self.logger.info(f"Created profile for {agent_id}")
                else:
                    self.logger.warning(f"Failed to create profile for {agent_id}")

    async def analyze_current_context(self) -> SimulationContext:
        """Analyze current context from backend data"""
        recent_tweets = await self.api_client.get_timeline(limit=self.sim_config.context_tweets_limit * 2)
        context = self.prompt_engine.analyze_context_from_tweets(recent_tweets)
        return context

    async def execute_agent_action(self, agent: Dict, action: str, context: SimulationContext):
        """Execute a specific action for an agent"""
        agent_id = agent.get('id')
        self.logger.info(f"[{agent_id}] Executing action: {action}")

        try:
            if action == ActionType.TWEET.value:
                await self._execute_tweet(agent, context)
            elif action == ActionType.LIKE.value:
                await self._execute_like(agent, context)
            elif action == ActionType.RETWEET.value:
                await self._execute_retweet(agent, context)
            elif action == ActionType.REPLY.value:
                await self._execute_reply(agent, context)
            else:
                self.logger.warning(f"[{agent_id}] Unknown action '{action}'")
        except Exception as e:
            self.logger.error(f"[{agent_id}] Failed to execute {action}: {e}", exc_info=True)

    # ----- Internal helpers -----

    def _build_prompt_safe(
        self,
        agent: Dict,
        kind: str,
        context: SimulationContext,
        tool_result: Any = None,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Call prompt_engine.build_enhanced_prompt with full context support.
        EnhancedPromptEngine provides sophisticated memory management and personality consistency.
        """
        return self.prompt_engine.build_enhanced_prompt(
            agent, kind, context, tool_result=tool_result, extra_context=extra_context
        )

    def _normalize_symbol(self, token: str) -> str:
        return SYMBOL_NORMALIZATION.get(token.upper(), token.upper())

    def _extract_token_mentions(self, content: str) -> List[str]:
        """Extract cryptocurrency token mentions from tweet content"""
        tokens = []
        content_upper = content.upper()

        # Check for known tokens
        for token in SYMBOL_NORMALIZATION.keys():
            if token in content_upper or f"${token}" in content_upper:
                normalized = SYMBOL_NORMALIZATION[token]
                if normalized not in tokens:
                    tokens.append(normalized)

        return tokens

    # ----- Actions -----

    async def _execute_tweet(self, agent: Dict, context: SimulationContext):
        """Execute tweet action with a potential tool-use loop."""
        agent_id = agent.get('id')

        prompt = self._build_prompt_safe(
            agent, "tweet", context,
            extra_context={
                "trending_tokens": getattr(context, "trending_tokens", ["BTC"]),
                "liquidity_data": getattr(context, "liquidity_data", {}),
            }
        )
        thought = await self.llm_client.generate_content_async(agent, prompt)

        try:
            tool_call = json.loads(thought)
            tool_name = tool_call.get("tool_name")
            tool_args = tool_call.get("args", {}) if isinstance(tool_call.get("args"), dict) else {}

            # Auto-inject a trending token if LLM forgot the symbol
            if tool_name == "get_token_price" and "symbol" not in tool_args:
                tool_args["symbol"] = random.choice(getattr(context, "trending_tokens", ["BTC"]))

            if tool_name in self.tools:
                self.logger.info(f"[{agent_id}] decided to use tool: {tool_name} with args {tool_args}")
                tool_function = self.tools[tool_name]
                tool_result = tool_function(**tool_args)
                self.logger.info(f"[{agent_id}] got tool result: {tool_result}")

                final_prompt = self._build_prompt_safe(
                    agent, "tweet", context, tool_result=tool_result,
                    extra_context={
                        "trending_tokens": getattr(context, "trending_tokens", ["BTC"]),
                        "liquidity_data": getattr(context, "liquidity_data", {}),
                    }
                )
                content = await self.llm_client.generate_content_async(agent, final_prompt)
            else:
                # Thought was JSON but unknown tool → fallback text
                content = "I was thinking about using a tool, but changed my mind."
        except (json.JSONDecodeError, AttributeError):
            # Not a tool call → treat as final tweet content
            content = thought

        tweet = Tweet(agent_id=agent_id, content=content)
        posted_tweet = await self.api_client.post_tweet(tweet)

        if posted_tweet:
            self.simulation_stats['tweets_posted'] += 1
            self.logger.info(f"[{agent_id}] tweeted: {content[:50]}...")

            # Track successful tweet in memory
            self.prompt_engine.update_agent_memory(agent_id, {
                'type': 'tweet',
                'content': content,
                'timestamp': time.time()
            })

            # Track in Neo4j social graph
            if self.social_graph and posted_tweet.id:
                try:
                    self.social_graph.create_tweet_node({
                        'id': posted_tweet.id,
                        'agent_id': agent_id,
                        'content': content,
                        'timestamp': datetime.now().isoformat(),
                        'sentiment': getattr(context, 'sentiment', 'neutral')
                    })
                    # Extract and link mentioned tokens
                    tokens = self._extract_token_mentions(content)
                    for token in tokens:
                        self.social_graph.link_tweet_to_token(posted_tweet.id, token)
                        sentiment = 'positive' if any(word in content.lower() for word in ['bullish', 'moon', 'pump']) else \
                                  'negative' if any(word in content.lower() for word in ['bearish', 'dump', 'crash']) else 'neutral'
                        self.social_graph.track_agent_sentiment_on_token(agent_id, token, sentiment)
                except Exception as e:
                    self.logger.debug(f"Neo4j tracking error: {e}")
        else:
            self.logger.error(f"[{agent_id}] Failed to post tweet")

    async def _execute_like(self, agent: Dict, context: SimulationContext):
        agent_id = agent.get('id')
        recent_tweets = await self.api_client.get_timeline(limit=5)
        if not recent_tweets:
            return
        other_tweets = [t for t in recent_tweets if t.agent_id != agent_id]
        if not other_tweets:
            return
        tweet_to_like = random.choice(other_tweets)
        success = await self.api_client.like_tweet(tweet_to_like.id)
        if success:
            self.simulation_stats['likes_given'] += 1
            self.logger.info(f"[{agent_id}] liked tweet from @{tweet_to_like.agent_id}")

            # Track like in memory
            self.prompt_engine.update_agent_memory(agent_id, {
                'type': 'like',
                'target_agent': tweet_to_like.agent_id,
                'content': tweet_to_like.content[:100],
                'timestamp': time.time()
            })

            # Track in Neo4j social graph
            if self.social_graph:
                try:
                    self.social_graph.track_like(agent_id, tweet_to_like.id, tweet_to_like.agent_id)
                except Exception as e:
                    self.logger.debug(f"Neo4j tracking error: {e}")

    async def _execute_retweet(self, agent: Dict, context: SimulationContext):
        agent_id = agent.get('id')
        recent_tweets = await self.api_client.get_timeline(limit=5)
        if not recent_tweets:
            return
        other_tweets = [t for t in recent_tweets if t.agent_id != agent_id]
        if not other_tweets:
            return
        tweet_to_retweet = random.choice(other_tweets)
        success = await self.api_client.retweet(tweet_to_retweet.id)
        if success:
            self.simulation_stats['retweets_made'] += 1
            self.logger.info(f"[{agent_id}] retweeted from @{tweet_to_retweet.agent_id}")

            # Track retweet in memory
            self.prompt_engine.update_agent_memory(agent_id, {
                'type': 'retweet',
                'target_agent': tweet_to_retweet.agent_id,
                'content': tweet_to_retweet.content[:100],
                'timestamp': time.time()
            })

            # Track in Neo4j social graph
            if self.social_graph:
                try:
                    self.social_graph.track_retweet(agent_id, tweet_to_retweet.id, tweet_to_retweet.agent_id)
                except Exception as e:
                    self.logger.debug(f"Neo4j tracking error: {e}")

    async def _execute_reply(self, agent: Dict, context: SimulationContext):
        agent_id = agent.get('id')
        recent_tweets = await self.api_client.get_timeline(limit=5)
        if not recent_tweets:
            return
        other_tweets = [t for t in recent_tweets if t.agent_id != agent_id]
        if not other_tweets:
            return
        tweet_to_reply = random.choice(other_tweets)
        reply_prompt = self._build_prompt_safe(
            agent, "reply", context,
            extra_context={
                "trending_tokens": getattr(context, "trending_tokens", ["BTC"]),
                "liquidity_data": getattr(context, "liquidity_data", {}),
                "original_tweet": tweet_to_reply.content
            }
        )
        reply_content = await self.llm_client.generate_content_async(agent, reply_prompt)
        reply = Tweet(agent_id=agent_id, content=reply_content)
        posted_reply = await self.api_client.reply_to_tweet(tweet_to_reply.id, reply)
        if posted_reply:
            self.simulation_stats['replies_posted'] += 1
            self.logger.info(f"[{agent_id}] replied to @{tweet_to_reply.agent_id}")

            # Track reply in memory
            self.prompt_engine.update_agent_memory(agent_id, {
                'type': 'reply',
                'target_agent': tweet_to_reply.agent_id,
                'original_content': tweet_to_reply.content[:100],
                'reply_content': reply_content,
                'timestamp': time.time()
            })

            # Track in Neo4j social graph
            if self.social_graph and posted_reply.id:
                try:
                    # Create the reply tweet node
                    self.social_graph.create_tweet_node({
                        'id': posted_reply.id,
                        'agent_id': agent_id,
                        'content': reply_content,
                        'timestamp': datetime.now().isoformat(),
                        'sentiment': getattr(context, 'sentiment', 'neutral')
                    })
                    # Track the reply relationship
                    self.social_graph.track_reply(agent_id, tweet_to_reply.id, posted_reply.id, tweet_to_reply.agent_id)
                except Exception as e:
                    self.logger.debug(f"Neo4j tracking error: {e}")

    async def simulate_agent(self, agent: Dict, context: SimulationContext):
        agent_id = agent.get('id')
        self.logger.info(f"[{agent_id}] Starting agent simulation")
        
        activity = agent.get('activity', {})
        action_range = activity.get('actions_per_awake', [1, 2])
        num_actions = random.randint(action_range[0], action_range[1])
        
        self.logger.info(f"[{agent_id}] Will perform {num_actions} actions")
        
        for action_num in range(num_actions):
            try:
                action = self.action_engine.select_action(agent, context)
                self.logger.info(f"[{agent_id}] Action {action_num + 1}/{num_actions}: {action}")
                await self.execute_agent_action(agent, action, context)
                
                if num_actions > 1 and action_num < num_actions - 1:
                    delay_range = activity.get('action_delay_range', self.sim_config.agent_delay_range)
                    delay = random.uniform(delay_range[0], delay_range[1])
                    await asyncio.sleep(delay)
            except Exception as e:
                self.logger.error(f"[{agent_id}] Failed action {action_num + 1}: {e}")
                
        self.logger.info(f"[{agent_id}] Completed agent simulation")

    async def _run_onchain_snapshot(self):
        self.logger.info("--- Starting On-chain Snapshot ---")
        wallets_to_watch = [
            "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
            "0xbe0eb53f46cd790cd13851d5eff43d12404d33e8"
        ]
        check_balance_tool = self.tools.get("get_eth_balance")
        if not check_balance_tool:
            self.logger.error("'get_eth_balance' tool not registered. Skipping snapshot.")
            return
        for address in wallets_to_watch:
            result = check_balance_tool(address)
            if result and not result.get("error"):
                await self.api_client.save_wallet_snapshot(
                    address=result["address"],
                    balance=result["balance_eth"],
                    block_number=result["block_number"]
                )
            else:
                self.logger.warning(f"Could not fetch balance for {address}: {result.get('error', 'Unknown error')}")
        self.logger.info("--- On-chain Snapshot Complete ---")

    async def run_simulation_round(self, round_num: int):
        self.logger.info(f"\nRound {round_num + 1}/{self.sim_config.rounds}")

        # 1) News + trending tokens
        news_data, _ = get_aggregated_news(limit=5)
        trending_tokens_raw = detect_trending_tokens(news_data)
        trending_tokens = [self._normalize_symbol(t) for t in trending_tokens_raw] or ["BTC"]
        self.logger.info(f"Trending tokens for this round: {trending_tokens}")

        # 2) On-chain snapshot (unchanged)
        await self._run_onchain_snapshot()

        # 3) Analyze timeline context
        context = await self.analyze_current_context()
        context.trending_tokens = trending_tokens
        context.trending_topics = trending_tokens  # For action engine compatibility

        # 4) Enrich with liquidity data for top trending tokens (limit to avoid rate-limit)
        context.liquidity_data = {}
        for token in trending_tokens[:5]:
            info = get_liquidity_pool_info(symbol=token)
            if info and not info.get("error"):
                context.liquidity_data[token] = info
        if context.liquidity_data:
            pretty = ", ".join(
                f"{sym}: ${int(info['liquidityUsd']):,} liq @ ${info['priceUsd']}"
                for sym, info in context.liquidity_data.items()
                if info.get("liquidityUsd") and info.get("priceUsd")
            )
            if pretty:
                self.logger.info(f"Liquidity snapshot: {pretty}")

        # 5) Select & run agents
        active_agents = self.agent_manager.select_active_agents(
            self.agents, context, self.sim_config.max_concurrent_agents
        )
        self.logger.info(f"{len(active_agents)} agents selected for this round")

        tasks = [self.simulate_agent(agent, context) for agent in active_agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for exceptions in agent execution
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                agent_id = active_agents[i].get('id', f'agent_{i}')
                self.logger.error(f"Agent {agent_id} failed with exception: {result}")

    async def run_simulation(self):
        """Run the complete simulation"""
        self.simulation_stats['start_time'] = time.time()
        try:
            await self.initialize()
            for round_num in range(self.sim_config.rounds):
                await self.run_simulation_round(round_num)
                if round_num < self.sim_config.rounds - 1:
                    delay = random.randint(*self.sim_config.round_delay_range)
                    self.logger.info(f"Waiting {delay}s before next round...")
                    await asyncio.sleep(delay)
            self.simulation_stats['end_time'] = time.time()
            await self._print_final_stats()
        except Exception as e:
            self.logger.error(f"Simulation failed: {e}")
            raise

    async def _print_final_stats(self):
        """Print final simulation statistics"""
        elapsed = self.simulation_stats['end_time'] - self.simulation_stats['start_time']
        self.logger.info("\nSimulation completed!")
        self.logger.info(f"Final Statistics:")
        self.logger.info(f"  • Tweets posted: {self.simulation_stats['tweets_posted']}")
        self.logger.info(f"  • Likes given: {self.simulation_stats['likes_given']}")
        self.logger.info(f"  • Retweets made: {self.simulation_stats['retweets_made']}")
        self.logger.info(f"  • Replies posted: {self.simulation_stats['replies_posted']}")
        self.logger.info(f"  • Total time: {elapsed:.2f} seconds")
        try:
            agent_stats = await self.api_client.get_agent_stats()
            if agent_stats:
                self.logger.info(f"📈 Backend agent stats:")
                for stat in agent_stats[:5]:
                    self.logger.info(f"  • @{stat.agent_id}: {stat.total_likes} likes, {stat.total_retweets} retweets")
        except Exception as e:
            self.logger.warning(f"Failed to get backend stats: {e}")