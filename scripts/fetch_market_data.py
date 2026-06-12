#!/usr/bin/env python3
"""
fetch_market_data.py — Live Market Data Fetcher (yfinance)

Fetches 24h price change % for configured asset classes.
Computes Asymmetry Score: Narrative Sentiment vs Actual Price Action.
Outputs data/market_prices.json for use by generate_flows.py and the frontend.

Asset mapping from config.yaml asset classes to yfinance tickers.
"""

import json, os, sys, time
from datetime import datetime, timezone
from pathlib import Path

try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance not installed. Run: pip install yfinance")
    sys.exit(1)

PROJECT = Path(__file__).resolve().parent.parent
DATA = PROJECT / "data"

# Asset class → yfinance ticker mapping
TICKER_MAP = {
    "crypto": "BTC-USD",
    "equities": "SPY",
    "commodities": "CL=F",  # WTI Crude
    "fixed_income": "TLT",
    "fx": "UUP",
    "defense": "ITA",
    "tech": "QQQ",
    "gold": "GC=F",
}

def fetch_24h_change(ticker_symbol):
    """Fetch 24h price change percentage for a ticker."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="1d")
        if len(hist) < 2:
            # Try 5d as fallback
            hist = ticker.history(period="5d")
        if len(hist) >= 2:
            close = hist["Close"]
            prev = close.iloc[-2]
            current = close.iloc[-1]
            change_pct = ((current - prev) / prev) * 100
            return {
                "ticker": ticker_symbol,
                "price": round(float(current), 2),
                "change_pct": round(float(change_pct), 2),
                "direction": "up" if change_pct > 0 else "down",
            }
    except Exception as e:
        pass
    return {"ticker": ticker_symbol, "price": None, "change_pct": 0, "direction": "neutral", "error": str(e)[:80]}

def compute_asymmetry_score(narrative_direction, price_direction, narrative_confidence, price_change_pct):
    """
    Asymmetry Score (0-100) — Mathematical Delta Formula v2.0
    
    Score = (NarrativeSentiment [-1 to 1] - PriceActionVelocity [-1 to 1]) * 50
    
    NarrativeSentiment: derived from direction + confidence
      - inflow/bullish → +confidence/100
      - outflow/bearish → -confidence/100
      - neutral → 0
    
    PriceActionVelocity: price change % mapped to [-1, 1] via tanh normalization
      - velocity = tanh(change_pct / 5)  — 5% change ≈ ±0.76, 10% ≈ ±0.96
    
    Interpretation:
      >= 80: MAX ASYMMETRY (massive contradiction — institutional edge)
      >= 60: HIGH ASYMMETRY (significant divergence — trade opportunity)
      >= 40: MODERATE (some misalignment)
      < 40:  LOW (market and narrative aligned)
    """
    import math
    
    # Narrative sentiment: [-1, 1]
    narrative_bullish = narrative_direction in ("inflow", "bullish")
    narrative_bearish = narrative_direction in ("outflow", "bearish")
    conf_factor = max(narrative_confidence, 50) / 100.0  # floor at 0.5
    
    if narrative_bullish:
        narrative_sentiment = conf_factor  # 0.5 to 1.0
    elif narrative_bearish:
        narrative_sentiment = -conf_factor  # -0.5 to -1.0
    else:
        narrative_sentiment = 0.0
    
    # Price action velocity: [-1, 1] using tanh normalization
    # tanh(x/5): 1%→0.20, 2%→0.38, 5%→0.76, 10%→0.96
    price_velocity = math.tanh(price_change_pct / 5.0)
    
    # Raw delta * 50 → 0-100 scale
    raw_score = (narrative_sentiment - price_velocity) * 50
    score = abs(raw_score)  # Absolute value — contradiction magnitude matters
    
    # Cap at 100
    score = min(100, max(0, round(score)))
    
    # Diagnostic trace (for Math Sanity Check)
    diag = {
        "narrative_sentiment": round(narrative_sentiment, 3),
        "price_velocity": round(price_velocity, 3),
        "raw_delta": round(raw_score, 1),
        "formula": f"({'%.2f' % narrative_sentiment} - {'%.2f' % price_velocity}) * 50 = |{'%.1f' % raw_score}| = {score}"
    }
    
    return score, diag

def main():
    print("═══ Market Data Fetcher ═══\n")
    
    prices = {}
    for asset_class, ticker in TICKER_MAP.items():
        data = fetch_24h_change(ticker)
        prices[asset_class] = data
        status = "✓" if data["price"] else "✗"
        price_str = f"${data['price']:.2f}" if data["price"] else "N/A"
        print(f"  {status} {asset_class:15s} ({ticker:8s}) {price_str:>12s} {data['change_pct']:+.1f}%")
    
    # Load flows for asymmetry computation
    flows_path = DATA / "flows.json"
    asymmetry_scores = {}
    
    if flows_path.exists():
        with open(flows_path) as f:
            flows_data = json.load(f)
        
        for flow in flows_data.get("flows", []):
            ac = flow.get("asset_class", "")
            direction = flow.get("direction", "neutral")
            confidence = flow.get("confidence_pct", 50)
            
            price_data = prices.get(ac, {})
            score, diag = compute_asymmetry_score(
                direction,
                price_data.get("direction", "neutral"),
                confidence,
                price_data.get("change_pct", 0)
            )
            asymmetry_scores[flow.get("id", ac)] = {
                "flow_id": flow.get("id", ""),
                "asset_class": ac,
                "narrative_direction": direction,
                "price_direction": price_data.get("direction", "neutral"),
                "price_change_pct": price_data.get("change_pct", 0),
                "asymmetry_score": score,
                "diagnostic_trace": diag,
                "signal": "MAX ASYMMETRY" if score >= 80 else "HIGH ASYMMETRY" if score >= 60 else "MODERATE" if score >= 40 else "LOW ASYMMETRY",
            }
        
        high_count = sum(1 for v in asymmetry_scores.values() if v["asymmetry_score"] >= 60)
        print(f"\n  ⚡ Asymmetry Scores: {high_count} high ({len(asymmetry_scores)} total)")
    
    # Write output
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "prices": prices,
        "asymmetry_scores": asymmetry_scores,
    }
    
    out_path = DATA / "market_prices.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    
    # Also sync to public/data/
    site_data = PROJECT / "site" / "data"
    os.makedirs(str(site_data), exist_ok=True)
    with open(site_data / "market_prices.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✓ Written to {out_path} and public/data/market_prices.json")

if __name__ == "__main__":
    main()
