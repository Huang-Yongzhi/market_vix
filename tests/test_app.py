import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from app import app


def test_server_exists():
    assert app.server is not None
