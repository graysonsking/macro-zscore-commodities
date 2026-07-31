"""Term structure carry. The baseline comparison.

Carry is the best documented commodity signal there is: backwardated markets
have historically outperformed contangoed ones. Any macro model needs to beat
this, or at minimum show it is capturing something carry does not, otherwise
it is an elaborate way of buying backwardation.
"""

from __future__ import annotations

import pandas as pd

from src import signal

LONG_QUANTILE = 0.33
SHORT_QUANTILE = 0.33


def roll_yield(front: pd.Series, deferred: pd.Series, months_apart: int = 12) -> pd.Series:
    """Annualized roll yield from the futures curve slope.

    Positive means backwardation, the front contract trades above the
    deferred, and a long position earns as it rolls down the curve.
    """
    return (front / deferred - 1.0) * (12.0 / months_apart)


def weights_fn(
    returns: pd.DataFrame,
    date: pd.Timestamp,
    carry_scores: pd.DataFrame | None = None,
    **kwargs,
) -> pd.Series:
    if carry_scores is None:
        raise ValueError("carry score panel required")

    history = carry_scores.loc[carry_scores.index < date]
    if history.empty:
        return pd.Series(0.0, index=returns.columns)

    latest = history.iloc[-1].reindex(returns.columns)
    return signal.quantile_weights(
        latest,
        long_quantile=kwargs.get("long_quantile", LONG_QUANTILE),
        short_quantile=kwargs.get("short_quantile", SHORT_QUANTILE),
    )
