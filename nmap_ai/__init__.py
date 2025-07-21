"""
NMAP-AI: AI-Powered Network Scanning & Automation

This package provides advanced network scanning capabilities enhanced with
artificial intelligence for script generation, intelligent scanning, and
automated vulnerability detection.

Author: Yashab Alam (ZehraSec)
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Yashab Alam"
__email__ = "yashabalam707@gmail.com"
__license__ = "MIT"
__url__ = "https://github.com/yashab-cyber/nmap-ai"

from .core.scanner import NmapAIScanner
from .ai.script_generator import AIScriptGenerator
from .ai.smart_scanner import SmartScanner
from .ai.vulnerability_detector import VulnerabilityDetector

__all__ = [
    "NmapAIScanner",
    "AIScriptGenerator", 
    "SmartScanner",
    "VulnerabilityDetector"
]
