# Configuration Directory

This directory contains configuration files and templates for NMAP-AI.

## Structure

- `default.yaml` - Default application configuration
- `profiles/` - Predefined scanning profiles
- `templates/` - Configuration templates for different use cases
- `schemas/` - Configuration validation schemas
- `examples/` - Example configurations for reference

## Configuration Files

### Main Configuration (`default.yaml`)
The primary configuration file that defines application behavior:

```yaml
# Application settings
app:
  name: "NMAP-AI"
  version: "1.0.0"
  debug: false
  
# Scanning configuration
scanning:
  default_timeout: 300
  max_threads: 20
  default_ports: "1-1000"
  
# AI settings
ai:
  enable_smart_scanning: true
  enable_vulnerability_detection: true
  enable_script_generation: true
  model_path: "data/models/"
  
# Output settings
output:
  default_format: "json"
  save_raw_results: true
  results_directory: "results/"
  
# Logging configuration
logging:
  level: "INFO"
  file: "logs/nmap-ai.log"
  max_size: "10MB"
  backup_count: 5
```

### Scanning Profiles (`profiles/`)
Pre-configured scanning profiles for different scenarios:

- `quick.yaml` - Fast basic scanning
- `comprehensive.yaml` - Thorough full scanning
- `stealth.yaml` - Stealthy scanning methods
- `vulnerability.yaml` - Vulnerability-focused scanning
- `web.yaml` - Web application scanning
- `internal.yaml` - Internal network scanning

### Configuration Templates (`templates/`)
Template files for different deployment scenarios:

- `production.yaml.template` - Production environment settings
- `development.yaml.template` - Development environment settings
- `enterprise.yaml.template` - Enterprise deployment settings
- `minimal.yaml.template` - Minimal configuration template

## Using Configurations

### Loading Configuration
```python
from nmap_ai.config import Config

# Load default configuration
config = Config()

# Load custom configuration file
config = Config('config/custom.yaml')

# Load configuration with profile
config = Config(profile='stealth')
```

### Environment Variables
Configuration can be overridden with environment variables:

```bash
export NMAP_AI_DEBUG=true
export NMAP_AI_THREADS=10
export NMAP_AI_LOG_LEVEL=DEBUG

python -m nmap_ai
```

### Command Line Override
```bash
# Override configuration via CLI
python -m nmap_ai --config config/custom.yaml --threads 15
```

## Configuration Profiles

### Quick Scan Profile (`profiles/quick.yaml`)
```yaml
scanning:
  timeout: 60
  ports: "--top-ports 100"
  timing: "-T4"
  scripts: []
  
ai:
  enable_smart_scanning: false
  enable_script_generation: false
  
output:
  format: "json"
  detailed: false
```

### Comprehensive Scan Profile (`profiles/comprehensive.yaml`)
```yaml
scanning:
  timeout: 1800
  ports: "-p-"
  timing: "-T3"
  scripts: ["default", "vuln", "auth"]
  service_detection: true
  os_detection: true
  
ai:
  enable_smart_scanning: true
  enable_script_generation: true
  enable_vulnerability_detection: true
  
output:
  format: ["json", "html", "pdf"]
  detailed: true
  include_raw: true
```

### Stealth Scan Profile (`profiles/stealth.yaml`)
```yaml
scanning:
  timeout: 3600
  ports: "-p 1-1000"
  timing: "-T1"
  scan_type: "-sS"
  fragmentation: "-f"
  decoy: "--decoy"
  
ai:
  enable_smart_scanning: true
  adaptive_timing: true
  
output:
  format: "json"
  minimize_logging: true
```

## Validation Schemas

Configuration files are validated against JSON schemas in `schemas/`:

- `config.schema.json` - Main configuration schema
- `profile.schema.json` - Scanning profile schema
- `ai.schema.json` - AI settings schema

## Creating Custom Configurations

### Steps to Create Custom Config
1. Copy a template file from `templates/`
2. Modify settings for your environment
3. Validate against schema
4. Test with a small scan
5. Deploy to production

### Configuration Best Practices
- Use environment-specific configurations
- Keep sensitive data in environment variables
- Validate configurations before deployment
- Document custom settings
- Use version control for configuration files

## Environment-Specific Configurations

### Development (`templates/development.yaml.template`)
```yaml
app:
  debug: true
  
scanning:
  timeout: 120
  max_threads: 5
  
logging:
  level: "DEBUG"
  console_output: true
  
ai:
  cache_models: false
```

### Production (`templates/production.yaml.template`)  
```yaml
app:
  debug: false
  
scanning:
  timeout: 600
  max_threads: 20
  
logging:
  level: "WARNING"
  console_output: false
  syslog: true
  
security:
  encrypt_results: true
  secure_temp_files: true
```

## Security Considerations

- Store sensitive credentials in environment variables
- Encrypt configuration files containing sensitive data
- Use proper file permissions (600) for config files
- Audit configuration changes
- Avoid hardcoding secrets in configuration files

## Troubleshooting

### Common Issues
1. **Invalid YAML syntax** - Use YAML validator
2. **Missing required fields** - Check against schema
3. **File permission errors** - Verify file permissions
4. **Environment variable conflicts** - Check variable precedence
5. **Profile not found** - Verify profile file exists

### Validation Commands
```bash
# Validate configuration file
python -m nmap_ai.config.validate config/custom.yaml

# Test configuration
python -m nmap_ai --config config/custom.yaml --dry-run

# Show effective configuration
python -m nmap_ai --show-config
```

## Migration

When upgrading NMAP-AI, configuration files may need updates:

1. Backup existing configuration
2. Compare with new default configuration
3. Update deprecated settings
4. Test migrated configuration
5. Deploy updated configuration

Migration scripts are available in `scripts/migrate_config.py`.
