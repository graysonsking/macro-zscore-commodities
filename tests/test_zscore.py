"""Tests for point-in-time standardization and signal construction."""

import numpy as np
import pandas as pd
import pytest

from src import fred_client, mapping, signal, zscore


@pytest.fixture
def trending():
    idx = pd.date_range("2000-01-31", periods=240, freq="ME")
    return pd.Series(np.linspace(100, 300, 240), index=idx)


def test_rolling_zscore_uses_no_future_data(trending):
    """Truncating the series must not change earlier Z-scores."""
    full = zscore.rolling_zscore(trending, window=60)
    truncated = zscore.rolling_zscore(trending.iloc[:120], window=60)
    pd.testing.assert_series_equal(full.iloc[:120], truncated, check_freq=False)


def test_expanding_zscore_uses_no_future_data(trending):
    full = zscore.expanding_zscore(trending, min_periods=36)
    truncated = zscore.expanding_zscore(trending.iloc[:120], min_periods=36)
    pd.testing.assert_series_equal(full.iloc[:120], truncated, check_freq=False)


def test_diff_zscore_undefined_on_a_pure_trend(trending):
    """A perfectly linear trend differences to a constant.

    Zero variance means the Z-score is undefined, not zero. Returning NaN is
    the correct behavior. Returning 0.0 would silently assert "this reading is
    exactly average" about a series carrying no information at all.
    """
    assert zscore.diff_zscore(trending, window=60).dropna().empty


def test_diff_zscore_removes_trend_bias():
    """On a noisy trend, differencing centers the score. Levels do not.

    Standardizing a trending level produces a score that mostly measures how
    far through the sample you are. This is the reason transforms exist.
    """
    idx = pd.date_range("2000-01-31", periods=240, freq="ME")
    rng = np.random.default_rng(0)
    s = pd.Series(np.linspace(100, 300, 240) + rng.normal(0, 5, 240), index=idx)

    level_z = zscore.rolling_zscore(s, window=60).dropna()
    diff_z = zscore.diff_zscore(s, window=60).dropna()

    assert abs(diff_z.mean()) < abs(level_z.mean())
    assert abs(diff_z.mean()) < 0.5


def test_winsorize_clips_outliers():
    s = pd.Series([-10.0, 0.0, 10.0])
    assert zscore.winsorize(s, 3.0).tolist() == [-3.0, 0.0, 3.0]


def test_publication_lag_shifts_series():
    idx = pd.date_range("2020-01-31", periods=12, freq="ME")
    panel = pd.DataFrame({"INDPRO": range(12)}, index=idx)
    lagged = fred_client.apply_publication_lag(panel)
    assert pd.isna(lagged["INDPRO"].iloc[0])
    assert lagged["INDPRO"].iloc[1] == 0


def test_every_series_has_a_declared_lag():
    for series_ids in mapping.FACTOR_SERIES.values():
        for sid in series_ids:
            assert sid in fred_client.PUBLICATION_LAG, f"{sid} has no declared lag"


def test_gold_loads_negatively_on_real_rates():
    assert mapping.EXPOSURES["real_rates"]["gold"] < 0


def test_dollar_exposures_are_all_negative():
    assert all(v < 0 for v in mapping.EXPOSURES["dollar"].values())


def test_quantile_weights_are_dollar_neutral():
    s = pd.Series(np.arange(9.0), index=[f"C{i}" for i in range(9)])
    w = signal.quantile_weights(s)
    assert w.sum() == pytest.approx(0.0)
    assert w.abs().sum() == pytest.approx(2.0)


def test_long_only_weights_sum_to_one():
    s = pd.Series(np.arange(9.0), index=[f"C{i}" for i in range(9)])
    assert signal.quantile_weights(s, long_only=True).sum() == pytest.approx(1.0)
