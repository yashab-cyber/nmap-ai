"""
Web API module for NMAP-AI.

This module contains REST API endpoints for the web interface.
"""

from .endpoints import router
from .models import *

__all__ = ['router']
