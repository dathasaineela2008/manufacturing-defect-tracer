from flask import Flask
import os

from dotenv import load_dotenv

load_dotenv()


from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(ROOT / "templates"),
        static_folder=str(ROOT / "static"),
    )
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-only-change-me")
    app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024

    from app.routes import bp

    app.register_blueprint(bp)

    @app.errorhandler(404)
    def not_found(_e):
        from flask import render_template
        return render_template("error.html", code=404, message="Page not found."), 404

    @app.errorhandler(500)
    def server_error(_e):
        from flask import render_template
        return render_template(
            "error.html",
            code=500,
            message="Something went wrong. If this is a database error, check .env and MySQL.",
        ), 500

    return app
