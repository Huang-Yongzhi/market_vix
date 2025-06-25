import io
import pathlib
import time
import os
import certifi
from pathlib import Path
import shutil
import logging
import itertools

cert_file = certifi.where()
if " " in cert_file or any(ord(ch) > 127 for ch in cert_file):
    short = str(Path(cert_file).with_name("cacert.pem"))
    if not Path(short).exists():
        shutil.copy(cert_file, short)
    logging.getLogger(__name__).warning("Copied cert file to %s", short)
    cert_file = short

os.environ.setdefault("SSL_CERT_FILE", cert_file)
os.environ.setdefault("REQUESTS_CA_BUNDLE", cert_file)

import pandas as pd
import requests
import yfinance as yf

cycle_iter = itertools.cycle(["QQQ", "VIXY", "VIXM"])
price_df = pd.DataFrame(columns=["QQQ", "VIXY", "VIXM"], dtype=float)


def safe_download(tickers, period="3d", interval="5m"):
    """Download quotes with retry and backoff."""
    last_err = None
    for delay in (2, 4, 8):
        try:
            df = yf.download(
                tickers,
                interval=interval,
                period=period,
                progress=False,
                threads=False,
                auto_adjust=False,
                timeout=10,
            )
            if not df.empty:
                return df
        except Exception as err:
            last_err = err
        time.sleep(delay)
    raise RuntimeError("download failed") from last_err

def get_prices(period="3d", interval="5m"):
    """Fetch price data for QQQ, VIXY and VIXM."""

    tickers = ["QQQ", "VIXY", "VIXM"]
    cache = pathlib.Path(__file__).resolve().parent / "data" / "etf_cache.parquet"

    try:
        df = safe_download(tickers, period=period, interval=interval)
        cache.parent.mkdir(parents=True, exist_ok=True)
        try:
            df.to_parquet(cache)
        except Exception:
            df.to_csv(cache)
    except RuntimeError:
        if cache.exists():
            try:
                df = pd.read_parquet(cache)
            except Exception:
                df = pd.read_csv(cache, index_col=0, parse_dates=True)
        else:
            raise

    return df


def fetch_next_etf(period="3d", interval="5m"):
    """Download one ETF in rotation and store last price."""
    global price_df
    etf = next(cycle_iter)

    try:
        df = safe_download(etf, period=period, interval=interval)
        close = (
            df["Close"][etf].iloc[-1]
            if isinstance(df.columns, pd.MultiIndex)
            else df["Close"].iloc[-1]
        )
    except RuntimeError:
        cache = pathlib.Path(__file__).resolve().parent / "data" / "etf_cache.parquet"
        if cache.exists():
            cached = pd.read_parquet(cache)
            close = cached[etf].iloc[-1]
        else:
            return
    now = pd.Timestamp.now()
    price_df.loc[now, etf] = close
    cutoff = now - pd.Timedelta(minutes=200)
    price_df = price_df.loc[price_df.index >= cutoff]



def get_price_frame(period="3d", interval="5m"):
    """Return interpolated price DataFrame."""
    fetch_next_etf(period=period, interval=interval)
    df = price_df.sort_index().interpolate(method="time")
    df = df.ffill().bfill()
    return df


def get_vix_front():
    """Return first three settle values from VIX futures."""
    url = "https://cdn.cboe.com/pub/historicalfutures/vix/current_contract.csv"
    text = None
    for _ in range(3):
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            text = r.text
            break
        except requests.RequestException:
            time.sleep(1)
    if text is None:
        data_path = pathlib.Path(__file__).with_name("sample_vix.csv")
        text = data_path.read_text(encoding="utf-8")
    df = pd.read_csv(io.StringIO(text))
    return df["SETTLE"].iloc[:3]


def calc_slope():
    """Calculate VIX term structure slope using front contracts."""
    v1, v2, v3 = get_vix_front()
    slope = (v1 - v3) / v3
    return round(slope, 4)
