import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Output, Input
import plotly.graph_objs as go
import os, certifi


from fetch_data import get_price_frame, get_vix_front, calc_slope

ALARM_HISTORY = []


app = dash.Dash(__name__)
app.layout = html.Div([
    html.H2("Market Dashboard"),
    dcc.Graph(id="live"),
    html.Div(id="alert", style={"fontSize": "24px"}),
    html.Ul(id="log"),
    dcc.Interval(id="timer", interval=10000, n_intervals=0),
])


@app.callback(
    Output("live", "figure"),
    Output("alert", "children"),
    Output("log", "children"),
    Input("timer", "n_intervals"),
)
def update(_):
    prices = get_price_frame(period="3d", interval="5m")
    v1 = get_vix_front()[0]
    slope = calc_slope()

    fig = go.Figure()
    for col in prices.columns:
        fig.add_trace(go.Scatter(x=prices.index, y=prices[col], name=col))
    fig.add_trace(go.Scatter(x=prices.index, y=[v1] * len(prices), name="VIX_front"))

    now = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    if slope >= 0.05:
        alert = html.Span("高风险", style={"color": "red"})
        ALARM_HISTORY.insert(0, f"{now} {slope}")
        with open("alarm.log", "a", encoding="utf-8") as f:
            f.write(f"{now} slope={slope}\n")
    elif slope >= 0.03:
        alert = html.Span("警戒", style={"color": "yellow"})
        ALARM_HISTORY.insert(0, f"{now} {slope}")
    else:
        alert = html.Span("正常", style={"color": "green"})

    items = [html.Li(entry) for entry in ALARM_HISTORY[:5]]
    return fig, alert, items


if __name__ == "__main__":
    app.run(debug=True, port=8050)
