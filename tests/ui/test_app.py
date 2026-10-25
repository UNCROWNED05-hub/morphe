from pathlib import Path
from streamlit.testing.v1 import AppTest

def test_app_smoke():
    root = Path(__file__).resolve().parent.parent.parent
    app_path = root / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=30)
    at.run()
    assert not at.exception
