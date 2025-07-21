"""
Base plugin classes for NMAP-AI plugin system.

This module defines the base classes that all plugins should inherit from
to ensure proper integration with the NMAP-AI framework.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import logging
from dataclasses import dataclass

from ..utils.logger import get_logger


@dataclass
class PluginMetadata:
    """Plugin metadata information."""
    name: str
    version: str
    description: str
    author: str
    license: str
    dependencies: List[str]
    supported_platforms: List[str]


class BasePlugin(ABC):
    """
    Base class for all NMAP-AI plugins.
    
    All plugins must inherit from this class and implement the required methods.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the plugin.
        
        Args:
            config: Plugin configuration dictionary
        """
        self.config = config or {}
        self.logger = get_logger(f"plugin.{self.__class__.__name__}")
        self._enabled = True
        self._initialized = False
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the plugin.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """
        Cleanup plugin resources.
        
        Returns:
            bool: True if cleanup successful, False otherwise
        """
        pass
    
    def enable(self) -> None:
        """Enable the plugin."""
        self._enabled = True
        self.logger.info(f"Plugin {self.metadata.name} enabled")
    
    def disable(self) -> None:
        """Disable the plugin."""
        self._enabled = False
        self.logger.info(f"Plugin {self.metadata.name} disabled")
    
    @property
    def enabled(self) -> bool:
        """Check if plugin is enabled."""
        return self._enabled
    
    @property
    def initialized(self) -> bool:
        """Check if plugin is initialized."""
        return self._initialized
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate plugin configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            bool: True if configuration is valid
        """
        # Default implementation - plugins can override
        return True


