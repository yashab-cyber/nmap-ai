# NMAP-AI Documentation

Welcome to the NMAP-AI documentation! This guide will help you get started with AI-powered network scanning and automation.

## Quick Start

### Installation
```bash
# Install from PyPI
pip install nmap-ai

# Or install from source
git clone https://github.com/yashab-cyber/nmap-ai.git
cd nmap-ai
pip install -r requirements.txt
```

### Basic Usage
```bash
# CLI scanning
nmap-ai scan --target 192.168.1.0/24 --ports "22,80,443"

# Launch GUI
nmap-ai-gui

# Start web interface
nmap-ai-web --port 8080
```

## Features

### 🤖 AI-Powered Capabilities
- **Smart Scanning**: AI optimizes scan parameters based on target analysis
- **Script Generation**: Automatically generates custom Nmap scripts
- **Vulnerability Detection**: AI-driven vulnerability identification
- **Adaptive Scanning**: Dynamic parameter adjustment based on responses

### 📊 Multiple Interfaces
- **Command Line Interface**: Full-featured CLI with automation support
- **Graphical Interface**: Modern Qt-based GUI with real-time visualization
- **Web Dashboard**: Browser-based interface for remote management
- **REST API**: Programmatic access for integration

### 🛡️ Security Features
- **Offline AI Models**: No data sent to external services
- **Encrypted Storage**: Secure storage of scan results
- **Audit Logging**: Complete activity logging
- **Role-based Access**: Multi-user support with permissions

## Use Cases

### Network Discovery
- Automated network topology mapping
- Service detection and fingerprinting
- Operating system identification
- Port scanning and analysis

### Security Assessment
- Vulnerability scanning and reporting
- Configuration analysis
- Security audit automation
- Compliance checking

### Penetration Testing
- Custom script generation for specific targets
- Automated reconnaissance
- Exploit identification
- Report generation

## Documentation Structure

- **[Installation Guide](installation.md)** - Detailed installation instructions
- **[Usage Guide](usage.md)** - Comprehensive usage examples
- **[API Reference](api.md)** - Complete API documentation
- **[Configuration](../config/README.md)** - Configuration options
- **[Examples](../examples/README.md)** - Example scripts and workflows

## Getting Help

- 📖 **Documentation**: Browse the guides in this directory
- 🐛 **Issues**: Report bugs on [GitHub Issues](https://github.com/yashab-cyber/nmap-ai/issues)
- 💬 **Discussions**: Join the community on [GitHub Discussions](https://github.com/yashab-cyber/nmap-ai/discussions)
- 📧 **Contact**: Email yashabalam707@gmail.com

## Contributing

We welcome contributions! Please see our [Contributing Guide](../CONTRIBUTING.md) for details on:

- Code contributions
- Documentation improvements
- Bug reports
- Feature requests
- Testing

## License

NMAP-AI is licensed under the MIT License. See [LICENSE](../LICENSE) for details.

---

**Next Steps:**
1. Follow the [Installation Guide](installation.md) to get started
2. Try the examples in [Usage Guide](usage.md)  
3. Explore the [API Reference](api.md) for advanced usage
