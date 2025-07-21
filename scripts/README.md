# Scripts Directory

This directory contains utility scripts and automation tools for NMAP-AI development and deployment.

## Available Scripts

### Development Scripts
- `setup_dev.sh` - Set up development environment
- `run_tests.sh` - Run complete test suite
- `build.sh` - Build distribution packages
- `lint.sh` - Run code quality checks

### Deployment Scripts  
- `install.sh` - Installation script for Linux/macOS
- `install.bat` - Installation script for Windows
- `docker_build.sh` - Build Docker containers
- `deploy.sh` - Deployment automation

### Utility Scripts
- `backup_data.sh` - Backup user data and configurations
- `update_models.sh` - Update AI models and databases
- `cleanup.sh` - Clean temporary files and caches
- `benchmark.sh` - Performance benchmarking

### Database Scripts
- `init_db.py` - Initialize vulnerability databases
- `update_cve.py` - Update CVE database
- `export_results.py` - Export scan results in various formats

## Usage

Make scripts executable before running:
```bash
chmod +x scripts/*.sh
```

### Development Workflow
```bash
# Set up development environment
./scripts/setup_dev.sh

# Run tests
./scripts/run_tests.sh

# Check code quality  
./scripts/lint.sh

# Build distribution
./scripts/build.sh
```

### Installation
```bash
# Linux/macOS installation
sudo ./scripts/install.sh

# Or using curl
curl -sSL https://raw.githubusercontent.com/yashab-cyber/nmap-ai/main/scripts/install.sh | bash
```

### Maintenance
```bash
# Update vulnerability databases
./scripts/update_models.sh

# Clean temporary files
./scripts/cleanup.sh

# Backup important data
./scripts/backup_data.sh
```

## Script Categories

### Build & Distribution
Scripts for building, packaging, and distributing the application.

### Testing & Quality Assurance  
Automated testing, linting, and code quality verification scripts.

### Database Management
Scripts for managing vulnerability databases and threat intelligence feeds.

### System Administration
Installation, configuration, and maintenance scripts.

### Development Tools
Helper scripts for developers contributing to the project.

## Contributing New Scripts

When adding new scripts:

1. Follow the naming convention: `action_target.ext`
2. Include proper error handling and logging
3. Add usage documentation at the top of each script
4. Make scripts idempotent where possible
5. Test on multiple platforms if applicable
6. Update this README with script description

## Requirements

Some scripts may require additional dependencies:
- `jq` for JSON processing
- `curl` for downloads
- `docker` for containerization
- `git` for repository operations

Install missing dependencies as needed for your platform.
