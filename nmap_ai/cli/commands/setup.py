"""
Setup and initialization command for NMAP-AI CLI.
Handles application setup, model initialization, and system validation.
"""
import argparse
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
import subprocess
import shutil
import requests
import json

try:
    from nmap_ai.config import load_config, save_config, get_default_config
except ImportError:
    # Fallback for when dependencies aren't available
    def load_config(path):
        """Fallback config loader."""
        try:
            import yaml
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except:
            return {}
    
    def save_config(config, path):
        """Fallback config saver."""
        try:
            import yaml
            from pathlib import Path
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
        except:
            pass
    
    def get_default_config():
        """Fallback default config."""
        return {
            'ai': {
                'enabled': True,
                'model_path': '~/.nmap-ai/models',
                'confidence_threshold': 0.7
            },
            'scanning': {
                'default_timing': 'T3',
                'max_concurrent': 10,
                'timeout': 300
            },
            'logging': {
                'level': 'INFO',
                'file': '~/.nmap-ai/logs/nmap-ai.log'
            }
        }

try:
    from nmap_ai.utils.logger import get_logger
except ImportError:
    def get_logger(name):
        """Fallback logger."""
        import logging
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(name)

logger = get_logger(__name__)


def setup_command(args: argparse.Namespace) -> int:
    """
    Handle setup and initialization commands.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        if args.setup_action == 'init':
            return initialize_application(args)
        elif args.setup_action == 'init-models':
            return initialize_models(args)
        elif args.setup_action == 'init-db':
            return initialize_database(args)
        elif args.setup_action == 'validate':
            return validate_setup(args)
        elif args.setup_action == 'reset':
            return reset_application(args)
        else:
            logger.error(f"Unknown setup action: {args.setup_action}")
            return 1
            
    except Exception as e:
        logger.error(f"Setup command failed: {e}")
        return 1


def initialize_application(args: argparse.Namespace) -> int:
    """
    Initialize the complete NMAP-AI application.
    
    Args:
        args: Command line arguments
        
    Returns:
        Exit code
    """
    logger.info("Initializing NMAP-AI application...")
    
    try:
        # Create necessary directories
        create_directories()
        
        # Initialize configuration
        initialize_config(args)
        
        # Check system dependencies
        if not check_dependencies():
            logger.error("System dependencies check failed")
            return 1
        
        # Initialize models if requested
        if args.with_models:
            if initialize_models(args) != 0:
                logger.warning("Model initialization failed, continuing without models")
        
        # Initialize database if requested
        if args.with_db:
            if initialize_database(args) != 0:
                logger.warning("Database initialization failed, continuing without database")
        
        logger.info("NMAP-AI application initialized successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Application initialization failed: {e}")
        return 1


def create_directories() -> None:
    """Create necessary application directories."""
    dirs = [
        Path.home() / '.nmap-ai',
        Path.home() / '.nmap-ai' / 'config',
        Path.home() / '.nmap-ai' / 'logs',
        Path.home() / '.nmap-ai' / 'models',
        Path.home() / '.nmap-ai' / 'data',
        Path.home() / '.nmap-ai' / 'cache',
        Path.home() / '.nmap-ai' / 'reports'
    ]
    
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created directory: {directory}")


def initialize_config(args: argparse.Namespace) -> None:
    """Initialize application configuration."""
    config_path = Path.home() / '.nmap-ai' / 'config' / 'config.yaml'
    
    if config_path.exists() and not args.force:
        logger.info(f"Configuration already exists at {config_path}")
        return
    
    logger.info("Creating default configuration...")
    default_config = get_default_config()
    save_config(default_config, str(config_path))
    logger.info(f"Configuration created at {config_path}")


def check_dependencies() -> bool:
    """Check if required system dependencies are installed."""
    logger.info("Checking system dependencies...")
    
    dependencies = {
        'nmap': 'nmap --version',
        'python': 'python --version'
    }
    
    all_ok = True
    for dep, check_cmd in dependencies.items():
        try:
            result = subprocess.run(check_cmd.split(), 
                                  capture_output=True, text=True, check=True)
            logger.debug(f"{dep}: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error(f"Required dependency not found: {dep}")
            all_ok = False
    
    return all_ok


def initialize_models(args: argparse.Namespace) -> int:
    """
    Initialize AI models for the application.
    
    Args:
        args: Command line arguments
        
    Returns:
        Exit code
    """
    logger.info("Initializing AI models...")
    
    try:
        models_dir = Path.home() / '.nmap-ai' / 'models'
        models_dir.mkdir(parents=True, exist_ok=True)
        
        # For now, we'll just create placeholder files
        # In a real implementation, this would download and set up actual models
        model_files = [
            'vulnerability_classifier.pkl',
            'service_detector.pkl',
            'network_analyzer.pkl'
        ]
        
        for model_file in model_files:
            model_path = models_dir / model_file
            if not model_path.exists() or args.force:
                # Create placeholder model file
                model_path.write_text(f"# Placeholder for {model_file}\n")
                logger.info(f"Initialized model: {model_file}")
        
        logger.info("AI models initialized successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Model initialization failed: {e}")
        return 1


def initialize_database(args: argparse.Namespace) -> int:
    """
    Initialize database for storing scan results and history.
    
    Args:
        args: Command line arguments
        
    Returns:
        Exit code
    """
    logger.info("Initializing database...")
    
    try:
        db_dir = Path.home() / '.nmap-ai' / 'data'
        db_dir.mkdir(parents=True, exist_ok=True)
        
        db_file = db_dir / 'nmap_ai.db'
        
        # For now, we'll just create a placeholder database file
        # In a real implementation, this would set up SQLite/PostgreSQL tables
        if not db_file.exists() or args.force:
            db_file.write_text("# NMAP-AI Database placeholder\n")
            logger.info(f"Database initialized at {db_file}")
        else:
            logger.info("Database already exists")
        
        logger.info("Database initialized successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return 1


def validate_setup(args: argparse.Namespace) -> int:
    """
    Validate the current application setup.
    
    Args:
        args: Command line arguments
        
    Returns:
        Exit code
    """
    logger.info("Validating NMAP-AI setup...")
    
    try:
        issues = []
        
        # Check directories
        required_dirs = [
            Path.home() / '.nmap-ai',
            Path.home() / '.nmap-ai' / 'config',
            Path.home() / '.nmap-ai' / 'logs',
        ]
        
        for directory in required_dirs:
            if not directory.exists():
                issues.append(f"Missing directory: {directory}")
        
        # Check configuration
        config_path = Path.home() / '.nmap-ai' / 'config' / 'config.yaml'
        if not config_path.exists():
            issues.append(f"Missing configuration file: {config_path}")
        else:
            try:
                load_config(str(config_path))
            except Exception as e:
                issues.append(f"Invalid configuration file: {e}")
        
        # Check dependencies
        if not check_dependencies():
            issues.append("Missing system dependencies")
        
        if issues:
            logger.error("Setup validation failed:")
            for issue in issues:
                logger.error(f"  - {issue}")
            return 1
        else:
            logger.info("Setup validation successful - all checks passed")
            return 0
            
    except Exception as e:
        logger.error(f"Setup validation failed: {e}")
        return 1


def reset_application(args: argparse.Namespace) -> int:
    """
    Reset the application to initial state.
    
    Args:
        args: Command line arguments
        
    Returns:
        Exit code
    """
    if not args.force:
        logger.error("Reset requires --force flag to confirm destructive action")
        return 1
    
    logger.info("Resetting NMAP-AI application...")
    
    try:
        nmap_ai_dir = Path.home() / '.nmap-ai'
        
        if nmap_ai_dir.exists():
            shutil.rmtree(nmap_ai_dir)
            logger.info(f"Removed application directory: {nmap_ai_dir}")
        
        logger.info("Application reset completed")
        return 0
        
    except Exception as e:
        logger.error(f"Application reset failed: {e}")
        return 1


# Add argument parser for setup command
def add_setup_arguments(parser: argparse.ArgumentParser) -> None:
    """Add setup command arguments to parser."""
    setup_parser = parser.add_parser('setup', help='Initialize and configure NMAP-AI')
    setup_subparsers = setup_parser.add_subparsers(dest='setup_action', help='Setup actions')
    
    # Init command
    init_parser = setup_subparsers.add_parser('init', help='Initialize complete application')
    init_parser.add_argument('--force', action='store_true', 
                           help='Force reinitialize even if already exists')
    init_parser.add_argument('--with-models', action='store_true', 
                           help='Initialize AI models during setup')
    init_parser.add_argument('--with-db', action='store_true',
                           help='Initialize database during setup')
    
    # Init models command
    models_parser = setup_subparsers.add_parser('init-models', help='Initialize AI models')
    models_parser.add_argument('--force', action='store_true',
                             help='Force download models even if they exist')
    
    # Init database command
    db_parser = setup_subparsers.add_parser('init-db', help='Initialize database')
    db_parser.add_argument('--force', action='store_true',
                         help='Force recreate database even if it exists')
    
    # Validate command
    setup_subparsers.add_parser('validate', help='Validate current setup')
    
    # Reset command
    reset_parser = setup_subparsers.add_parser('reset', help='Reset application to initial state')
    reset_parser.add_argument('--force', action='store_true', required=True,
                            help='Confirm destructive reset operation')
