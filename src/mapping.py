"""Macro factor to commodity exposure mapping.

These signs are theory driven and set before any backtest. They are a modeling
choice, not an estimated result, and different defensible choices produce
different rankings. That sensitivity belongs in any writeup that uses them.

Estimating the exposures from the data instead would be one more thing fitted
on the sample, and with this few commodities and this many macro factors it
would overfit badly.
"""

from __future__ import annotations

import pandas as pd
import yaml

# Sign and magnitude of each commodity's response to a positive move in the factor.
EXPOSURES = {
    "growth": {
        "crude_oil": 0.8, "copper": 1.0, "aluminum": 0.8, "natural_gas": 0.4,
        "gold": -0.3, "silver": 0.1, "corn": 0.2, "wheat": 0.2, "soybeans": 0.2,
    },
    "inflation": {
        "crude_oil": 0.7, "copper": 0.5, "aluminum": 0.4, "natural_gas": 0.5,
        "gold": 0.8, "silver": 0.7, "corn": 0.5, "wheat": 0.5, "soybeans": 0.5,
    },
    "real_rates": {
        "crude_oil": -0.3, "copper": -0.4, "aluminum": -0.3, "natural_gas": -0.2,
        "gold": -1.0, "silver": -0.8, "corn": -0.1, "wheat": -0.1, "soybeans": -0.1,
    },
    "dollar": {
        "crude_oil": -0.7, "copper": -0.8, "aluminum": -0.7, "natural_gas": -0.3,
        "gold": -0.9, "silver": -0.8, "corn": -0.5, "wheat": -0.5, "soybeans": -0.5,
    },
}

# Which FRED series feed each macro factor.
FACTOR_SERIES = {
    "growth": ["INDPRO", "PAYEMS", "DGORDER"],
    "inflation": ["CPIAUCSL", "PPIACO", "T10YIE"],
    "real_rates": ["DFII10"],
    "dollar": ["DTWEXBGS"],
}


def factor_scores(standardized: pd.DataFrame, factor_series: dict | None = None) -> pd.DataFrame:
    """Collapse standardized series into one score per macro factor."""
    factor_series = factor_series or FACTOR_SERIES
    out = {}
    for factor, series_ids in factor_series.items():
        available = [s for s in series_ids if s in standardized.columns]
        if available:
            out[factor] = standardized[available].mean(axis=1)
    return pd.DataFrame(out, index=standardized.index)


def commodity_scores(factors: pd.DataFrame, exposures: dict | None = None) -> pd.DataFrame:
    """Project macro factor scores onto commodities."""
    exposures = exposures or EXPOSURES
    commodities = sorted({c for m in exposures.values() for c in m})

    out = pd.DataFrame(0.0, index=factors.index, columns=commodities)
    for factor, mapping in exposures.items():
        if factor not in factors.columns:
            continue
        for commodity, sign in mapping.items():
            out[commodity] += factors[factor].fillna(0.0) * sign
    return out


def load_config(path: str) -> dict:
    """Load exposures and series mapping from YAML."""
    with open(path) as fh:
        return yaml.safe_load(fh)
