"""FRED retrieval with vintage awareness.

The single most important thing in this repository.

Macro data is revised, often substantially and often for months after first
publication. Industrial production for a given month is not final when first
released. If a backtest reads today's value of a series at a historical date,
the model is trading on numbers that did not exist yet. This inflates results
dramatically and is invisible unless you look for it.

Two defenses, in order of preference:

1. ALFRED vintage data. Retrieves the series as it stood on a given date,
   revisions and all. This is correct rather than approximate.
2. Publication lag. Where vintage data is unavailable, shift the series by its
   typical release delay. Approximate, but far better than nothing.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

# Months between the reference period and first publication.
PUBLICATION_LAG = {
    "INDPRO": 1,      # Industrial production
    "CPIAUCSL": 1,    # CPI, all urban consumers
    "PPIACO": 1,      # PPI, all commodities
    "UNRATE": 1,      # Unemployment rate
    "PAYEMS": 1,      # Nonfarm payrolls
    "HOUST": 1,       # Housing starts
    "DGORDER": 2,     # Durable goods orders
    "BUSINV": 2,      # Business inventories
    "T10Y2Y": 0,      # Yield curve slope, daily
    "DFII10": 0,      # 10 year TIPS yield, daily
    "T10YIE": 0,      # 10 year breakeven, daily
    "DTWEXBGS": 0,    # Trade weighted dollar, daily
    "DCOILWTICO": 0,  # WTI spot, daily
}


class FredClient:
    """Series retrieval with a local parquet cache."""

    def __init__(self, api_key: str | None = None, cache_dir: str | Path = "cache"):
        self.api_key = api_key or os.environ.get("FRED_API_KEY")
        if not self.api_key:
            raise ValueError("set FRED_API_KEY in the environment")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._client = None

    def _connect(self):
        if self._client is None:
            from fredapi import Fred

            self._client = Fred(api_key=self.api_key)
        return self._client

    def get(self, series_id: str, use_cache: bool = True) -> pd.Series:
        """Latest vintage of a series. Apply a lag before using in a backtest."""
        cache_path = self.cache_dir / f"{series_id}.parquet"
        if use_cache and cache_path.exists():
            return pd.read_parquet(cache_path)[series_id]

        data = self._connect().get_series(series_id)
        data.name = series_id
        data.to_frame().to_parquet(cache_path)
        return data

    def get_vintage(self, series_id: str, vintage_date) -> pd.Series:
        """Series as it stood on `vintage_date`, via ALFRED.

        Prefer this over `get` plus a lag wherever the series supports it.
        """
        data = self._connect().get_series_as_of_date(series_id, vintage_date)
        if isinstance(data, pd.DataFrame):
            data = data.set_index("date")["value"]
        data.name = series_id
        return data

    def get_panel(self, series_ids: list[str], apply_lag: bool = True) -> pd.DataFrame:
        """Assemble several series into a monthly panel.

        apply_lag: shift each series by its publication delay so a backtest
            reading row `t` sees only what was public at `t`. Leave this on
            unless you are supplying vintage data yourself.
        """
        frames = []
        for sid in series_ids:
            s = self.get(sid)
            monthly = s.resample("ME").last()
            if apply_lag:
                monthly = monthly.shift(PUBLICATION_LAG.get(sid, 1))
            frames.append(monthly.rename(sid))
        return pd.concat(frames, axis=1)


def apply_publication_lag(panel: pd.DataFrame, lags: dict[str, int] | None = None) -> pd.DataFrame:
    """Shift each column by its publication delay."""
    lags = lags or PUBLICATION_LAG
    out = panel.copy()
    for col in out.columns:
        out[col] = out[col].shift(lags.get(col, 1))
    return out
