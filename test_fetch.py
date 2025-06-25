# 一个超小单元测试
from fetch_vix import fetch_vix_front

def test_shape():
    df = fetch_vix_front()
    assert df.shape[1] == 3
    assert (df["settle"] > 0).all()
