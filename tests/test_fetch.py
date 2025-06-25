import sys
import pathlib
import os
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from fetch_data import (
    get_prices,
    get_vix_front,
    calc_slope,
    get_price_frame,
)
import pandas as pd
import fetch_data


def test_prices_shape():
    df = get_prices()
    assert not df.empty


def test_vix_vals():
    vals = get_vix_front()
    assert all(v > 0 for v in vals)


def test_slope_positive():
    vals = get_vix_front()
    slope = calc_slope()
    if vals[0] > vals[2]:
        assert slope > 0


def test_safe_download_fallback(monkeypatch):
    cache = pathlib.Path(__file__).resolve().parents[1] / "data" / "etf_cache.parquet"
    cache.parent.mkdir(exist_ok=True)
    df = pd.DataFrame({"QQQ": [1], "VIXY": [2], "VIXM": [3]}, index=[pd.Timestamp("2024-01-01")])
    df.to_csv(cache)

    def fail(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(fetch_data, "safe_download", fail)
    got = get_prices()
    assert got.shape == df.shape


def test_interpolate(monkeypatch):
    def fake(*args, **kwargs):
        return pd.DataFrame({"Close": [1]}, index=[pd.Timestamp("2024-01-01")])

    monkeypatch.setattr(fetch_data, "safe_download", fake)
    df = None
    for _ in range(6):
        df = get_price_frame()
    assert df is not None and not df.isna().any().any()


def test_cert_path():
    path = pathlib.Path(os.getenv("SSL_CERT_FILE"))
    assert path.exists()
