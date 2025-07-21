# Test Fixtures Directory

This directory contains test fixtures and sample data used across the NMAP-AI test suite.

## Fixture Categories

### Network Data Fixtures
- **sample_networks.json**: Sample network configurations for testing
- **nmap_outputs.xml**: Real nmap XML output samples
- **port_scan_results.json**: Various port scanning result samples
- **network_topologies.yaml**: Network topology definitions

### Vulnerability Data Fixtures
- **cve_samples.json**: Sample CVE data for vulnerability testing
- **vulnerability_reports.xml**: Sample vulnerability scan reports
- **exploit_data.json**: Test exploit information
- **security_alerts.json**: Sample security alert data

### Configuration Fixtures
- **test_configs.yaml**: Various configuration scenarios
- **user_preferences.json**: Sample user preference settings
- **plugin_configs.json**: Plugin configuration samples
- **scan_profiles.yaml**: Predefined scanning profiles

### AI Model Fixtures
- **model_predictions.json**: Sample AI model outputs
- **training_data.csv**: Sample training datasets
- **feature_vectors.json**: Sample feature extraction results
- **classification_results.json**: Sample classification outputs

## File Formats

### JSON Fixtures
- Structured data for API responses
- Configuration samples
- Test result datasets
- Mock service responses

### XML Fixtures
- Nmap XML output samples
- Vulnerability scan reports
- Configuration exports
- Report templates

### CSV Fixtures
- Large dataset samples
- Statistical data for analysis
- Export format examples
- Training data samples

### YAML Fixtures
- Configuration files
- Test scenarios
- Network definitions
- Workflow specifications

## Usage in Tests

```python
import pytest
from tests.fixtures import load_fixture

# Load a JSON fixture
network_data = load_fixture('network_data/sample_networks.json')

# Load XML fixture
nmap_output = load_fixture('nmap_outputs/basic_scan.xml')

# Use with pytest fixtures
@pytest.fixture
def sample_scan_result():
    return load_fixture('scan_results/web_server_scan.json')
```

## Fixture Management

- **Validation**: All fixtures are validated against schemas
- **Version Control**: Fixtures are version controlled for consistency
- **Documentation**: Each fixture includes metadata and documentation
- **Cleanup**: Automated cleanup for temporary test data
