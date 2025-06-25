import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Output, Input
import plotly.graph_objs as go

from fetch_data import get_prices, get_vix_front, calc_slope


app = dash.Dash(__name__)
app.layout = html.Div([
    html.H2("Market Dashboard"),
    dcc.Graph(id="live"),
    html.Div(id="alert", style={"fontSize": "24px"}),
    dcc.Interval(id="timer", interval=10000, n_intervals=0),
])


@app.callback(
    Output("live", "figure"),
    Output("alert", "children"),
    Input("timer", "n_intervals"),
)
def update(_):
    prices = get_prices()
    latest = prices.iloc[-1]
    if isinstance(prices.columns, pd.MultiIndex):
        qqq = latest[("Close", "QQQ")]
        vixy = latest[("Close", "VIXY")]
        vixm = latest[("Close", "VIXM")]
    else:
        qqq = latest["QQQ"]
        vixy = latest["VIXY"]
        vixm = latest["VIXM"]
    v1 = get_vix_front()[0]
    slope = calc_slope()

    df = pd.DataFrame({"Instrument": ["QQQ", "VIXY", "VIXM", "VIX_front"],
                       "Price": [qqq, vixy, vixm, v1]})
    fig = go.Figure(data=go.Scatter(x=df["Instrument"], y=df["Price"], mode="lines+markers"))

    if slope >= 0.05:
        alert = html.Span("高风险", style={"color": "red"})
    elif slope >= 0.03:
        alert = html.Span("警戒", style={"color": "yellow"})
    else:
        alert = html.Span("正常", style={"color": "green"})

    return fig, alert


if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
