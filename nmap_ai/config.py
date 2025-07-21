"""
Configuration management for NMAP-AI
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class AIConfig:
    """AI model configuration."""
    script_generation_model: str = "models/script_gen_v3.pkl"
    vulnerability_detection_model: str = "models/vuln_detect_v2.pkl"
    port_prediction_model: str = "models/port_pred_v1.pkl"
    confidence_threshold: float = 0.7
    max_script_length: int = 5000


@dataclass
class ScanConfig:
    """Scanning configuration."""
    default_timeout: int = 300
    max_parallel_hosts: int = 50
    retries: int = 3
    default_ports: str = "1-1000"
    stealth_mode: bool = False
    timing_template: int = 3


@dataclass
class OutputConfig:
    """Output configuration."""
    default_format: str = "json"
    include_raw_nmap: bool = True
    compress_results: bool = True
    output_directory: str = "results"
    report_templates_dir: str = "data/templates"


@dataclass
class WebConfig:
    """Web interface configuration."""
    host: str = "localhost"
    port: int = 8080
    debug: bool = False
    secret_key: str = "change-me-in-production"
    max_upload_size: int = 10 * 1024 * 1024  # 10MB


@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str = "sqlite:///nmap_ai.db"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10


@dataclass
class NmapAIConfig:
    """Main configuration class."""
    ai: AIConfig = AIConfig()
    scanning: ScanConfig = ScanConfig()
    output: OutputConfig = OutputConfig()
    web: WebConfig = WebConfig()
    database: DatabaseConfig = DatabaseConfig()
    log_level: str = "INFO"
    debug: bool = False


class ConfigManager:
    """Configuration manager for NMAP-AI."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._get_default_config_path()
        self.config = NmapAIConfig()
        self.load_config()
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path."""
        config_dir = Path.home() / ".nmap-ai"
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / "config.yml")
    
    def load_config(self) -> None:
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    if self.config_file.endswith(('.yml', '.yaml')):
                        data = yaml.safe_load(f)
                    else:
                        data = json.load(f)
                
                if data:
                    self._update_config_from_dict(data)
            except Exception as e:
                print(f"Warning: Could not load config file {self.config_file}: {e}")
    
    def save_config(self) -> None:
        """Save configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            data = asdict(self.config)
            
            with open(self.config_file, 'w') as f:
                if self.config_file.endswith(('.yml', '.yaml')):
                    yaml.dump(data, f, default_flow_style=False, indent=2)
                else:
                    json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config file {self.config_file}: {e}")
    
    def _update_config_from_dict(self, data: Dict[str, Any]) -> None:
        """Update configuration from dictionary."""
        if "ai" in data:
            for key, value in data["ai"].items():
                if hasattr(self.config.ai, key):
                    setattr(self.config.ai, key, value)
        
        if "scanning" in data:
            for key, value in data["scanning"].items():
                if hasattr(self.config.scanning, key):
                    setattr(self.config.scanning, key, value)
        
        if "output" in data:
            for key, value in data["output"].items():
                if hasattr(self.config.output, key):
                    setattr(self.config.output, key, value)
        
        if "web" in data:
            for key, value in data["web"].items():
                if hasattr(self.config.web, key):
                    setattr(self.config.web, key, value)
        
        if "database" in data:
            for key, value in data["database"].items():
                if hasattr(self.config.database, key):
                    setattr(self.config.database, key, value)
        
        # Top-level attributes
        if "log_level" in data:
            self.config.log_level = data["log_level"]
        if "debug" in data:
            self.config.debug = data["debug"]
    
    def get_config(self) -> NmapAIConfig:
        """Get the current configuration."""
        return self.config
    
    def update_config(self, **kwargs) -> None:
        """Update configuration values."""
        for section, updates in kwargs.items():
            if hasattr(self.config, section):
                section_config = getattr(self.config, section)
                for key, value in updates.items():
                    if hasattr(section_config, key):
                        setattr(section_config, key, value)
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        self.config = NmapAIConfig()
        self.save_config()


# Global configuration instance
config_manager = ConfigManager()

def get_config() -> NmapAIConfig:
    """Get the global configuration."""
    return config_manager.get_config()

def update_config(**kwargs) -> None:
    """Update the global configuration."""
    config_manager.update_config(**kwargs)
    config_manager.save_config()
