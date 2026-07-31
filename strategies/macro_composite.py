"""Composite macro score strategy.

Ranks commodities on the projected macro score and takes the top and bottom
tercile. Volatility scaling is applied afterward so the book is not dominated
by energy simply because energy is the most volatile complex.
"""

from __future__ import annotations

import pandas as pd

from src import mapping, signal

LONG_QUANTILE = 0.33
SHORT_QUANTILE = 0.33
TARGET_VOL = 0.10


def weights_fn(
    returns: pd.DataFrame,
    date: pd.Timestamp,
    macro_scores: pd.DataFrame | None = None,
    **kwargs,
) -> pd.Series:
    """Target weights from the macro composite as of `date`.

    macro_scores: commodity level scores over time, already lagged for
        publication delay. Only rows strictly before `date` are read.
    """
    if macro_scores is None:
        raise ValueError("macro score panel required")

    history = macro_scores.loc[macro_scores.index < date]
    if history.empty:
        return pd.Series(0.0, index=returns.columns)

    latest = history.iloc[-1].reindex(returns.columns)
    w = signal.quantile_weights(
        latest,
        long_quantile=kwargs.get("long_quantile", LONG_QUANTILE),
        short_quantile=kwargs.get("short_quantile", SHORT_QUANTILE),
    )
    return signal.volatility_scaled(
        w, returns, target_vol=kwargs.get("target_vol", TARGET_VOL)
    )
