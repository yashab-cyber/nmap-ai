"""
Configuration management command for NMAP-AI CLI.
Handles application configuration viewing, updating, and validation.
"""
import argparse
import sys
from pathlib import Path
from typing import Dict, Any
import yaml

from nmap_ai.config import load_config, save_config, validate_config
from nmap_ai.utils.logger import get_logger

logger = get_logger(__name__)


def config_command(args: argparse.Namespace) -> int:
    """
    Handle configuration management commands.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        if args.config_action == 'show':
            return show_config(args)
        elif args.config_action == 'set':
            return set_config(args)
        elif args.config_action == 'validate':
            return validate_config_command(args)
        elif args.config_action == 'reset':
            return reset_config(args)
        else:
            logger.error(f"Unknown config action: {args.config_action}")
            return 1
            
    except Exception as e:
        logger.error(f"Configuration command failed: {e}")
        return 1


def show_config(args: argparse.Namespace) -> int:
    """Show current configuration."""
    try:
        config = load_config()
        
        if args.section:
            # Show specific section
            if args.section in config:
                print(f"Configuration section: {args.section}")
                print(yaml.dump({args.section: config[args.section]}, 
                              default_flow_style=False, indent=2))
            else:
                logger.error(f"Configuration section '{args.section}' not found")
                return 1
        else:
            # Show all configuration
            print("Current NMAP-AI Configuration:")
            print("=" * 40)
            print(yaml.dump(config, default_flow_style=False, indent=2))
            
        return 0
        
    except Exception as e:
        logger.error(f"Failed to show configuration: {e}")
        return 1


def set_config(args: argparse.Namespace) -> int:
    """Set configuration value."""
    try:
        config = load_config()
        
        # Parse the key path (e.g., "scanning.timing.aggressive")
        keys = args.key.split('.')
        current = config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
            
        # Set the value
        final_key = keys[-1]
        
        # Try to convert value to appropriate type
        value = args.value
        if value.lower() in ('true', 'false'):
            value = value.lower() == 'true'
        elif value.isdigit():
            value = int(value)
        elif value.replace('.', '').isdigit():
            value = float(value)
            
        current[final_key] = value
        
        # Validate the updated configuration
        if not validate_config(config):
            logger.error("Invalid configuration after update")
            return 1
            
        # Save the configuration
        save_config(config)
        
        print(f"Configuration updated: {args.key} = {value}")
        return 0
        
    except Exception as e:
        logger.error(f"Failed to set configuration: {e}")
        return 1


def validate_config_command(args: argparse.Namespace) -> int:
    """Validate configuration."""
    try:
        config = load_config()
        
        if validate_config(config):
            print("Configuration is valid ✓")
            return 0
        else:
            print("Configuration validation failed ✗")
            return 1
            
    except Exception as e:
        logger.error(f"Failed to validate configuration: {e}")
        return 1


def reset_config(args: argparse.Namespace) -> int:
    """Reset configuration to defaults."""
    try:
        if not args.force:
            response = input("Reset configuration to defaults? This cannot be undone. [y/N]: ")
            if response.lower() not in ('y', 'yes'):
                print("Configuration reset cancelled")
                return 0
                
        # Load default configuration
        from nmap_ai.config import get_default_config
        default_config = get_default_config()
        
        # Save default configuration
        save_config(default_config)
        
        print("Configuration reset to defaults ✓")
        return 0
        
    except Exception as e:
        logger.error(f"Failed to reset configuration: {e}")
        return 1


def add_config_parser(subparsers):
    """Add configuration command parser."""
    config_parser = subparsers.add_parser(
        'config',
        help='Manage application configuration',
        description='View, update, and validate NMAP-AI configuration settings'
    )
    
    config_subparsers = config_parser.add_subparsers(
        dest='config_action',
        help='Configuration actions',
        required=True
    )
    
    # Show configuration
    show_parser = config_subparsers.add_parser(
        'show',
        help='Display current configuration'
    )
    show_parser.add_argument(
        '--section', '-s',
        help='Show specific configuration section'
    )
    
    # Set configuration
    set_parser = config_subparsers.add_parser(
        'set',
        help='Set configuration value'
    )
    set_parser.add_argument(
        'key',
        help='Configuration key (e.g., scanning.timing.aggressive)'
    )
    set_parser.add_argument(
        'value',
        help='Configuration value'
    )
    
    # Validate configuration
    config_subparsers.add_parser(
        'validate',
        help='Validate current configuration'
    )
    
    # Reset configuration
    reset_parser = config_subparsers.add_parser(
        'reset',
        help='Reset configuration to defaults'
    )
    reset_parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Skip confirmation prompt'
    )
    
    return config_parser
