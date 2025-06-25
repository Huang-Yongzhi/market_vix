import dash
from dash import html, dcc, Output, Input
import plotly.graph_objs as go
import pandas as pd
import yfinance as yf
from fetch_vix import fetch_vix_front
import datetime

# 阈值
SLOPE_WARN = 0.03
SLOPE_DANGER = 0.05

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H2("实时市场风险仪表盘"),
    # 报警牌
    html.Div(id="alert-box", style={"font-size":"24px", "margin":"10px"}),
    # 折线图
    dcc.Graph(id="live-chart"),
    # 每10秒刷新一次
    dcc.Interval(id="interval", interval=10_000, n_intervals=0)
])

@app.callback(
    Output("live-chart", "figure"),
    Output("alert-box", "children"),
    Input("interval", "n_intervals")
)
def update_dashboard(n):
    # 1) 抓 VIX 数据
    df_vix = fetch_vix_front()
    # 前 3 行：当月、下月、次下月
    vix1, vix2, vix3 = df_vix["settle"].iloc[:3]
    slope = (vix1 - vix3) / vix3

    # 2) 抓 VIXY/VIXM ETF 价格
    etf = yf.download(["VIXY","VIXM","QQQ"], period="1d", interval="1m")
    # last prices
    p_qqq = etf["Close"]["QQQ"].iloc[-1]
    p_vixy = etf["Close"]["VIXY"].iloc[-1]
    p_vixm = etf["Close"]["VIXM"].iloc[-1]

    # 3) 组织折线数据
    now = datetime.datetime.now()
    x = [now] * 4
    df = pd.DataFrame({
        "Instrument": ["VIX Front","VIXY","VIXM","QQQ"],
        "Price": [vix1, p_vixy, p_vixm, p_qqq]
    })

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Instrument"], y=df["Price"]))
    fig.update_layout(title=f"实时价格 ({now.strftime('%H:%M:%S')})")

    # 4) 报警逻辑
    if slope >= SLOPE_DANGER:
        alert = f"⚠️ Slope={slope:.3f} ≥ {SLOPE_DANGER}: 高风险"
    elif slope >= SLOPE_WARN:
        alert = f"⚠ Slope={slope:.3f} ≥ {SLOPE_WARN}: 注意风险"
    else:
        alert = f"✅ Slope={slope:.3f} 正常"

    return fig, alert

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
