# Examples Directory

This directory contains example scripts, configuration files, and usage demonstrations for NMAP-AI.

## Contents

### Basic Examples
- `basic_scan.py` - Simple network scan example
- `vulnerability_scan.py` - Vulnerability detection example  
- `ai_script_generation.py` - AI-powered script generation
- `report_generation.py` - Generating scan reports

### Advanced Examples
- `custom_plugin.py` - Creating custom scanning plugins
- `automation_workflow.py` - Automated scanning workflows
- `integration_example.py` - Integrating with other tools
- `bulk_scanning.py` - Scanning multiple targets

### Configuration Examples
- `config_examples/` - Sample configuration files
- `custom_profiles/` - Custom scanning profiles
- `ai_model_configs/` - AI model configuration examples

### API Examples
- `rest_api_client.py` - REST API usage examples
- `web_integration.py` - Web interface integration
- `cli_automation.py` - CLI automation scripts

## Quick Start Examples

### Basic Network Scan
```python
from nmap_ai import NmapAIScanner

# Initialize scanner
scanner = NmapAIScanner()

# Perform basic scan
results = scanner.scan("192.168.1.1-10", ports="22,80,443")

# Print results
for host in results:
    print(f"Host: {host.ip}")
    for port in host.open_ports:
        print(f"  Port {port.number}: {port.service}")
```

### AI-Powered Vulnerability Detection
```python
from nmap_ai import SmartScanner, VulnerabilityDetector

# Smart scanning with AI
scanner = SmartScanner()
scan_results = scanner.intelligent_scan("target.example.com")

# AI vulnerability analysis
detector = VulnerabilityDetector()
vuln_report = detector.analyze_scan_results(scan_results)

# Generate report
report = detector.export_report(vuln_report, format='html')
with open('vulnerability_report.html', 'w') as f:
    f.write(report)
```

### Custom Script Generation
```python
from nmap_ai import AIScriptGenerator

# Generate custom nmap script using AI
generator = AIScriptGenerator()

# Describe what you want to scan for
description = "Detect vulnerable SSH configurations and weak ciphers"

# Generate custom script
custom_script = generator.generate_script(
    target_service="ssh",
    description=description,
    security_focus=True
)

print("Generated Nmap Script:")
print(custom_script)
```

## Running Examples

### Prerequisites
```bash
# Install NMAP-AI
pip install -r requirements.txt

# Ensure nmap is installed
nmap --version
```

### Basic Usage
```bash
# Run basic examples
python examples/basic_scan.py

# Run with custom target
python examples/basic_scan.py --target 192.168.1.0/24

# Run vulnerability scan
python examples/vulnerability_scan.py --target example.com
```

### Advanced Usage
```bash
# Custom workflow
python examples/automation_workflow.py --config examples/config_examples/advanced.yaml

# Bulk scanning
python examples/bulk_scanning.py --targets targets.txt --output results/
```

## Configuration Examples

### Basic Configuration (`config_examples/basic.yaml`)
```yaml
scanning:
  default_ports: "1-1000"
  timeout: 300
  threads: 10

ai:
  enable_smart_scanning: true
  enable_script_generation: true
  vulnerability_detection: true

output:
  format: ["json", "html"]
  directory: "results/"
  
logging:
  level: "INFO"
  file: "nmap-ai.log"
```

### Advanced Configuration (`config_examples/advanced.yaml`)
```yaml
scanning:
  profiles:
    quick: "--top-ports 100 -T4"
    thorough: "-p- -sV -sC -T3"
    stealth: "-sS -T1 -f"
  
  custom_scripts:
    - "vuln"
    - "auth"
    - "discovery"

ai:
  models:
    vulnerability_model: "models/vuln_detector_v2.pkl"
    script_generator: "models/script_gen_v1.pkl"
  
  thresholds:
    vulnerability_confidence: 0.8
    script_relevance: 0.7

notifications:
  email:
    enabled: true
    smtp_server: "smtp.example.com"
    recipients: ["admin@example.com"]
  
  slack:
    enabled: false
    webhook_url: "https://hooks.slack.com/..."
```

## Integration Examples

### With Security Tools
- SIEM integration example
- Vulnerability scanner integration
- Threat intelligence platform integration

### With Automation Platforms
- Ansible playbook integration
- Jenkins CI/CD integration
- Python automation frameworks

### With Databases
- PostgreSQL result storage
- MongoDB document storage
- Elasticsearch logging integration

## Contributing Examples

When contributing new examples:

1. Include clear documentation
2. Add error handling
3. Use realistic but safe targets
4. Include configuration files if needed
5. Test examples thoroughly
6. Update this README

## Safety Notes

⚠️ **Important**: 
- Only scan networks you own or have permission to test
- Use test environments for examples
- Be mindful of rate limits and network impact
- Follow responsible disclosure for any vulnerabilities found

## Support

If you need help with examples:
1. Check the main documentation
2. Review error messages carefully
3. Ensure all dependencies are installed
4. Open an issue on GitHub with example-specific questions
