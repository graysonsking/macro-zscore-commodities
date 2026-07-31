# Macro Z-Score Commodities

A cross-sectional commodity signal built from standardized macroeconomic indicators. Each commodity is scored against the macro environment it is most sensitive to, and positions are taken on the resulting ranking.

## Idea

Commodities respond to macro conditions with different sensitivities. Energy tracks growth and inventory cycles. Industrial metals track manufacturing activity and dollar strength. Precious metals track real rates. Rather than trading each on its own price history, this model builds a composite Z-score from the macro series that drive each complex, then ranks across the universe.

## Signal Construction

1. Pull macro series from FRED.
2. Standardize each series against its own trailing history to produce a Z-score, using a rolling window so the standardization is point-in-time.
3. Map series to commodity groups with fixed exposure weights set ex ante.
4. Compute a composite score per commodity.
5. Rank cross-sectionally, go long the top quantile and short the bottom.

## Macro Inputs

| Category | Example series |
|---|---|
| Growth | Industrial production, manufacturing surveys |
| Inflation | CPI, PPI, breakeven rates |
| Rates | Real yields, curve slope |
| Dollar | Trade-weighted dollar index |
| Inventory | Sector-specific stock levels |

Adjust to match the series actually used in `config/series.yaml`.

## Point-in-Time Handling

Macro data is revised. Using the current vintage of a series over a historical backtest gives the model information it could not have had. Where FRED provides vintage data through ALFRED, the release-date vintage is used. Where it does not, the series is lagged by its typical publication delay.

This is the single largest source of overstated performance in macro backtests and it is handled explicitly here.

## Repository Layout

```
macro-zscore-commodities/
|
|-- README.md
|-- LICENSE
|-- .gitignore
|-- requirements.txt
|
|-- src/
|   |-- __init__.py
|   |-- fred_client.py
|   |-- mapping.py
|   |-- signal.py
|   `-- zscore.py
|
|-- strategies/
|   |-- __init__.py
|   |-- carry.py
|   `-- macro_composite.py
|
|-- config/
|   `-- series.yaml
|
|-- docs/
|   |-- methodology.md
|   `-- roadmap.md
|
|-- results/
|   `-- .gitkeep
|
|-- tests/
|   |-- __init__.py
|   `-- test_zscore.py
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export FRED_API_KEY=your_key
```

## Usage

```bash
python -m src.backtest --start 2005-01-01 --end 2025-12-31 --rebalance M
```

## Tests

```bash
python -m pytest tests -q
```

11 tests covering point-in-time standardization, publication lag coverage, and position sizing.

## Results

Populate with your own output.

## Limitations

Fixed exposure weights are a modeling choice, not an estimated result, and different reasonable choices produce different rankings. Publication lags are approximated where vintage data is unavailable. The commodity universe is traded through futures, and roll yield is a material component of returns that must be modeled correctly to interpret the results.

## License

MIT

---

*Research code. Not investment advice.*
