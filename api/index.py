"""
Vercel Serverless Entrypoint for MDTPS.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure the root project directory is in the Python search path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Handle Vercel serverless read-only filesystem:
# In Vercel serverless environments, only /tmp is writable.
if os.getenv("VERCEL") or not os.getenv("DB_ENGINE") or os.getenv("DB_ENGINE") == "sqlite":
    import shutil
    tmp_db = Path("/tmp/mdtps.sqlite3")
    src_db = ROOT / "instance" / "mdtps.sqlite3"
    
    if not tmp_db.exists() and src_db.exists():
        tmp_db.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_db, tmp_db)
        os.environ["SQLITE_PATH"] = str(tmp_db)
    elif not tmp_db.exists():
        # Fallback to direct seeding if bundled file is missing
        from app.seed import seed_all
        os.environ["SQLITE_PATH"] = str(tmp_db)
        seed_all()
    else:
        os.environ["SQLITE_PATH"] = str(tmp_db)

from app import create_app

# Vercel needs the WSGI callable named 'app'
app = create_app()

if __name__ == "__main__":
    app.run()
