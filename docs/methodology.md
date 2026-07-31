# Methodology

## Idea

Commodities respond to macro conditions with different sensitivities. Energy tracks growth and inventory cycles. Industrial metals track manufacturing activity and the dollar. Precious metals track real rates. Rather than trading each commodity on its own price history, this model builds a composite score from the macro series that drive each complex and ranks across the universe.

## The Central Problem: Data Revisions

This is the one thing that determines whether a macro backtest means anything.

Macro data is revised, often substantially, and often for months after first release. Industrial production for a given month is not final when first published. If a backtest reads today's value of a series at a historical date, it is trading on numbers that did not exist yet, and the results will be excellent and worthless.

The bias is insidious because the code looks completely normal. There is no obvious `shift` missing. The series simply contains better information than was available.

Two defenses, in order of preference:

**1. Vintage data via ALFRED.** Retrieves the series as it stood on a given date, revisions and all. Correct rather than approximate. `FredClient.get_vintage` does this.

**2. Publication lag.** Where vintage data is unavailable, shift each series by its typical release delay. `PUBLICATION_LAG` holds these per series and a test asserts every series used by the model has a declared lag, so a new series cannot be added without one.

## Point-in-Time Standardization

The second place look-ahead enters. A full sample Z-score uses the mean and standard deviation of the entire series, including the future.

Every function in `zscore.py` uses trailing windows only. This is enforced by a test that computes Z-scores on the full series and on a truncated copy and asserts the overlapping values are identical. If any future data leaked in, truncating would change the earlier values.

## Transforms

Most macro series are non-stationary in levels. Standardizing a trending level produces a score that largely measures how far through the sample you are rather than anything about current conditions.

| Transform | When |
|---|---|
| `yoy` | Levels with trend and seasonality: production, employment, CPI |
| `diff` | Levels with trend but no strong seasonality |
| `level` | Already stationary: yields, spreads, breakevens |

Transforms are declared per series in `config/series.yaml` so the configuration behind a published result is version controlled rather than living in a notebook.

## Exposure Mapping

Macro factor scores are projected onto commodities through a fixed exposure matrix. Gold loads negatively on real rates. Copper loads positively on growth. Everything loads negatively on the dollar.

**These signs are a modeling choice, not an estimated result.** They are theory driven and set before any backtest.

Estimating them from the data was considered and rejected. With nine commodities and four factors over a monthly sample, estimated exposures would fit noise, and the model would then be tested on the same data that produced them. Fixed signs are the more honest option, but the sensitivity is real and belongs in any writeup: different defensible sign choices produce different rankings.

## Portfolio Construction

Long the top tercile, short the bottom, dollar neutral. Then scaled toward a 10 percent annualized volatility target.

The scaling matters more than it might appear. Commodity volatility varies enormously across the complex, and natural gas can run several times the volatility of gold. An unscaled book has an energy dominated risk profile no matter what the signal said.

## The Baseline

`strategies/carry.py` implements term structure carry, the best documented commodity signal there is. Backwardated markets have historically outperformed contangoed ones.

The macro model has to beat carry, or at minimum demonstrate it captures something carry does not. Otherwise it is an elaborate way of buying backwardation.

## Limitations

- Publication lags are approximations where vintage data is unavailable. They are typical delays, not actual ones, and actual delays vary.
- Fixed exposure signs are a judgment call, as discussed above.
- Commodities are traded through futures, so roll yield is a large component of returns. Results computed on spot prices do not represent an investable strategy.
- Nine commodities across four factors is a small cross section. The number of independent bets is limited and statistical power is correspondingly weak.
- Macro relationships are regime dependent. The dollar and commodity relationship in particular has not been stable across decades.
