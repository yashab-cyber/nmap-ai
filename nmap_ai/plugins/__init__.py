"""
Plugin system for NMAP-AI.

This module provides the base classes and utilities for creating
custom plugins to extend NMAP-AI functionality.
"""

from .base import (
    BasePlugin,
    ScannerPlugin,
    ReportPlugin,
    AIPlugin,
    PluginMetadata,
    PluginManager,
    default_plugin_dirs,
)

__all__ = [
    'BasePlugin',
    'ScannerPlugin',
    'ReportPlugin',
    'AIPlugin',
    'PluginMetadata',
    'PluginManager',
    'default_plugin_dirs',
]
