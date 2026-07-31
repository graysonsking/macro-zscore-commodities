"""Cross-sectional ranking and position sizing."""

from __future__ import annotations

import numpy as np
import pandas as pd


def cross_sectional_rank(scores: pd.Series) -> pd.Series:
    """Percentile rank within the cross section."""
    return scores.rank(pct=True)


def quantile_weights(
    scores: pd.Series,
    long_quantile: float = 0.33,
    short_quantile: float = 0.33,
    long_only: bool = False,
) -> pd.Series:
    """Long the top quantile, short the bottom, dollar neutral."""
    s = scores.dropna()
    w = pd.Series(0.0, index=scores.index)
    if len(s) < 3:
        return w

    n_long = max(1, int(len(s) * long_quantile))
    w[s.nlargest(n_long).index] = 1.0 / n_long

    if not long_only and short_quantile > 0:
        n_short = max(1, int(len(s) * short_quantile))
        w[s.nsmallest(n_short).index] = -1.0 / n_short

    return w


def volatility_scaled(
    weights: pd.Series,
    returns: pd.DataFrame,
    target_vol: float = 0.10,
    lookback: int = 36,
    max_leverage: float = 2.0,
) -> pd.Series:
    """Scale a weight vector toward a target portfolio volatility.

    Commodity volatility varies enormously across the complex and across time.
    An unscaled book has an energy dominated risk profile regardless of what
    the signal said.
    """
    cols = [c for c in weights.index if c in returns.columns]
    if not cols:
        return weights

    cov = returns[cols].tail(lookback).cov()
    w = weights[cols].values
    realized = float(np.sqrt(max(w @ cov.values @ w, 0.0)) * np.sqrt(12))
    if realized <= 0:
        return weights

    return weights * min(target_vol / realized, max_leverage)
