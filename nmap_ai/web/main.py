"""
Web interface main module for NMAP-AI
"""

import sys
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
            from fastapi import FastAPI, HTTPException
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
        
        # Basic routes
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>NMAP-AI Web Interface</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    h1 { color: #2c3e50; text-align: center; }
                    .status { background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 20px 0; }
                    .api-info { background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0; font-family: monospace; }
                </style>
            </head>
            <body>
                <div class="container">
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
