# Market VIX Dashboard

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
python app.py
```

## Screenshot

![dashboard screenshot](docs/screenshot.png)

## Indicator Explanation

The app computes the VIX term structure slope using the first and third futures
contracts: `(v1 - v3) / v3`. Positive values indicate a steeper front end and
can signal increased market stress.

