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
if os.getenv("VERCEL"):
    if not os.getenv("DB_ENGINE"):
        os.environ["DB_ENGINE"] = "sqlite"

    if os.environ.get("DB_ENGINE") == "sqlite":
        import shutil
        tmp_db = Path("/tmp/mdtps.sqlite3")
        src_db = ROOT / "instance" / "mdtps.sqlite3"
        
        if not tmp_db.exists() and src_db.exists():
            tmp_db.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_db, tmp_db)
            os.environ["SQLITE_PATH"] = str(tmp_db)
        elif not tmp_db.exists():
            from app.seed import seed_all
            os.environ["SQLITE_PATH"] = str(tmp_db)
            seed_all()
        else:
            os.environ["SQLITE_PATH"] = str(tmp_db)


from app import create_app

# Vercel needs the WSGI callable named 'app'
app = create_app()


class VercelPathFixMiddleware:
    """Ensures Flask receives the intended PATH_INFO under Vercel rewrites."""

    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path_info = environ.get("PATH_INFO", "")
        if path_info in ("/api/index.py", "/api/index", "/api", ""):
            real_uri = (
                environ.get("HTTP_X_FORWARDED_URI")
                or environ.get("REQUEST_URI")
                or environ.get("RAW_URI")
                or "/"
            )
            real_path = real_uri.split("?")[0]
            if real_path and not real_path.startswith("/api/index"):
                environ["PATH_INFO"] = real_path
            else:
                environ["PATH_INFO"] = "/"

        return self.wsgi_app(environ, start_response)


app.wsgi_app = VercelPathFixMiddleware(app.wsgi_app)

if __name__ == "__main__":
    app.run()

