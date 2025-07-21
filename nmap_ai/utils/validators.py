"""
Input validators for NMAP-AI
"""

import re
import ipaddress
from typing import Union


def validate_target(target: str) -> bool:
    """
    Validate if a target is a valid IP address, hostname, or network range.
    
    Args:
        target: Target to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not target or not isinstance(target, str):
        return False
    
    target = target.strip()
    
    # Check for IP address
    try:
        ipaddress.ip_address(target)
        return True
    except ValueError:
        pass
    
    # Check for network range
    try:
        ipaddress.ip_network(target, strict=False)
        return True
    except ValueError:
        pass
    
    # Check for hostname (basic validation)
    hostname_pattern = re.compile(
        r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
    )
    
    if hostname_pattern.match(target):
        return True
    
    # Check for IP range formats like 192.168.1.1-10
    range_pattern = re.compile(r'^(\d+\.\d+\.\d+\.\d+)-(\d+)$')
    if range_pattern.match(target):
        return True
    
    return False


def validate_ports(ports: str) -> bool:
    """
    Validate port specification.
    
    Args:
        ports: Port specification (e.g., '80', '80,443', '1-1000', '80,443,1000-2000')
    
    Returns:
        True if valid, False otherwise
    """
    if not ports or not isinstance(ports, str):
        return False
    
    ports = ports.strip()
    
    # Allow common port keywords
    keywords = ['all', 'top-ports', 'fast']
    if ports.lower() in keywords:
        return True
    
    # Split by comma and validate each part
    port_parts = [part.strip() for part in ports.split(',')]
    
    for part in port_parts:
        if not part:
            continue
        
        # Check for single port
        if part.isdigit():
            port_num = int(part)
            if not (1 <= port_num <= 65535):
                return False
            continue
        
        # Check for port range
        if '-' in part:
            range_parts = part.split('-')
            if len(range_parts) != 2:
                return False
            
            start_port, end_port = range_parts
            if not (start_port.isdigit() and end_port.isdigit()):
                return False
            
            start_num, end_num = int(start_port), int(end_port)
            if not (1 <= start_num <= 65535 and 1 <= end_num <= 65535):
                return False
            
            if start_num >= end_num:
                return False
            
            continue
        
        # Invalid format
        return False
    
    return True


def validate_scan_arguments(arguments: str) -> bool:
    """
    Validate Nmap scan arguments for safety.
    
    Args:
        arguments: Nmap arguments string
    
    Returns:
        True if safe, False if potentially dangerous
    """
    if not arguments:
        return True
    
    # Dangerous argument patterns to avoid
    dangerous_patterns = [
        r'--script.*\.(lua|nse)$',  # Arbitrary script execution
        r'--datadir',               # Custom data directory
        r'--resume',                # Resume from file
        r'-oN\s*/dev/',            # Output to system files
        r'-oX\s*/dev/',
        r'-oG\s*/dev/',
        r'--iflist',               # Interface listing
        r'--packet-trace',         # Packet tracing (can be verbose)
        r'--open',                 # Only show open ports (not dangerous but noteworthy)
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, arguments, re.IGNORECASE):
            return False
    
    return True


def validate_file_path(file_path: str, must_exist: bool = True) -> bool:
    """
    Validate file path.
    
    Args:
        file_path: Path to validate
        must_exist: Whether file must already exist
    
    Returns:
        True if valid, False otherwise
    """
    if not file_path or not isinstance(file_path, str):
        return False
    
    try:
        from pathlib import Path
        path = Path(file_path)
        
        if must_exist:
            return path.exists() and path.is_file()
        else:
            # Check if parent directory exists or can be created
            return path.parent.exists() or path.parent == path.parent.parent
    
    except Exception:
        return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal and invalid characters.
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    if not filename:
        return "unnamed"
    
    # Remove directory traversal attempts
    filename = filename.replace('../', '').replace('..\\', '')
    
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    # Ensure it's not empty
    if not filename.strip():
        filename = "unnamed"
    
    return filename.strip()


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
    
    Returns:
        True if valid format, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    email_pattern = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    return bool(email_pattern.match(email.strip()))


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
    
    Returns:
        True if valid format, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    return bool(url_pattern.match(url.strip()))
