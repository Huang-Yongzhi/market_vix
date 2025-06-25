import io
import pathlib
import time
import os, certifi
import pandas as pd
import requests
import yfinance as yf

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

def get_prices(period="3d", interval="5m"):
    """Fetch price data for QQQ, VIXY and VIXM."""

    tickers = ["QQQ", "VIXY", "VIXM"]
    df = None
    for _ in range(3):
        try:          
            df = yf.download(
                tickers,
                interval=interval,
                period=period,
                progress=False,
                threads=False,
            )

            if not df.empty:
                break
        except Exception:
            time.sleep(1)
    if df is None or df.empty:
        path = pathlib.Path(__file__).with_name("sample_prices.csv")
        df = pd.read_csv(path, index_col=0, parse_dates=True)
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
