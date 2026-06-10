"""
BoneSignal — Market Regime Engine
Built by Bones HQ (@0x_BoneWalker)

A CMC Skill that classifies the current crypto market regime using
four data layers: sentiment, market structure, momentum, and divergence.
Outputs a clean, actionable signal for traders.
"""

import os
from datetime import datetime, timezone
import requests
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────

CMC_API_KEY = os.getenv("CMC_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

CMC_BASE = "https://pro-api.coinmarketcap.com"
CMC_HEADERS = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
MIN_MARKET_CAP = 100_000_000  # $100M minimum — filters low-cap noise

groq_client = Groq(api_key=GROQ_API_KEY)


# ── Data Fetchers ─────────────────────────────────────────────────────────────

def get_fear_and_greed():
    """Layer 1: Sentiment — Fear & Greed Index"""
    r = requests.get(
        f"{CMC_BASE}/v3/fear-and-greed/latest",
        headers=CMC_HEADERS,
        timeout=10
    )
    r.raise_for_status()
    data = r.json()["data"]
    return {
        "score": data["value"],
        "label": data["value_classification"]
    }


def get_global_metrics():
    """Layer 2: Market Structure — dominance, market cap, volume flows"""
    r = requests.get(
        f"{CMC_BASE}/v1/global-metrics/quotes/latest",
        headers=CMC_HEADERS,
        timeout=10
    )
    r.raise_for_status()
    data = r.json()["data"]
    q = data["quote"]["USD"]
    return {
        "total_market_cap_trillion": round(q["total_market_cap"] / 1e12, 3),
        "total_volume_24h_billion": round(q["total_volume_24h"] / 1e9, 2),
        "btc_dominance": round(data["btc_dominance"], 2),
        "eth_dominance": round(data["eth_dominance"], 2),
        "altcoin_market_cap_billion": round(q["altcoin_market_cap"] / 1e9, 2),
        "defi_volume_24h_change_pct": round(q["defi_24h_percentage_change"], 2),
        "derivatives_volume_24h_change_pct": round(q["derivatives_24h_percentage_change"], 2),
        "stablecoin_volume_24h_billion": round(q["stablecoin_volume_24h"] / 1e9, 2),
        "market_cap_24h_change_pct": round(q["total_market_cap_yesterday_percentage_change"], 2),
    }


def get_top_movers():
    """Layer 3: Momentum — gainers and losers filtered above $100M market cap"""

    def fetch_listings(sort_dir):
        r = requests.get(
            f"{CMC_BASE}/v1/cryptocurrency/listings/latest",
            headers=CMC_HEADERS,
            params={"limit": 200, "sort": "percent_change_24h", "sort_dir": sort_dir},
            timeout=10
        )
        r.raise_for_status()
        return r.json()["data"]

    def format_coin(coin):
        q = coin["quote"]["USD"]
        return {
            "symbol": coin["symbol"],
            "name": coin["name"],
            "price_usd": round(q["price"], 4),
            "change_24h_pct": round(q["percent_change_24h"], 2),
            "volume_24h_million": round(q["volume_24h"] / 1e6, 2),
            "market_cap_billion": round(q["market_cap"] / 1e9, 3),
        }

    def filter_and_format(coins, limit=5):
        filtered = [
            c for c in coins
            if c["quote"]["USD"]["market_cap"] >= MIN_MARKET_CAP
            and abs(c["quote"]["USD"]["percent_change_24h"]) < 500  # remove obvious outliers
        ]
        return [format_coin(c) for c in filtered[:limit]]

    gainers = filter_and_format(fetch_listings("desc"))
    losers = filter_and_format(fetch_listings("asc"))

    return {"top_gainers": gainers, "top_losers": losers}


# ── Regime Classifier ─────────────────────────────────────────────────────────

def classify_regime(fear_greed, global_metrics, movers):
    """Layer 4: Divergence — LLM synthesizes all layers into a regime signal"""

    gainers_text = "\n".join([
        f"  {c['symbol']} ({c['name']}): +{c['change_24h_pct']}% | "
        f"Vol ${c['volume_24h_million']}M | MCap ${c['market_cap_billion']}B"
        for c in movers["top_gainers"]
    ]) or "  No significant gainers above $100M market cap"

    losers_text = "\n".join([
        f"  {c['symbol']} ({c['name']}): {c['change_24h_pct']}% | "
        f"Vol ${c['volume_24h_million']}M | MCap ${c['market_cap_billion']}B"
        for c in movers["top_losers"]
    ]) or "  No significant losers above $100M market cap"

    prompt = f"""You are BoneSignal — a crypto market regime classifier built by Bones HQ (@0x_BoneWalker).

You are a CT-native trader who has survived multiple cycles: the 2022 Luna collapse, the FTX implosion, the 2024 ETF euphoria, and the 2025 altcoin wipeout. You've watched people get wrecked by ignoring regime context and you've watched others print by reading it correctly.

Your job: synthesize four layers of live market data into one sharp, honest regime signal. You speak plainly. You have a view and you state it. No corporate finance speak. No "on the other hand." No hedging. Sound like the smartest degen in the room who also actually understands macro flows.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LIVE MARKET DATA — {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LAYER 1 — SENTIMENT
  Fear & Greed: {fear_greed['score']}/100 ({fear_greed['label']})

LAYER 2 — MARKET STRUCTURE
  Total Market Cap:       ${global_metrics['total_market_cap_trillion']}T ({global_metrics['market_cap_24h_change_pct']}% 24h)
  24h Spot Volume:        ${global_metrics['total_volume_24h_billion']}B
  BTC Dominance:          {global_metrics['btc_dominance']}%
  ETH Dominance:          {global_metrics['eth_dominance']}%
  Altcoin Market Cap:     ${global_metrics['altcoin_market_cap_billion']}B
  Stablecoin Volume 24h:  ${global_metrics['stablecoin_volume_24h_billion']}B
  DeFi Volume 24h Change: {global_metrics['defi_volume_24h_change_pct']}%
  Derivatives 24h Change: {global_metrics['derivatives_volume_24h_change_pct']}%

LAYER 3 — MOMENTUM (coins above $100M market cap only)
  Top Gainers 24h:
{gainers_text}

  Top Losers 24h:
{losers_text}

LAYER 4 — DIVERGENCE (analyze these relationships)
  • Sentiment vs price action — are they aligned or diverging?
  • BTC dominance direction — risk-off (rising) or risk-on (falling)?
  • Derivatives vs spot volume ratio — hedging or speculation?
  • Stablecoin volume — dry powder sitting or actively deploying?
  • Gainer/loser quality — real sector rotation or random noise?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESPOND ONLY IN THIS EXACT FORMAT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REGIME: [Accumulation | Distribution | Euphoria | Fear Flush | Neutral]

CONFIDENCE: [Low | Medium | High]

MARKET READ:
[2-3 sentences max. What is actually happening right now. Name specific numbers from the data. No vague language.]

KEY SIGNALS:
- [The single most telling data point and what it means]
- [Second signal — focus on any divergence between layers]
- [Third signal — what the smart money flow looks like]

PLAYBOOK:
[Concrete moves. Name specific asset categories or sectors. Give a sizing approach — how much to deploy vs hold back. State the exact condition that triggers action vs staying out. Write like you have real money on the line.]

RISK LEVEL: [Low | Medium | High | Extreme]

BONES HQ VERDICT:
[One sentence. Raw and direct. The kind of take you'd post on CT at 2am that gets 500 likes because you said what everyone was thinking but nobody had the guts to say clearly.]
"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.25,
        max_tokens=900
    )

    return response.choices[0].message.content


# ── Output ────────────────────────────────────────────────────────────────────

def save_output(output, fear_greed, global_metrics):
    """Save signal to a timestamped file"""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    filename = f"signal_{timestamp}.txt"

    content = f"""
╔══════════════════════════════════════════════════════════╗
║           BONES SIGNAL — MARKET REGIME ENGINE            ║
║                  by Bones HQ @0x_BoneWalker              ║
╚══════════════════════════════════════════════════════════╝

Generated:     {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}
Fear & Greed:  {fear_greed['score']}/100 — {fear_greed['label']}
Market Cap:    ${global_metrics['total_market_cap_trillion']}T
BTC Dom:       {global_metrics['btc_dominance']}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{output}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    return filename


# ── Main ──────────────────────────────────────────────────────────────────────

def run():
    print("\n🦴 BONES SIGNAL — Market Regime Engine")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    try:
        print("📡 Fetching Layer 1 — Sentiment...")
        fear_greed = get_fear_and_greed()
        print(f"   Fear & Greed: {fear_greed['score']}/100 ({fear_greed['label']})")

        print("📡 Fetching Layer 2 — Market Structure...")
        global_metrics = get_global_metrics()
        print(f"   BTC Dom: {global_metrics['btc_dominance']}% | Market Cap: ${global_metrics['total_market_cap_trillion']}T")

        print("📡 Fetching Layer 3 — Momentum...")
        movers = get_top_movers()
        if movers["top_gainers"]:
            print(f"   Top gainer: {movers['top_gainers'][0]['symbol']} +{movers['top_gainers'][0]['change_24h_pct']}%")
        if movers["top_losers"]:
            print(f"   Top loser:  {movers['top_losers'][0]['symbol']} {movers['top_losers'][0]['change_24h_pct']}%")

        print("\n🧠 Running regime classification...\n")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

        result = classify_regime(fear_greed, global_metrics, movers)
        print(result)

        filename = save_output(result, fear_greed, global_metrics)
        print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"✅ Signal saved to: {filename}")

    except requests.exceptions.RequestException as e:
        print(f"❌ API error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    run()