class ScannerPlugin(BasePlugin):
    """
    Base class for scanning plugins.
    
    Scanner plugins can modify scan parameters, add custom scan methods,
    or post-process scan results.
    """
    
    @abstractmethod
    def pre_scan_hook(self, targets: List[str], scan_options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hook called before scanning starts.
        
        Args:
            targets: List of scan targets
            scan_options: Scan configuration options
            
        Returns:
            Dict: Modified scan options
        """
        pass
    
    @abstractmethod
    def post_scan_hook(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hook called after scanning completes.
        
        Args:
            scan_results: Raw scan results
            
        Returns:
            Dict: Modified scan results
        """
        pass
    
    def custom_scan_method(self, targets: List[str], **kwargs) -> Optional[Dict[str, Any]]:
        """
        Implement custom scanning method.
        
        Args:
            targets: List of scan targets
            **kwargs: Additional scan parameters
            
        Returns:
            Optional[Dict]: Custom scan results or None if not implemented
        """
        return None


class ReportPlugin(BasePlugin):
    """
    Base class for report generation plugins.
    
    Report plugins can add new output formats or modify existing reports.
    """
    
    @property
    @abstractmethod
    def supported_formats(self) -> List[str]:
        """Return list of supported report formats."""
        pass
    
    @abstractmethod
    def generate_report(self, scan_results: Dict[str, Any], format_type: str, output_path: Optional[Path] = None) -> Union[str, bytes]:
        """
        Generate report in specified format.
        
        Args:
            scan_results: Scan results to generate report from
            format_type: Report format type
            output_path: Optional output file path
            
        Returns:
            Union[str, bytes]: Generated report content
        """
        pass
    
    def validate_format(self, format_type: str) -> bool:
        """
        Validate if format is supported.
        
        Args:
            format_type: Format to validate
            
        Returns:
            bool: True if format is supported
        """
        return format_type.lower() in [f.lower() for f in self.supported_formats]


class AIPlugin(BasePlugin):
    """
    Base class for AI-powered plugins.
    
    AI plugins can add new machine learning models, analysis methods,
    or intelligent automation features.
    """
    
    @property
    @abstractmethod
    def model_requirements(self) -> List[str]:
        """Return list of required AI models."""
        pass
    
    @abstractmethod
    def load_models(self) -> bool:
        """
        Load required AI models.
        
        Returns:
            bool: True if models loaded successfully
        """
        pass
    
    @abstractmethod
    def analyze_results(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform AI analysis on scan results.
        
        Args:
            scan_results: Raw scan results
            
        Returns:
            Dict: Analysis results with AI insights
        """
        pass
    
    def train_model(self, training_data: List[Dict[str, Any]]) -> bool:
        """
        Train AI model with new data.
        
        Args:
            training_data: Training data samples
            
        Returns:
            bool: True if training successful
        """
        # Default implementation - plugins can override
        self.logger.warning(f"Plugin {self.metadata.name} does not support model training")
        return False
    
    def get_confidence_score(self, analysis_results: Dict[str, Any]) -> float:
        """
        Get confidence score for AI analysis.
        
        Args:
            analysis_results: AI analysis results
            
        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        return analysis_results.get('confidence', 0.0)


class PluginManager:
    """
    Plugin manager for loading and managing NMAP-AI plugins.
    """
    
    def __init__(self, plugin_dirs: Optional[List[Path]] = None):
        """
        Initialize plugin manager.
        
        Args:
            plugin_dirs: List of directories to search for plugins
        """
        self.plugin_dirs = plugin_dirs or []
        self.plugins: Dict[str, BasePlugin] = {}
        self.logger = get_logger("plugin_manager")
    
    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins in plugin directories.
        
        Returns:
            List[str]: List of discovered plugin names
        """
        discovered = []
        
        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                continue
                
            for plugin_file in plugin_dir.glob("*.py"):
                if plugin_file.name.startswith("__"):
                    continue
                    
                plugin_name = plugin_file.stem
                discovered.append(plugin_name)
                
        return discovered
    
    def load_plugin(self, plugin_name: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Load a plugin by name.
        
        Args:
            plugin_name: Name of plugin to load
            config: Plugin configuration
            
        Returns:
            bool: True if plugin loaded successfully
        """
        try:
            # Import plugin module dynamically
            import importlib.util
            
            plugin_path = None
            for plugin_dir in self.plugin_dirs:
                potential_path = plugin_dir / f"{plugin_name}.py"
                if potential_path.exists():
                    plugin_path = potential_path
                    break
            
            if not plugin_path:
                self.logger.error(f"Plugin {plugin_name} not found")
                return False
            
            # Load plugin module
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            if not spec or not spec.loader:
                self.logger.error(f"Failed to load plugin spec for {plugin_name}")
                return False
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin class
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, BasePlugin) and 
                    attr != BasePlugin and
                    not attr.__name__.startswith('_')):
                    plugin_class = attr
                    break
            
            if not plugin_class:
                self.logger.error(f"No plugin class found in {plugin_name}")
                return False
            
            # Initialize plugin
            plugin = plugin_class(config)
            if not plugin.initialize():
                self.logger.error(f"Failed to initialize plugin {plugin_name}")
                return False
            
            self.plugins[plugin_name] = plugin
            self.logger.info(f"Successfully loaded plugin {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading plugin {plugin_name}: {e}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin.
        
        Args:
            plugin_name: Name of plugin to unload
            
        Returns:
            bool: True if plugin unloaded successfully
        """
        if plugin_name not in self.plugins:
            self.logger.warning(f"Plugin {plugin_name} not loaded")
            return False
        
        try:
            plugin = self.plugins[plugin_name]
            plugin.cleanup()
            del self.plugins[plugin_name]
            self.logger.info(f"Successfully unloaded plugin {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unloading plugin {plugin_name}: {e}")
            return False
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """
        Get a loaded plugin by name.
        
        Args:
            plugin_name: Name of plugin to get
            
        Returns:
            Optional[BasePlugin]: Plugin instance or None if not found
        """
        return self.plugins.get(plugin_name)
    
    def list_plugins(self, plugin_type: Optional[type] = None) -> List[str]:
        """
        List loaded plugins, optionally filtered by type.
        
        Args:
            plugin_type: Optional plugin type to filter by
            
        Returns:
            List[str]: List of plugin names
        """
        if plugin_type is None:
            return list(self.plugins.keys())
        
        return [
            name for name, plugin in self.plugins.items()
            if isinstance(plugin, plugin_type)
        ]
    
    def cleanup_all(self) -> None:
        """Cleanup all loaded plugins."""
        for plugin_name in list(self.plugins.keys()):
            self.unload_plugin(plugin_name)
