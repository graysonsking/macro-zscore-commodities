"""Point-in-time standardization.

A full sample Z-score uses the mean and standard deviation of the entire
series, including the future. It is the most common way look-ahead bias enters
a macro model, and it is easy to miss because the code looks innocuous.

Every function here uses trailing windows only.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# Relative tolerance below which a standard deviation is treated as zero.
#
# Exact equality against 0.0 is not sufficient. A constant series differences
# to a constant whose rolling standard deviation computes to roughly 1e-15
# rather than 0 because of floating point cancellation. Dividing a numerator
# of similar magnitude by that produces order-one values out of a window that
# carries no information at all, which then flow through the pipeline as
# perfectly plausible looking signals.
SD_TOLERANCE = 1e-10


def _safe_sd(sd: pd.Series, scale: pd.Series) -> pd.Series:
    """Mask standard deviations that are zero to within floating point error.

    `scale` sets the reference magnitude so the tolerance is relative rather
    than absolute, since a series measured in millions has different rounding
    behavior than one measured in percent.
    """
    threshold = SD_TOLERANCE * scale.abs().clip(lower=1.0)
    return sd.where(sd > threshold, np.nan)


def rolling_zscore(series: pd.Series, window: int = 60, min_periods: int | None = None) -> pd.Series:
    """Standardize against trailing history only."""
    min_periods = min_periods or window // 2
    mean = series.rolling(window, min_periods=min_periods).mean()
    sd = series.rolling(window, min_periods=min_periods).std(ddof=1)
    return (series - mean) / _safe_sd(sd, mean)


def expanding_zscore(series: pd.Series, min_periods: int = 36) -> pd.Series:
    """Standardize against all history to date.

    Use when the series has a stable long run mean. Rolling is safer when the
    level drifts, since an expanding window anchors to a regime that may no
    longer apply.
    """
    mean = series.expanding(min_periods=min_periods).mean()
    sd = series.expanding(min_periods=min_periods).std(ddof=1)
    return (series - mean) / _safe_sd(sd, mean)


def yoy_change(series: pd.Series, periods: int = 12) -> pd.Series:
    """Year over year change. Removes seasonality and level drift."""
    return series.pct_change(periods)


def diff_zscore(series: pd.Series, window: int = 60, periods: int = 1) -> pd.Series:
    """Z-score of the change rather than the level.

    Many macro series are non-stationary in levels. Standardizing a trending
    level produces a score that mostly measures how far through the sample you
    are. Differencing first fixes that.
    """
    return rolling_zscore(series.diff(periods), window)


def standardize_panel(
    panel: pd.DataFrame,
    window: int = 60,
    transforms: dict[str, str] | None = None,
) -> pd.DataFrame:
    """Standardize every column, applying a per-series transform first.

    transforms maps a column to one of: "level", "diff", "yoy".
    """
    transforms = transforms or {}
    out = {}
    for col in panel.columns:
        how = transforms.get(col, "level")
        if how == "diff":
            out[col] = diff_zscore(panel[col], window)
        elif how == "yoy":
            out[col] = rolling_zscore(yoy_change(panel[col]), window)
        else:
            out[col] = rolling_zscore(panel[col], window)
    return pd.DataFrame(out, index=panel.index)


def winsorize(series: pd.Series, limit: float = 3.0) -> pd.Series:
    """Clip extreme Z-scores.

    A five standard deviation macro print is usually a definitional break or a
    data error rather than five times the signal of a one sigma move.
    """
    return series.clip(-limit, limit)
