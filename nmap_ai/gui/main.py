"""
GUI entry point for NMAP-AI.

The desktop GUI is not implemented yet (see roadmap Phase 1 / Phase 4).
Rather than launch a placeholder window that pretends to be a real UI,
``gui_main`` reports that the GUI is unavailable and points users at the
working CLI. This keeps the advertised feature set honest.
"""

import sys
from typing import Optional


_MESSAGE = (
    "The NMAP-AI desktop GUI is not available yet.\n"
    "Please use the command-line interface instead:\n\n"
    "    nmap-ai scan <target> --ai-mode smart\n"
    "    nmap-ai smart-scan <target> --profile adaptive\n"
    "    nmap-ai generate-script <target> --vulnerability web\n\n"
    "Run 'nmap-ai --help' (or 'nmap-ai-cli --help') for all commands.\n"
    "Track GUI progress in roadmap.md."
)


def gui_main(args: Optional[list] = None) -> None:
    """Report that the GUI is unavailable and exit with a non-zero status."""
    print(_MESSAGE, file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    gui_main()
