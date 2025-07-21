"""
Helper utilities for NMAP-AI
"""

import json
import time
import hashlib
import platform
import subprocess
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path


def get_system_info() -> Dict[str, str]:
    """Get system information."""
    return {
        'platform': platform.system(),
        'platform_version': platform.version(),
        'architecture': platform.machine(),
        'python_version': platform.python_version(),
        'hostname': platform.node()
    }


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable format."""
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"


def format_bytes(bytes_count: int) -> str:
    """Format bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} PB"


def get_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
    """Get hash of a file."""
    hash_algo = hashlib.new(algorithm)
    
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_algo.update(chunk)
        return hash_algo.hexdigest()
    except Exception as e:
        raise ValueError(f"Could not hash file {file_path}: {e}")


def ensure_directory(directory: str) -> Path:
    """Ensure directory exists, create if it doesn't."""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_json_load(file_path: str) -> Optional[Dict[str, Any]]:
    """Safely load JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception:
        return None


def safe_json_save(data: Dict[str, Any], file_path: str) -> bool:
    """Safely save data to JSON file."""
    try:
        ensure_directory(str(Path(file_path).parent))
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception:
        return False


def is_nmap_installed() -> bool:
    """Check if Nmap is installed and accessible."""
    try:
        result = subprocess.run(['nmap', '--version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def get_nmap_version() -> Optional[str]:
    """Get installed Nmap version."""
    try:
        result = subprocess.run(['nmap', '--version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        if result.returncode == 0:
            # Extract version from output
            for line in result.stdout.split('\n'):
                if 'Nmap version' in line:
                    return line.split('version')[1].strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def parse_port_range(port_spec: str) -> List[int]:
    """Parse port specification into list of ports."""
    ports = []
    
    for part in port_spec.split(','):
        part = part.strip()
        
        if '-' in part:
            start, end = part.split('-', 1)
            start, end = int(start.strip()), int(end.strip())
            ports.extend(range(start, end + 1))
        else:
            ports.append(int(part))
    
    return sorted(list(set(ports)))  # Remove duplicates and sort


def generate_report_id() -> str:
    """Generate unique report ID."""
    timestamp = int(time.time())
    random_part = hashlib.md5(str(timestamp).encode()).hexdigest()[:8]
    return f"report_{timestamp}_{random_part}"


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string to maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def merge_dictionaries(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries, with later ones taking precedence."""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def retry_operation(func, max_retries: int = 3, delay: float = 1.0):
    """Retry an operation with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(delay * (2 ** attempt))


def clean_old_files(directory: str, max_age_days: int = 7, pattern: str = "*"):
    """Clean old files from directory."""
    directory_path = Path(directory)
    if not directory_path.exists():
        return
    
    cutoff_time = datetime.now() - timedelta(days=max_age_days)
    
    for file_path in directory_path.glob(pattern):
        if file_path.is_file():
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_time < cutoff_time:
                try:
                    file_path.unlink()
                except Exception:
                    pass  # Ignore errors when cleaning up


def get_available_memory() -> Optional[int]:
    """Get available system memory in bytes."""
    try:
        import psutil
        return psutil.virtual_memory().available
    except ImportError:
        return None


def is_port_open(host: str, port: int, timeout: float = 3.0) -> bool:
    """Check if a port is open on a host."""
    import socket
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            return result == 0
    except Exception:
        return False


def parse_nmap_xml(xml_content: str) -> Dict[str, Any]:
    """Parse Nmap XML output."""
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml_content)
        
        results = {
            'hosts': [],
            'scan_info': {},
            'run_stats': {}
        }
        
        # Parse scan info
        scaninfo = root.find('scaninfo')
        if scaninfo is not None:
            results['scan_info'] = {
                'type': scaninfo.get('type', ''),
                'protocol': scaninfo.get('protocol', ''),
                'numservices': scaninfo.get('numservices', ''),
                'services': scaninfo.get('services', '')
            }
        
        # Parse hosts
        for host in root.findall('host'):
            host_info = {
                'addresses': [],
                'hostnames': [],
                'status': {},
                'ports': []
            }
            
            # Status
            status = host.find('status')
            if status is not None:
                host_info['status'] = {
                    'state': status.get('state', ''),
                    'reason': status.get('reason', '')
                }
            
            # Addresses
            for address in host.findall('address'):
                host_info['addresses'].append({
                    'addr': address.get('addr', ''),
                    'addrtype': address.get('addrtype', '')
                })
            
            # Hostnames
            hostnames = host.find('hostnames')
            if hostnames is not None:
                for hostname in hostnames.findall('hostname'):
                    host_info['hostnames'].append({
                        'name': hostname.get('name', ''),
                        'type': hostname.get('type', '')
                    })
            
            # Ports
            ports = host.find('ports')
            if ports is not None:
                for port in ports.findall('port'):
                    port_info = {
                        'protocol': port.get('protocol', ''),
                        'portid': port.get('portid', ''),
                        'state': {},
                        'service': {}
                    }
                    
                    # Port state
                    state = port.find('state')
                    if state is not None:
                        port_info['state'] = {
                            'state': state.get('state', ''),
                            'reason': state.get('reason', '')
                        }
                    
                    # Service info
                    service = port.find('service')
                    if service is not None:
                        port_info['service'] = {
                            'name': service.get('name', ''),
                            'product': service.get('product', ''),
                            'version': service.get('version', ''),
                            'extrainfo': service.get('extrainfo', '')
                        }
                    
                    host_info['ports'].append(port_info)
            
            results['hosts'].append(host_info)
        
        # Parse run stats
        runstats = root.find('runstats')
        if runstats is not None:
            finished = runstats.find('finished')
            if finished is not None:
                results['run_stats'] = {
                    'time': finished.get('time', ''),
                    'timestr': finished.get('timestr', ''),
                    'elapsed': finished.get('elapsed', '')
                }
        
        return results
        
    except Exception as e:
        raise ValueError(f"Could not parse XML content: {e}")


def create_backup(file_path: str) -> str:
    """Create backup of a file."""
    original_path = Path(file_path)
    if not original_path.exists():
        raise FileNotFoundError(f"File {file_path} does not exist")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = original_path.with_suffix(f".backup_{timestamp}{original_path.suffix}")
    
    import shutil
    shutil.copy2(original_path, backup_path)
    
    return str(backup_path)
