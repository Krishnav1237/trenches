# core/simulation_context.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time


@dataclass
class LiquidityInfo:
    symbol: str
    liquidity_usd: float
    price_usd: float
    source: Optional[str] = None


@dataclass
class WalletSnapshot:
    address: str
    balance_eth: float
    block_number: int


@dataclass
class SimulationContext:
    """Shared context passed to every agent each round."""

    # Trending tokens discovered from news / sources (list of normalized symbols, e.g., ['ETH','BTC'])
    trending_tokens: List[str] = field(default_factory=list)

    # Aggregated news items (list of dicts, source/title/url etc.)
    recent_news: List[Dict[str, Any]] = field(default_factory=list)

    # Liquidity snapshot mapping symbol -> LiquidityInfo
    liquidity_snapshot: Dict[str, LiquidityInfo] = field(default_factory=dict)

    # Recent actions performed by agents in the previous round (list of dicts)
    recent_agent_actions: List[Dict[str, Any]] = field(default_factory=list)

    # Latest on-chain wallet snapshots (for monitored wallets)
    wallet_snapshots: List[WalletSnapshot] = field(default_factory=list)

    # Recent tweets loaded from backend (used for sentiment & topical context)
    recent_tweets: List[Any] = field(default_factory=list)

    # Computed summary fields
    activity_level: Optional[str] = None
    sentiment: Optional[str] = None
    time_context: Optional[str] = None

    # Last updated timestamp
    updated_at: float = field(default_factory=lambda: time.time())

    def update_news(self, news_items: List[Dict[str, Any]]):
        """Replace recent_news with normalized list (flatten if nested)."""
        out: List[Dict[str, Any]] = []
        for item in news_items:
            if isinstance(item, list):
                for sub in item:
                    if isinstance(sub, dict):
                        out.append(sub)
            elif isinstance(item, dict):
                out.append(item)
        self.recent_news = out
        self.updated_at = time.time()

    def update_trending(self, tokens: List[str]):
        """Normalize and set trending tokens (upper-case, unique)"""
        normalized = []
        for t in tokens:
            if not t:
                continue
            s = str(t).upper()
            if s not in normalized:
                normalized.append(s)
        self.trending_tokens = normalized
        self.updated_at = time.time()

    def update_liquidity(self, liquidity_list: List[Dict[str, Any]]):
        """Accepts list of dicts with keys: symbol, liquidity_usd, price_usd, source (optional)."""
        snapshot = {}
        for entry in liquidity_list or []:
            if not isinstance(entry, dict):
                continue
            symbol = str(entry.get("symbol", "")).upper()
            if not symbol:
                continue
            liq_usd = float(entry.get("liquidity_usd", 0) or 0)
            price_usd = float(entry.get("price_usd", 0) or 0)
            snapshot[symbol] = LiquidityInfo(
                symbol=symbol,
                liquidity_usd=liq_usd,
                price_usd=price_usd,
                source=entry.get("source")
            )
        self.liquidity_snapshot = snapshot
        self.updated_at = time.time()

    def add_agent_action(self, agent_action: Dict[str, Any]):
        """Append a recent agent action (tweet, like, retweet, tool call) for other agents to see."""
        if not isinstance(agent_action, dict):
            return
        self.recent_agent_actions.insert(0, agent_action)
        # keep only last N actions
        max_actions = 50
        self.recent_agent_actions = self.recent_agent_actions[:max_actions]
        self.updated_at = time.time()

    def add_wallet_snapshot(self, wallet_snapshot: WalletSnapshot):
        self.wallet_snapshots.insert(0, wallet_snapshot)
        self.wallet_snapshots = self.wallet_snapshots[:20]
        self.updated_at = time.time()

    def set_tweets(self, tweets: List[Any]):
        """Set latest tweets used for sentiment/topic extraction."""
        self.recent_tweets = tweets
        self.updated_at = time.time()
