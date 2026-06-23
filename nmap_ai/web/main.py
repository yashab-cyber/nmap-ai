"""
Web interface main module for NMAP-AI.

The FastAPI application is built by ``create_app()`` and exposed at module
level as ``app`` so it can be imported directly by tests / ASGI servers
(e.g. ``uvicorn nmap_ai.web.main:app``). ``web_main()`` is the CLI entry
point that serves ``app`` with uvicorn.
"""

import os
import sys
from typing import Optional

from ..config import DEFAULT_SECRET_KEY, get_config


# Inline HTML served at "/" when no Jinja template is available.
_FALLBACK_INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>NMAP-AI Web Interface</title>
    <link rel="icon" type="image/png" href="/static/nmap-ai.png">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .logo { text-align: center; margin-bottom: 20px; }
        .logo img { width: 64px; height: 64px; }
        h1 { color: #2c3e50; text-align: center; margin-top: 10px; }
        .status { background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .api-info { background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0; font-family: monospace; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <img src="/static/nmap-ai.png" alt="NMAP-AI Logo">
        </div>
        <h1>🚀 NMAP-AI Web Interface</h1>
        <div class="status">
            <strong>Status:</strong> Web interface is under development.<br>
            Please use the CLI interface for now.
        </div>
        <div class="api-info">
            <strong>API Endpoints:</strong><br>
            • GET /docs - API documentation<br>
            • GET /health - Health check<br>
            • GET /api/v1/status - Service status
        </div>
        <p><strong>CLI Usage:</strong></p>
        <div class="api-info">
            nmap-ai scan 192.168.1.1 --ai-mode smart<br>
            nmap-ai generate-script example.com --vulnerability web<br>
            nmap-ai smart-scan 10.0.0.1 --profile adaptive
        </div>
    </div>
</body>
</html>
"""


def resolve_secret_key(config) -> str:
    """Secret key precedence: NMAP_AI_SECRET_KEY env var > config value."""
    return os.environ.get("NMAP_AI_SECRET_KEY") or config.web.secret_key


def secret_key_error(config) -> Optional[str]:
    """Return an error message if the secret key is unsafe to serve with.

    Returns None when it is safe (debug mode, or a non-default key is set).
    """
    if config.web.debug:
        return None
    key = resolve_secret_key(config)
    if not key or key == DEFAULT_SECRET_KEY:
        return (
            "Refusing to start the web server with the default secret key.\n"
            "Set a strong secret via the NMAP_AI_SECRET_KEY environment "
            "variable,\nor enable debug mode (web.debug = true) for local "
            "development."
        )
    return None


def create_app(config=None):
    """Build and return the NMAP-AI FastAPI application.

    Raises ImportError if the optional web dependencies are not installed.
    This does not enforce secret-key safety (so the module is import-safe);
    that check happens at server start in web_main().
    """
    from fastapi import FastAPI, Request
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates

    config = config or get_config()

    app = FastAPI(
        title="NMAP-AI Web Interface",
        description="Heuristic-driven Nmap wrapper — web interface",
        version="1.0.0",
    )

    current_dir = os.path.dirname(__file__)
    static_dir = os.path.join(current_dir, "static")
    templates_dir = os.path.join(current_dir, "templates")

    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    templates = Jinja2Templates(directory=templates_dir) if os.path.exists(templates_dir) else None

    @app.get("/", response_class=HTMLResponse)
    async def root(request: Request):
        if templates is not None:
            try:
                return templates.TemplateResponse("index.html", {"request": request})
            except Exception:
                pass
        return HTMLResponse(_FALLBACK_INDEX_HTML)

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "nmap-ai-web", "version": "1.0.0"}

    @app.get("/api/v1/status")
    async def api_status():
        return {
            "service": "NMAP-AI API",
            "version": "1.0.0",
            "status": "development",
            "features": {
                "scanning": "planned",
                "ai_script_generation": "planned",
                "result_analysis": "planned",
                "web_dashboard": "in_development",
            },
        }

    app.state.secret_key = resolve_secret_key(config)
    return app


try:
    # Module-level app for ASGI servers and tests. None if web deps absent.
    app = create_app()
except ImportError:
    app = None


def web_main(port: int = 8080, host: str = "localhost", args: Optional[list] = None) -> None:
    """CLI entry point: serve the web application with uvicorn."""
    try:
        try:
            import uvicorn
        except ImportError:
            print("Web dependencies not installed. Please install with: pip install nmap-ai[web]")
            sys.exit(1)

        config = get_config()

        # Fail fast rather than serving with the insecure default secret key.
        err = secret_key_error(config)
        if err:
            print(err, file=sys.stderr)
            sys.exit(1)

        application = create_app(config)

        print("🚀 Starting NMAP-AI Web Interface...")
        print(f"🌐 Access the web interface at: http://{host}:{port}")
        print(f"📖 API documentation at: http://{host}:{port}/docs")
        print("⚡ Use Ctrl+C to stop the server")

        uvicorn.run(application, host=host, port=port, log_level="info")

    except Exception as e:
        print(f"Error launching web interface: {e}")
        print("Please ensure web dependencies are installed: pip install nmap-ai[web]")
        sys.exit(1)


if __name__ == "__main__":
    web_main()
