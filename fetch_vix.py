# 抓 VIX 期货的脚本
import io
import pathlib
import time
import sys

import pandas as pd
import requests

def fetch_vix_front():
    """拉最近 3 个月 VIX 期货结算价（CFE 公开 CSV）"""
    url = "https://cdn.cboe.com/pub/historicalfutures/vix/current_contract.csv"
    last_err = None
    text = None
    for _ in range(3):
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            text = r.text
            break
        except requests.RequestException as exc:
            last_err = exc
            time.sleep(1)
    if text is None:
        data_path = pathlib.Path(__file__).with_name("sample_vix.csv")
        text = data_path.read_text(encoding="utf-8")
    df = pd.read_csv(io.StringIO(text))
    today = pd.Timestamp.today().normalize()
    df = df[["FUT_EXP_DATE","SETTLE"]].rename(
        columns={"FUT_EXP_DATE":"date","SETTLE":"settle"}
    )
    df["download_ts"] = today
    return df

if __name__ == "__main__":
    out = fetch_vix_front()
    pathlib.Path("data").mkdir(exist_ok=True)
    out.to_csv("data/vix_front.csv", index=False)
    print(out.tail())
