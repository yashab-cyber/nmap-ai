# 🚀 NMAP-AI: AI-Powered Network Scanning & Automation

<div align="center">
  <img src="assets/nmap-ai.png" alt="NMAP-AI Logo" width="200" height="200">
</div>

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey.svg)

> **🤖 A heuristic-driven wrapper around Nmap with rule-based scan optimization, NSE script scaffolding, and an extensible plugin system. (The "AI" today is rule-based — a real ML layer is on the roadmap, not in the box.)**

## 📋 Table of Contents

- [🌟 Features](#-features)
- [🚀 Installation](#-installation)
- [💻 Usage](#-usage)
- [🤖 AI Capabilities](#-ai-capabilities)
- [📱 GUI Mode](#-gui-mode)
- [⌨️ CLI Mode](#-cli-mode)
- [🛠️ Configuration](#-configuration)
- [🤝 Contributing](#-contributing)
- [💰 Support](#-support)
- [📄 License](#-license)

## 🌟 Features

### 🤖 Heuristic Scan Intelligence
- **Template-Driven Script Scaffolding**: Generates Nmap NSE script skeletons from target type + vulnerability hints (Lua boilerplate + test placeholders — *real exploit logic is still on the roadmap*)
- **Rule-Based Scan Argument Optimization**: Picks Nmap timing, OS-detection, and script-category flags based on target count and naming heuristics
- **Pattern-Based Vulnerability Hints**: Flags known-risky ports/services (Telnet, FTP, SMB, etc.) and surfaces remediation suggestions from a hardcoded rule table
- **Adaptive Profiles**: `fast` / `thorough` / `stealth` / `adaptive` profiles that tune ports and timing per scan

### 🖥️ User Interfaces
- **CLI**: Click-based command-line interface (`scan`, `smart-scan`, `generate-script`, `batch`, `history`) — *working*
- **GUI**: *not available yet* — `--gui` exits with a pointer to the CLI (desktop UI is on the roadmap)
- **Web**: FastAPI server with `/health` and `/api/v1/status` endpoints — *scan/results endpoints planned*

### 🔧 Scanning Features
- **Async Batch Scanning**: Concurrent multi-host scans via `asyncio.Semaphore`
- **Pluggable Architecture**: `BasePlugin` / `ScannerPlugin` / `ReportPlugin` / `AIPlugin` extension points
- **JSON Output**: Structured scan results (XML/CSV output is stubbed, on the roadmap)

### 🛡️ Security & Privacy
- **Fully Offline**: No external API calls — all analysis is local
- **Audit Logging**: Activity logging via the built-in logger

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Nmap 7.0+
- Git

### Quick Installation

```bash
# Clone the repository
git clone https://github.com/yashab-cyber/nmap-ai.git
cd nmap-ai

# Install dependencies
pip install -r requirements.txt

# Install Nmap (if not already installed)
sudo apt-get install nmap  # Ubuntu/Debian
sudo yum install nmap      # CentOS/RHEL
brew install nmap          # macOS

# Run the application
python -m nmap_ai
```

### Docker Installation

> **Note**: The Docker image is currently being set up on Docker Hub. Until it's available, you can build the image locally using the instructions below.

**Option 1: Pull from Docker Hub (Coming Soon)**
```bash
docker pull yashabalam/nmap-ai:latest
docker run -it --rm yashabalam/nmap-ai:latest
```

**Option 2: Build Locally (Current Recommended Method)**
```bash
# Clone the repository
git clone https://github.com/yashab-cyber/nmap-ai.git
cd nmap-ai

# Build and run using Docker Compose
docker-compose up nmap-ai

# Or build manually
./scripts/docker_build.sh build-prod
docker run -it --rm -p 8080:8080 yashabalam/nmap-ai:latest
```

**Option 3: Using Docker with Volume Mounts**
```bash
# For persistent data
docker run -it --rm \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/results:/app/results \
  yashabalam/nmap-ai:latest
```

## 💻 Usage

### 🖥️ GUI Mode *(not available yet)*

The desktop GUI is on the roadmap. `python -m nmap_ai --gui` currently exits
with a message pointing you to the CLI below. See [roadmap.md](roadmap.md).

### ⌨️ CLI Mode

```bash
# Basic Heuristic-driven scan
nmap-ai --target 192.168.1.0/24 --ai-mode smart

# Generate custom script with AI
nmap-ai --generate-script --target example.com --vulnerability web

# Advanced port scan with ML optimization
nmap-ai --target 10.0.0.1 --ports all --ai-optimize --output report.json

# Batch scanning with AI analysis
nmap-ai --batch targets.txt --ai-analysis --format pdf
```

### 🌐 Web Dashboard

```bash
# Set a secret key (required outside debug mode — the server refuses to
# start with the built-in default)
export NMAP_AI_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"

# Start web server
nmap-ai --web --port 8080

# Access dashboard at http://localhost:8080
```

## 🤖 Heuristic Capabilities

### 🧠 Template-Driven Script Scaffolding

NMAP-AI generates Nmap NSE script skeletons from a target-type template + vulnerability hints. The output is valid Lua scaffolding — the actual exploit/check logic is left as TODO placeholders for the operator to fill in:

```python
from nmap_ai import AIScriptGenerator

generator = AIScriptGenerator()

# Generate script for web application testing
script = generator.create_script(
    target_type="web_server",
    vulnerabilities=["sql_injection", "xss", "directory_traversal"],
    stealth_level="high"
)

# Generate script for network device scanning
network_script = generator.create_script(
    target_type="network_device",
    device_types=["router", "switch", "firewall"],
    protocols=["snmp", "ssh", "telnet"]
)
```

### 🔍 Heuristic Scan Planning

```python
from nmap_ai import SmartScanner

scanner = SmartScanner()

# Rule-based scan-argument optimization
results = scanner.smart_scan(
    target="192.168.1.0/24",
    optimization_level="aggressive"
)

# Adaptive scanning that learns from in-memory scan history
adaptive_results = scanner.adaptive_scan(
    target="example.com",
    learn_from_previous=True,
    adjust_timing=True
)
```

> The `ai_model` argument from prior README versions is removed — there are no model files loaded at runtime. Behavior is driven by the rule tables in `nmap_ai/core/ai_engine.py`.

## 📱 GUI (Planned)

> The GUI is not implemented yet — `--gui` exits with a pointer to the CLI. The following are roadmap items, not shipping features. See [roadmap.md](roadmap.md) for sequencing.

- Real-time scan progress visualization
- Interactive network topology maps
- Vulnerability explanation and remediation suggestions
- Customizable report templates + PDF / HTML / DOCX export

## ⌨️ CLI Advanced Usage

### Scripting and Automation

```bash
# Async scan of many targets in parallel
python -m nmap_ai scan 10.0.0.1 10.0.0.2 10.0.0.3 --async-scan --max-concurrent 20

# Batch scan from a file of targets, JSON output
python -m nmap_ai batch targets.txt --output results.json --format json

# Smart-scan profiles (adaptive | fast | thorough | stealth)
python -m nmap_ai smart-scan 192.168.1.0/24 --profile thorough

# Pipe results to jq
python -m nmap_ai scan 10.0.0.1 -o /dev/stdout | jq '.results'
```

> Profile creation, custom-model loading, cron-style scheduling, and email notifications shown in earlier README versions are not implemented. See [roadmap.md](roadmap.md).

### Advanced Configuration

```yaml
# ~/.nmap-ai/config.yml — fields match the dataclasses in nmap_ai/config.py
ai:
  confidence_threshold: 0.7   # heuristic risk-flag threshold

scanning:
  default_timeout: 300
  max_parallel_hosts: 50
  retries: 3
  default_ports: "1-1000"
  stealth_mode: false
  timing_template: 3

output:
  default_format: json
  include_raw_nmap: true
  compress_results: true
  output_directory: results

web:
  host: localhost
  port: 8080
```

> Notifications (email/webhook), encrypted storage, and role-based access are listed on the roadmap, not implemented today.

## 🛠️ Plugin System

NMAP-AI supports a flexible plugin architecture:

```python
# plugins/custom_scanner.py
from nmap_ai.plugins import BasePlugin

class CustomVulnScanner(BasePlugin):
    name = "Custom Vulnerability Scanner"
    version = "1.0.0"
    
    def scan(self, target, options):
        # Custom scanning logic
        return results
    
    def generate_script(self, requirements):
        # Custom script generation
        return script_code
```

## 🔧 API Reference

### REST API Endpoints — Current

| Endpoint | Status |
|---|---|
| `GET /health` | ✅ working |
| `GET /api/v1/status` | ✅ working |
| `GET /docs` | ✅ FastAPI auto-docs |
| `POST /api/v1/scan` | 🚧 returns 501 — planned |
| `GET /api/v1/results/{scan_id}` | 🚧 returns 501 — planned |

See [roadmap.md](roadmap.md) Phase 1 for the plan to wire the scan endpoints up against `NmapAIScanner`.

## 🎯 Use Cases

### 🏢 Enterprise Security
- **Automated Asset Discovery**: Heuristic-driven identification of network assets
- **Compliance Scanning**: Automated checks for security compliance
- **Threat Hunting**: Proactive identification of potential threats
- **Vulnerability Management**: Continuous vulnerability assessment

### 🎓 Education & Research
- **Security Training**: Interactive learning environment
- **Research Projects**: Advanced scanning capabilities for academic research
- **Penetration Testing**: Professional-grade testing tools
- **Network Analysis**: Deep network behavior analysis

### 🔒 Penetration Testing
- **Reconnaissance Automation**: Rule-based information gathering
- **Custom Exploit Development**: Script generation for specific targets
- **Stealth Scanning**: Advanced evasion techniques
- **Report Generation**: Professional penetration testing reports

## 🚀 Roadmap

### Version 1.1 (Q3 2025)
- [ ] Enhanced AI models for better accuracy
- [ ] Mobile companion app (Android/iOS)
- [ ] Cloud-based scanning coordination
- [ ] Advanced machine learning analytics

### Version 1.2 (Q4 2025)
- [ ] Integration with major SIEM platforms
- [ ] Real-time threat intelligence feeds
- [ ] Advanced network visualization
- [ ] Multi-language support

### Version 2.0 (Q1 2026)
- [ ] Distributed scanning architecture
- [ ] Advanced Heuristic-driven exploit generation
- [ ] Blockchain-based result verification
- [ ] Quantum-resistant scanning protocols

## 🤝 Contributing

We welcome contributions from the community! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone repository
git clone https://github.com/yashab-cyber/nmap-ai.git
cd nmap-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
python -m pytest
```

## 💰 Support

If you find NMAP-AI useful, please consider supporting our development:

- 💰 [Donate via Cryptocurrency or PayPal](DONATE.md)
- ⭐ Star this repository on GitHub
- 📢 Share the project with others
- 🐛 Report bugs and suggest features
- 📝 Contribute to documentation

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- The Nmap Development Team for creating the amazing Nmap tool
- The open-source AI/ML community for inspiration and tools
- All contributors and supporters of the NMAP-AI project
- ZehraSec for providing development resources and support

## 📞 Contact

- **Email**: yashabalam707@gmail.com
- **GitHub**: [@yashab-cyber](https://github.com/yashab-cyber)
- **LinkedIn**: [Yashab Alam](https://www.linkedin.com/in/yashab-alam)
- **Company**: [ZehraSec](https://www.zehrasec.com)
- **WhatsApp**: [Business Channel](https://whatsapp.com/channel/0029Vaoa1GfKLaHlL0Kc8k1q)

---

**🚀 Made with ❤️ by Yashab Alam (Founder of ZehraSec) and the NMAP-AI team**

*Revolutionizing network security, one scan at a time.*
