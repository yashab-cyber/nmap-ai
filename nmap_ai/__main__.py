"""
Main entry point for NMAP-AI application.
"""

import sys
import argparse
from .cli.main import cli_main
from .gui.main import gui_main
from .web.main import web_main


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="NMAP-AI: AI-Powered Network Scanning")
    parser.add_argument("--gui", action="store_true", help="Launch GUI interface")
    parser.add_argument("--web", action="store_true", help="Launch web interface")
    parser.add_argument("--port", type=int, default=8080, help="Web server port")
    
    # If no args provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args, remaining = parser.parse_known_args()
    
    if args.gui:
        gui_main()
    elif args.web:
        web_main(port=args.port)
    else:
        # Default to CLI with remaining args
        cli_main(remaining)


if __name__ == "__main__":
    main()
