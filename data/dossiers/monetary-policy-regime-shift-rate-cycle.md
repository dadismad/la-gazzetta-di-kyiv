# Liquidity Regime Transition

**Narrative ID**: `monetary_policy_regime_shift_rate_cycle`
**Tickers**: TLT, ^TNX, ^IRX
**Invalidation Threshold**: Fed funds rate < 3.5%

---

## Structural Thesis

The global interest rate structure is not "normalizing" — it is transitioning into a regime that most market participants have never experienced. After 40 years of structurally declining rates (1981-2021), the world has entered an era where fiscal dominance, demographic reversal, and geopolitical fragmentation create persistent upward pressure on the cost of capital.

The key structural insight is the fiscal-monetary collision. Central banks spent 2009-2021 as the sole responders to every economic shock, absorbing sovereign risk onto their balance sheets through quantitative easing. That era is over. In a world of persistent fiscal deficits (US 6%+ of GDP), military Keynesianism, and industrial policy subsidies, central banks cannot simultaneously fight inflation and finance government spending without losing credibility. The market is beginning to price the resulting risk premium into long-duration sovereign debt.

The demographic dimension is equally important. The global savings glut — driven by China's surplus workforce and aging European populations accumulating retirement assets — suppressed real rates for two decades. China's working-age population peaked in 2014. Europe's demographic drag is accelerating. The pool of global savings that bought US Treasuries at 1.5% is shrinking just as the supply of government debt is exploding.

This does not mean rates must go higher linearly. The transition will be volatile — liquidity events, recession scares, and flight-to-safety rallies will create sharp counter-trend moves. But the structural floor on long-duration yields is higher than the market's muscle memory expects. The GAP on this narrative spikes when media covers every Fed pause as a return to the pre-2022 rate regime, while fixed-income positioning data and CFTC bond futures show institutional capital positioning for a structurally higher rate environment.

---

## Key Actors & Tickers

| Actor | Role | Ticker |
|---|---|---|
| 20+ Year Treasury ETF | Long-duration sovereign debt proxy | TLT |
| 10-Year Treasury Yield | Benchmark sovereign rate | ^TNX |
| 13-Week Treasury Yield | Short-term rate / Fed policy proxy | ^IRX |
| 7-10 Year Treasury ETF | Intermediate duration | IEF |

---

## Data Baselines

*Live data injected by build_frontend.py on each pipeline cycle.*

- **FRED**: Fed funds rate, US 10Y-2Y spread, M2 money supply, US fiscal deficit
- **CFTC**: Net positioning on Treasury futures (2Y, 5Y, 10Y, 30Y)
- **Market**: TLT flow data, breakeven inflation rates
- **Contradictions**: Media "Fed pivot" euphoria vs. structural fiscal dominance and persistent deficit spending
