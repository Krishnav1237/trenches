# agents/tools/dex_screener.py
import httpx
from typing import Any, Dict, List, Optional, Tuple

DEX_SCREENER_BASE = "https://api.dexscreener.com/latest/dex"


def _safe_float(x: Any) -> Optional[float]:
    try:
        return float(x)
    except Exception:
        return None


def search_pair_by_symbol(symbol: str) -> Optional[Tuple[str, str, Dict[str, Any]]]:
    """
    Search by symbol (e.g., 'ETH', 'SOL', 'PEPE') and return the most liquid pair.
    Returns: (pair_address, chain_id, pair_data) or None
    """
    q = symbol.strip()
    if not q:
        return None

    url = f"{DEX_SCREENER_BASE}/search"
    try:
        resp = httpx.get(url, params={"q": q}, timeout=10)
    except Exception:
        return None

    if resp.status_code != 200:
        return None

    data = resp.json() or {}
    pairs: List[Dict[str, Any]] = data.get("pairs") or []
    if not pairs:
        return None

    # Prefer pairs where the base or quote symbol matches exactly
    preferred_quotes = {"USDC", "USDT", "USD", "WETH"}
    candidates = []
    for p in pairs:
        base = (p.get("baseToken") or {}).get("symbol", "")
        quote = (p.get("quoteToken") or {}).get("symbol", "")
        liq_usd = ((p.get("liquidity") or {}).get("usd")) or 0
        liq_usd = _safe_float(liq_usd) or 0.0

        score = liq_usd
        # Slight boost if quote is a stable/major
        if quote in preferred_quotes:
            score *= 1.25
        # Hard preference if symbol matches base or quote
        if base.upper() == q.upper() or quote.upper() == q.upper():
            score *= 1.1

        candidates.append((score, p))

    if not candidates:
        return None

    candidates.sort(key=lambda t: t[0], reverse=True)
    top = candidates[0][1]

    pair_address = top.get("pairAddress")
    chain_id = top.get("chainId") or top.get("chain") or "unknown"
    return pair_address, chain_id, top


def get_liquidity_pool_info(
    symbol: Optional[str] = None,
    pair_address: Optional[str] = None,
    chain: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Fetch liquidity pool info.

    - If `symbol` is provided, finds the most liquid pair for that symbol.
    - If `pair_address` (+ optional `chain`) is provided, fetch that exact pair.

    Returns a dict with keys: symbol, chain, pair, baseToken, quoteToken, priceUsd, liquidityUsd, volume24h
    or {"error": "..."} on failure.
    """
    try:
        if symbol:
            found = search_pair_by_symbol(symbol)
            if not found:
                return {"error": f"No liquidity data found for symbol '{symbol}'"}
            pair_address, chain_id, pair = found
        else:
            if not pair_address:
                return {"error": "Provide either 'symbol' or 'pair_address'."}
            # Fetch explicit pair
            if not chain:
                # Best effort: ethereum by default
                chain = "ethereum"
            url = f"{DEX_SCREENER_BASE}/pairs/{chain}/{pair_address}"
            resp = httpx.get(url, timeout=10)
            if resp.status_code != 200:
                return {"error": f"Failed to fetch pair info: {resp.status_code}"}
            data = resp.json() or {}
            pairs = data.get("pairs") or []
            if not pairs:
                return {"error": "No data found for the requested pair."}
            pair = pairs[0]
            chain_id = pair.get("chainId") or chain

        price_usd = _safe_float(pair.get("priceUsd"))
        liq_usd = _safe_float((pair.get("liquidity") or {}).get("usd"))
        vol_24h = _safe_float((pair.get("volume") or {}).get("h24"))

        return {
            "symbol": symbol or (pair.get("baseToken") or {}).get("symbol"),
            "chain": chain_id,
            "pair": pair.get("pairAddress"),
            "baseToken": (pair.get("baseToken") or {}).get("symbol"),
            "quoteToken": (pair.get("quoteToken") or {}).get("symbol"),
            "priceUsd": price_usd,
            "liquidityUsd": liq_usd,
            "volume24h": vol_24h,
        }
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}


def get_order_book(
    symbol: Optional[str] = None,
    pair_address: Optional[str] = None,
    chain: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Approximate an "order book" using price levels around spot price and liquidity.
    This is a heuristic snapshot for DEX pools (not a true order book).
    """
    info = get_liquidity_pool_info(symbol=symbol, pair_address=pair_address, chain=chain)
    if "error" in info:
        return info

    price = _safe_float(info.get("priceUsd"))
    liq = _safe_float(info.get("liquidityUsd"))
    if not price or not liq:
        return {"error": "Insufficient data to approximate order book."}

    def level(mult: float, frac: float) -> Dict[str, float]:
        return {"price": price * mult, "amount": liq * frac}

    return {
        "symbol": info.get("symbol"),
        "pair": info.get("pair"),
        "bids": [
            level(0.995, 0.05),
            level(0.990, 0.10),
            level(0.980, 0.20),
        ],
        "asks": [
            level(1.005, 0.05),
            level(1.010, 0.10),
            level(1.020, 0.20),
        ],
    }