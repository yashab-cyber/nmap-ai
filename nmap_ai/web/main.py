"""
Web interface main module for NMAP-AI
"""

import sys
import os
from typing import Optional

def web_main(port: int = 8080, host: str = "localhost", args: Optional[list] = None) -> None:
    """
    Main entry point for web application.
    
    Args:
        port: Port to run web server on
        host: Host to bind to
        args: Command line arguments (optional)
    """
    try:
        # Try to import web dependencies
        try:
            from fastapi import FastAPI, HTTPException, Request
            from fastapi.staticfiles import StaticFiles
            from fastapi.templating import Jinja2Templates
            from fastapi.responses import HTMLResponse
            import uvicorn
        except ImportError:
            print("Web dependencies not installed. Please install with: pip install nmap-ai[web]")
            sys.exit(1)
        
        # Create FastAPI application
        app = FastAPI(
            title="NMAP-AI Web Interface",
            description="AI-Powered Network Scanning & Automation",
            version="1.0.0"
        )
        
        # Get the current directory
        current_dir = os.path.dirname(__file__)
        static_dir = os.path.join(current_dir, "static")
        templates_dir = os.path.join(current_dir, "templates")
        
        # Mount static files
        if os.path.exists(static_dir):
            app.mount("/static", StaticFiles(directory=static_dir), name="static")
        
        # Setup templates
        if os.path.exists(templates_dir):
            templates = Jinja2Templates(directory=templates_dir)
        
        # Basic routes
        @app.get("/", response_class=HTMLResponse)
        async def root(request: Request):
            # If templates exist, use them, otherwise fall back to inline HTML
            if os.path.exists(templates_dir):
                try:
                    return templates.TemplateResponse("index.html", {"request": request})
                except:
                    pass
            
            return """
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
                        • POST /api/v1/scan - Start scan (coming soon)<br>
                        • GET /api/v1/results - Get results (coming soon)
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
                    "web_dashboard": "in_development"
                }
            }
        
        # Placeholder API endpoints
        @app.post("/api/v1/scan")
        async def start_scan():
            raise HTTPException(status_code=501, detail="Scan API endpoint not yet implemented")
        
        @app.get("/api/v1/results/{scan_id}")
        async def get_results(scan_id: str):
            raise HTTPException(status_code=501, detail="Results API endpoint not yet implemented")
        
        # Print startup message
        print("🚀 Starting NMAP-AI Web Interface...")
        print(f"🌐 Access the web interface at: http://{host}:{port}")
        print(f"📖 API documentation at: http://{host}:{port}/docs")
        print("⚡ Use Ctrl+C to stop the server")
        
        # Run the web server
        uvicorn.run(app, host=host, port=port, log_level="info")
        
    except Exception as e:
        print(f"Error launching web interface: {e}")
        print("Please ensure web dependencies are installed: pip install nmap-ai[web]")
        sys.exit(1)


if __name__ == "__main__":
    web_main()
