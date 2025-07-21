"""
Logging utilities for NMAP-AI
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from rich.logging import RichHandler
from rich.console import Console

from ..config import get_config


def setup_logging() -> None:
    """Setup logging configuration."""
    config = get_config()
    
    # Create logs directory
    log_dir = Path.home() / ".nmap-ai" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            RichHandler(console=Console(stderr=True), rich_tracebacks=True),
            logging.FileHandler(log_dir / "nmap-ai.log"),
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    # Setup logging if not already done
    if not logging.getLogger().handlers:
        setup_logging()
    
    return logging.getLogger(name)


class ProgressLogger:
    """Logger with progress indication."""
    
    def __init__(self, logger: logging.Logger, total_steps: int):
        self.logger = logger
        self.total_steps = total_steps
        self.current_step = 0
    
    def step(self, message: str, level: int = logging.INFO) -> None:
        """Log a step with progress indication."""
        self.current_step += 1
        progress = (self.current_step / self.total_steps) * 100
        
        progress_msg = f"[{self.current_step}/{self.total_steps}] ({progress:.1f}%) {message}"
        self.logger.log(level, progress_msg)
    
    def complete(self, message: str = "Process completed") -> None:
        """Log completion message."""
        self.logger.info(f"✓ {message}")
    
    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(f"✗ {message}")


def log_scan_start(logger: logging.Logger, targets: list, options: dict) -> None:
    """Log scan start information."""
    logger.info("=" * 50)
    logger.info("NMAP-AI Scan Starting")
    logger.info(f"Targets: {', '.join(targets)}")
    logger.info(f"Options: {options}")
    logger.info("=" * 50)


def log_scan_complete(logger: logging.Logger, results: dict) -> None:
    """Log scan completion information."""
    logger.info("=" * 50)
    logger.info("NMAP-AI Scan Complete")
    logger.info(f"Duration: {results.get('duration', 'N/A')} seconds")
    logger.info(f"Targets scanned: {len(results.get('results', {}))}")
    logger.info("=" * 50)
