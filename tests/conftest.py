import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.environ["DB_ENGINE"] = "sqlite"
os.environ["SQLITE_PATH"] = str(ROOT / "instance" / "test_mdtps.sqlite3")
os.environ["SECRET_KEY"] = "test-secret-key"

import pytest

from app.seed import seed_all


@pytest.fixture(scope="session", autouse=True)
def _prepare_data():
    subprocess.check_call([sys.executable, str(ROOT / "scripts" / "generate_sample_data.py")])
    seed_all()
    subprocess.check_call([sys.executable, str(ROOT / "ml" / "train_model.py")])
