# Roadmap

## Status

| Component | State |
|---|---|
| FRED client with caching | Complete |
| Publication lag table | Complete, coverage enforced by test |
| Point-in-time Z-scores | Complete, look-ahead tested |
| Series transforms | Complete, tested |
| Factor to commodity exposure mapping | Complete, tested |
| Cross-sectional ranking and sizing | Complete, tested |
| Volatility targeting | Complete |
| Carry baseline | Interface complete, needs curve data |
| ALFRED vintage retrieval | Interface complete, not yet used in the pipeline |
| Backtest harness | In progress |
| Published results | Not started |

## Next

1. **Switch the pipeline to vintage data.** `get_vintage` exists but the panel builder still uses latest vintage plus a lag. Moving to true vintages removes the largest approximation in the methodology.
2. **Source futures curve data.** Required for both the carry baseline and for computing investable returns including roll yield. Spot based results are not a strategy.
3. **Run macro against carry.** The primary comparison, on identical universe and costs.
4. **Exposure sign sensitivity.** Re-run under several defensible exposure matrices and report the dispersion. This is the honest way to handle a parameter that was set by judgment.

## Later

5. **Regime conditioning.** Test whether the signal behaves differently across inflation and rate regimes. Aggregate statistics may be hiding a model that works in one environment only.
6. **Expanded universe.** Nine commodities is a thin cross section. Adding livestock and softs would increase the number of independent bets.
7. **Revision impact study.** Quantify the difference between vintage and latest-vintage results directly. This is a useful exhibit in its own right, since it puts a number on how much a look-ahead a careless implementation would have bought.
