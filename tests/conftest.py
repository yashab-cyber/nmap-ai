"""
Test configuration for NMAP-AI pytest setup.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import os
import sys

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from nmap_ai.config import Config
from nmap_ai.utils.logger import get_logger


@pytest.fixture(scope="session")
def test_config():
    """Create a test configuration for all tests."""
    config = Config()
    config.data_dir = tempfile.mkdtemp(prefix="nmap_ai_test_")
    config.log_level = "DEBUG"
    config.debug = True
    return config


@pytest.fixture(scope="session")  
def temp_data_dir(test_config):
    """Create temporary data directory for tests."""
    data_dir = Path(test_config.data_dir)
    data_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    (data_dir / "models").mkdir(exist_ok=True)
    (data_dir / "databases").mkdir(exist_ok=True)
    (data_dir / "cache").mkdir(exist_ok=True)
    (data_dir / "logs").mkdir(exist_ok=True)
    
    yield data_dir
    
    # Cleanup after all tests
    shutil.rmtree(str(data_dir), ignore_errors=True)


@pytest.fixture
def sample_nmap_xml():
    """Sample nmap XML output for testing."""
    return """<?xml version="1.0"?>
<nmaprun scanner="nmap" version="7.80" xmloutputversion="1.04">
    <host>
        <address addr="192.168.1.1" addrtype="ipv4"/>
        <status state="up"/>
        <ports>
            <port protocol="tcp" portid="22">
                <state state="open"/>
                <service name="ssh" product="OpenSSH" version="7.4"/>
            </port>
            <port protocol="tcp" portid="80">
                <state state="open"/>
                <service name="http" product="Apache" version="2.4.6"/>
            </port>
            <port protocol="tcp" portid="443">
                <state state="open"/>
                <service name="https" product="Apache" version="2.4.6"/>
            </port>
        </ports>
    </host>
</nmaprun>"""


@pytest.fixture
def sample_scan_results():
    """Sample parsed scan results for testing."""
    return {
        'scan': {
            'target': '192.168.1.1',
            '192.168.1.1': {
                'status': {'state': 'up'},
                'tcp': {
                    22: {
                        'state': 'open',
                        'name': 'ssh',
                        'product': 'OpenSSH',
                        'version': '7.4'
                    },
                    80: {
                        'state': 'open', 
                        'name': 'http',
                        'product': 'Apache',
                        'version': '2.4.6'
                    },
                    443: {
                        'state': 'open',
                        'name': 'https', 
                        'product': 'Apache',
                        'version': '2.4.6'
                    }
                }
            }
        }
    }


@pytest.fixture
def mock_vulnerability_data():
    """Mock vulnerability data for testing."""
    return [
        {
            'cve_id': 'CVE-2018-15473',
            'severity': 'medium',
            'score': 5.3,
            'description': 'SSH username enumeration vulnerability',
            'service': 'ssh',
            'version_affected': 'OpenSSH 7.4'
        },
        {
            'cve_id': 'CVE-2017-15715',
            'severity': 'high', 
            'score': 7.5,
            'description': 'Apache HTTP Server vulnerability',
            'service': 'http',
            'version_affected': 'Apache 2.4.6'
        }
    ]


@pytest.fixture
def logger():
    """Get a test logger instance."""
    return get_logger("test", level="DEBUG")


# Test markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "network: marks tests that require network access"
    )
    config.addinivalue_line(
        "markers", "ai: marks tests that use AI models"
    )


# Skip tests based on availability
def pytest_runtest_setup(item):
    """Skip tests based on markers and system availability."""
    # Skip network tests if no network access
    if "network" in item.keywords:
        pytest.importorskip("requests")
        
    # Skip AI tests if AI dependencies not available
    if "ai" in item.keywords:
        try:
            import tensorflow
            import torch
        except ImportError:
            pytest.skip("AI dependencies not available")


# Timeout for slow tests
def pytest_timeout_set_timer(item, timeout):
    """Set timeout for tests."""
    if "slow" in item.keywords:
        return max(timeout, 300)  # 5 minutes for slow tests
    return timeout
