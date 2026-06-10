# BoneSignal — Market Regime Engine
**A CoinMarketCap AI Skill by Bones HQ (@0x_BoneWalker)**

---

## What This Skill Does

BoneSignal classifies the current crypto market into one of five regimes using four layers of live CoinMarketCap data, then outputs a specific, actionable trading playbook for that regime.

Most trading signals tell you what price is doing. BoneSignal tells you what the **market is doing** — and what to do about it.

---

## The Problem

Generic TA signals (RSI, MACD, Bollinger Bands) are context-blind. A bullish RSI crossover means something completely different in an Accumulation regime vs a Distribution regime. Traders who ignore regime context get wrecked by acting on signals that are technically correct but contextually wrong.

BoneSignal solves this by classifying the regime first, then generating signals and playbooks that are appropriate for that specific regime.

---

## The Four-Layer Architecture

### Layer 1 — Sentiment
**Data:** CMC Fear & Greed Index (live)
**Signal:** Where is retail psychology right now? Extreme fear historically marks bottoms. Extreme greed marks distribution zones.

### Layer 2 — Market Structure
**Data:** CMC Global Metrics (BTC dominance, total market cap, altcoin market cap, stablecoin volume, DeFi volume, derivatives volume)
**Signal:** What is the macro structure of the market? Rising BTC dominance = risk-off rotation. High stablecoin volume = dry powder waiting to deploy. Rising derivatives vs spot = hedging behavior.

### Layer 3 — Momentum
**Data:** CMC Cryptocurrency Listings (top 200, sorted by 24h % change, filtered to $100M+ market cap)
**Signal:** What sectors and assets are actually moving? Filtered to remove low-cap noise and outlier pumps. Real momentum only.

### Layer 4 — Divergence
**Logic:** Where are the layers disagreeing? Extreme fear + high stablecoin volume = potential reversal setup. Rising BTC dominance + falling derivatives = genuine risk-off, not a fake flush. Gainers with high volume + improving sentiment = real rotation beginning.

---

## The Five Regimes

| Regime | Description | Key Characteristics |
|--------|-------------|---------------------|
| **Accumulation** | Smart money loading | Low sentiment, flat price, rising stablecoin reserves |
| **Fear Flush** | Capitulation event | Extreme fear, high volume, derivatives declining |
| **Neutral** | No clear direction | Mixed signals, low conviction across all layers |
| **Distribution** | Smart money exiting | High sentiment, rising BTC dom, derivatives volume spike |
| **Euphoria** | Late cycle danger | Extreme greed, altcoin dominance surging, leverage at peak |

---

## Regime Playbooks

### Accumulation
- **Position:** Start building core positions in BTC and large-cap alts
- **Sizing:** 40-60% deployment, scale in over days not hours
- **Avoid:** Leverage, low-cap plays, chasing momentum
- **Signal to act:** Stablecoin volume declining (dry powder deploying)

### Fear Flush
- **Position:** Identify strongest assets holding support, prepare buy orders
- **Sizing:** 20-30% initial deployment, hold 50-60% for continuation
- **Avoid:** Catching falling knives in weak alts, over-leveraging
- **Signal to act:**

---

---

## Why This Beats Generic TA

| Generic TA Signal | BoneSignal Approach |
|-------------------|---------------------|
| RSI oversold → buy | RSI oversold in Fear Flush → buy. RSI oversold in Distribution → avoid, more downside coming |
| Volume spike → momentum | Volume spike with extreme fear + declining derivatives → capitulation bottom. Volume spike with extreme greed → distribution trap |
| BTC pumping → altseason soon | BTC pumping with rising dominance → risk-off rotation, altseason unlikely. BTC pumping with falling dominance → early altseason signal |

Context changes everything. BoneSignal provides the context.

---

## Data Sources

| Endpoint | Data Used |
|----------|-----------|
| v3/fear-and-greed/latest | Sentiment score and classification |
| v1/global-metrics/quotes/latest | BTC/ETH dominance, market cap, volume flows |
| v1/cryptocurrency/listings/latest | Top movers filtered to $100M+ market cap |

---

## LLM Integration

**Model:** Groq llama-3.3-70b-versatile
**Role:** Synthesizes all four data layers, identifies divergences, classifies regime, generates playbook
**Approach:** Prompted as a CT-native trader with multi-cycle experience — produces plain, direct, actionable output rather than generic financial commentary

---

## Built By

**Bones HQ** — CT-native builder at the intersection of AI, automation, and crypto.
Twitter: [@0x_BoneWalker](https://twitter.com/0x_BoneWalker)
GitHub: [bones-hub](https://github.com/bones-hub)

*Built for the BNB Hack: AI Trading Agent Edition — Track 2, Strategy Skills*
*Powered by CoinMarketCap AI Agent Hub*