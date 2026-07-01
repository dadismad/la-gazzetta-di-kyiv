# Crypto Representation Audit — June 2026

## Proven Persona Combination
- **Crypto Market Structure Analyst (Tier 1 exchange: Binance/Coinbase/Kraken)**
- **Crypto-Native UX Designer (DeFi protocols, crypto exchanges)**

## Key Findings

### Coverage Gaps
- 5/23 stories are crypto (22%) — triple-counted Zcash/Monero inflates coverage
- Zero dedicated crypto flows in sector_summary — crypto buried under "tech" or "commodities"
- 7 anchor assets (BTC/ETH/SOL/XRP/BNB/ADA/DOGE) but only BTC has a trade idea
- 2 crypto flow nodes with labeling bug (both show "Crypto → crypto")

### Missing Data
- Stablecoin flows (USDT/USDC mint/burn) — the on-chain equivalent of FX flows
- BTC/ETH ETF daily netflows — biggest institutional crypto signal
- DeFi TVL trends (Aave, Maker, Lido)
- On-chain exchange netflows (CEX cold/hot wallet movements)
- No on-chain verification links ("Verify on Etherscan")

### Ticker Format
- BTC-USD → should be BTC (crypto-native format)
- Horizon page uses Yahoo Finance format (BTC-USD) — wrong

### UX Disconnect
- Light-themed main site vs dark-themed Flow Nodes (feels like different products)
- No data provenance badges for crypto metrics
- Stablecoin supply ($172B) and exchange netflow (-$890M) on trades page — NOT SOURCED

### Recommended Data Sources (free tier available)
- Glassnode API: exchange inflows/outflows, miner flows, stablecoin supply
- CoinGecko API: price, volume, market cap
- Dune Analytics: DeFi TVL, DEX volumes (public dashboards, SQL queries)
- SoSoValue: Spot BTC/ETH ETF daily flows

### Integration Priority
1. Dedicated crypto sector page with on-chain data
2. Fix ticker format (BTC-USD → BTC)
3. Add ETH, SOL trade ideas
4. On-chain verification links + data provenance badges
5. Merge triple-counted Zcash/Monero story
