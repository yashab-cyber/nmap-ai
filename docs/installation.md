# Installation Guide

This guide covers installation of NMAP-AI on various platforms and configurations.

## Prerequisites

### System Requirements
- **Operating System**: Linux, macOS, or Windows
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB recommended for AI features)
- **Storage**: 2GB free space
- **Network**: Internet connection for initial setup

### Dependencies
- **Nmap**: 7.0 or higher (required)
- **Python packages**: Listed in requirements.txt
- **Optional**: Docker (for containerized deployment)

## Installation Methods

### Method 1: PyPI Installation (Recommended)

```bash
# Install stable release from PyPI
pip install nmap-ai

# Install with all optional dependencies
pip install nmap-ai[full]

# Install specific components only
pip install nmap-ai[gui]     # GUI components only
pip install nmap-ai[web]     # Web interface only
pip install nmap-ai[ai]      # AI features only
```

### Method 2: From Source

```bash
# Clone repository
git clone https://github.com/yashab-cyber/nmap-ai.git
cd nmap-ai

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Method 3: Automated Installation Script

```bash
# Linux/macOS automated installation
curl -sSL https://raw.githubusercontent.com/yashab-cyber/nmap-ai/main/scripts/install.sh | sudo bash

# Or download and run manually
wget https://raw.githubusercontent.com/yashab-cyber/nmap-ai/main/scripts/install.sh
chmod +x install.sh
sudo ./install.sh
```

### Method 4: Docker Installation

```bash
# Pull pre-built image
docker pull yashabalam/nmap-ai:latest

# Run container
docker run -it --rm yashabalam/nmap-ai:latest

# Run with volume mounting for persistent data
docker run -it --rm -v $(pwd)/data:/app/data yashabalam/nmap-ai:latest

# Run web interface
docker run -d -p 8080:8080 yashabalam/nmap-ai:latest nmap-ai-web
```

## Platform-Specific Instructions

### Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Install system dependencies
sudo apt install -y python3 python3-pip python3-venv nmap git

# Install build dependencies (for some Python packages)
sudo apt install -y build-essential python3-dev libssl-dev libffi-dev

# Install NMAP-AI
pip3 install nmap-ai
```

### CentOS/RHEL/Fedora

```bash
# Install system dependencies
sudo yum install -y python3 python3-pip nmap git  # CentOS 7
# or
sudo dnf install -y python3 python3-pip nmap git  # CentOS 8+/Fedora

# Install development tools
sudo yum groupinstall -y "Development Tools"
sudo yum install -y python3-devel openssl-devel libffi-devel

# Install NMAP-AI
pip3 install nmap-ai
```

### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python3 nmap git

# Install NMAP-AI
pip3 install nmap-ai
```

### Windows

#### Using pip (Recommended)
```powershell
# Install Python from python.org if not installed
# Install Nmap from nmap.org

# Install NMAP-AI
pip install nmap-ai
```

#### Using Chocolatey
```powershell
# Install Chocolatey (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install dependencies
choco install python3 nmap git

# Install NMAP-AI
pip install nmap-ai
```

## Verification

After installation, verify everything is working:

```bash
# Check NMAP-AI version
nmap-ai --version

# Check Nmap is accessible
nmap --version

# Test basic functionality
nmap-ai scan --target 127.0.0.1 --ports 80

# Launch GUI (if GUI dependencies installed)
nmap-ai-gui

# Start web interface
nmap-ai-web --port 8080
```

## Post-Installation Setup

### Initialize AI Models

```bash
# Download and initialize AI models
nmap-ai setup --init-models

# Update vulnerability database
nmap-ai setup --update-db

# Initialize configuration
nmap-ai setup --init-config
```

### Configuration

```bash
# View current configuration
nmap-ai config --show

# Set up custom configuration
cp /opt/nmap-ai/config/default.yaml ~/.nmap-ai/config.yaml
# Edit configuration as needed

# Test configuration
nmap-ai config --validate
```

## Troubleshooting

### Common Issues

#### "nmap command not found"
```bash
# Install nmap
sudo apt install nmap  # Ubuntu/Debian
brew install nmap      # macOS
choco install nmap     # Windows
```

#### Permission Errors
```bash
# Linux/macOS: Use virtual environment or user install
pip install --user nmap-ai

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install nmap-ai
```

#### Import Errors
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt

# Check for missing system libraries
# Ubuntu/Debian:
sudo apt install python3-dev build-essential

# CentOS/RHEL:
sudo yum install python3-devel gcc
```

#### AI Model Download Issues
```bash
# Manual model download
nmap-ai setup --init-models --force

# Or download to specific directory
nmap-ai setup --init-models --model-dir /path/to/models
```

### Diagnostic Commands

```bash
# System information
nmap-ai info

# Check dependencies
nmap-ai setup --check

# View logs
nmap-ai logs --tail 50

# Test network connectivity
nmap-ai test --network
```

## Uninstallation

### pip Installation
```bash
pip uninstall nmap-ai

# Remove user data (optional)
rm -rf ~/.nmap-ai/
```

### Script Installation
```bash
# Run uninstall script
sudo /opt/nmap-ai/scripts/uninstall.sh

# Manual cleanup
sudo rm -rf /opt/nmap-ai/
sudo rm /usr/local/bin/nmap-ai*
```

### Docker
```bash
# Remove container
docker rm nmap-ai-container

# Remove image
docker rmi yashabalam/nmap-ai:latest
```

## Development Installation

For developers who want to contribute:

```bash
# Clone repository
git clone https://github.com/yashab-cyber/nmap-ai.git
cd nmap-ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Run tests
pytest tests/
```

---

**Next Steps:**
- Continue to [Usage Guide](usage.md) for usage examples
- See [Configuration](../config/README.md) for configuration options
- Check [Examples](../examples/README.md) for practical examples
