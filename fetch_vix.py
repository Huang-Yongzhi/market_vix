# 抓 VIX 期货的脚本
import pandas as pd, requests, io, datetime as dt, sys, pathlib

def fetch_vix_front():
    """拉最近 3 个月 VIX 期货结算价（CFE 公开 CSV）"""
    url = "https://cdn.cboe.com/pub/historicalfutures/vix/current_contract.csv"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
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
