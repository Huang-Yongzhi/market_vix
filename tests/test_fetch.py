import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from fetch_data import get_prices, get_vix_front, calc_slope


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
