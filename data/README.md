# Data Directory

This directory contains data files used by NMAP-AI including AI models, vulnerability databases, and configuration data.

## Structure

- `models/` - AI/ML model files and weights
- `databases/` - Vulnerability and threat intelligence databases
- `configs/` - Default configuration templates
- `cache/` - Cached scan results and temporary files
- `exports/` - Exported reports and scan results
- `logs/` - Application log files

## Contents

### AI Models
- Pre-trained models for vulnerability detection
- Script generation models
- Network analysis models
- Custom trained models for specific environments

### Databases
- CVE vulnerability database
- Port/service fingerprint database  
- Exploit database references
- Threat intelligence feeds

### Cache Files
- Cached nmap scan results
- AI model inference cache
- Network topology cache
- User session data

## File Management

### Automatic Cleanup
The application automatically manages cache files and old logs:
- Cache files older than 7 days are automatically removed
- Log files are rotated and compressed
- Temporary scan files are cleaned after processing

### Manual Cleanup
```bash
# Clean all cache files
python -m nmap_ai.utils.cleanup --cache

# Clean old logs
python -m nmap_ai.utils.cleanup --logs

# Clean everything
python -m nmap_ai.utils.cleanup --all
```

## Security Considerations

- All data is stored locally - no data sent to external services
- Sensitive scan results are encrypted at rest
- Database files are protected with appropriate permissions
- Logs are sanitized to remove sensitive information

## Backup Recommendations

Important data files to backup:
- Custom AI models in `models/custom/`
- Configuration files in `configs/`
- Historical scan results in `exports/`
- Custom vulnerability signatures

## Storage Requirements

Typical storage usage:
- AI Models: ~500MB
- Vulnerability DB: ~100MB
- Cache (varies): 10MB-1GB
- Logs (varies): 10MB-100MB

## Data Privacy

- All data remains on local system
- No telemetry or usage data collected
- Scan results are never transmitted externally
- User configuration stays private
