# NMAP-AI Project Structure

```
nmap-ai/
├── README.md                   # Project documentation
├── LICENSE                     # MIT License
├── SECURITY.md                 # Security policy and vulnerability reporting
├── PRIVACY_POLICY.md          # Privacy policy and data handling
├── CONTRIBUTORS.md            # Contributors recognition and guidelines
├── DEVELOPER_MESSAGE.md       # Message from developers and project vision
├── DONATE.md                   # Donation information
├── Dockerfile                  # Docker container configuration
├── setup.py                    # Python package setup
├── pyproject.toml             # Project configuration
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies
├── .gitignore                 # Git ignore rules
├── .github/                   # GitHub workflows
│   └── workflows/
│       ├── ci.yml            # Continuous Integration
│       └── release.yml       # Release automation
├── docs/                      # Documentation
│   ├── README.md             # Documentation overview
│   ├── index.md              # Main documentation
│   ├── installation.md       # Installation guide
│   ├── usage.md              # Usage examples
│   └── api.md                # API reference
├── config/                    # Configuration files
│   ├── README.md             # Configuration documentation
│   └── default.yaml          # Default configuration
├── assets/                    # Static assets
│   └── README.md             # Assets documentation
├── data/                      # Data files
│   └── README.md             # Data directory info
├── scripts/                   # Utility scripts
│   ├── README.md             # Scripts documentation
│   └── install.sh            # Installation script
├── nmap_ai/                   # Main package
│   ├── __init__.py
│   ├── __main__.py           # Entry point
│   ├── config.py             # Configuration management
│   ├── core/                 # Core functionality
│   │   ├── __init__.py
│   │   ├── scanner.py        # Main scanning engine
│   │   ├── ai_engine.py      # AI processing
│   │   └── parser.py         # Result parsing
│   ├── ai/                   # AI/ML components
│   │   ├── __init__.py
│   │   ├── models/           # AI models
│   │   ├── script_generator.py
│   │   ├── vulnerability_detector.py
│   │   └── smart_scanner.py
│   ├── gui/                  # GUI application
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── widgets/          # GUI widgets
│   │   └── resources/        # GUI resources
│   ├── cli/                  # Command-line interface
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── commands/         # CLI commands
│   │       ├── __init__.py
│   │       ├── scan.py       # Scan command
│   │       ├── config.py     # Config command
│   │       ├── report.py     # Report command
│   │       └── setup.py      # Setup command
│   ├── web/                  # Web interface
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/              # REST API
│   │   │   ├── __init__.py
│   │   │   ├── endpoints.py  # API endpoints
│   │   │   └── models.py     # Pydantic models
│   │   ├── templates/        # Jinja2 templates
│   │   └── static/           # Static files
│   ├── utils/                # Utilities
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   ├── validators.py
│   │   └── helpers.py
│   └── plugins/              # Plugin system
│       ├── __init__.py
│       └── base.py           # Base plugin classes
├── tests/                    # Test suite
│   ├── README.md             # Testing documentation
│   ├── conftest.py           # Pytest configuration
│   ├── unit/                 # Unit tests
│   │   └── test_vulnerability_detector.py
│   ├── integration/          # Integration tests
│   └── fixtures/             # Test fixtures
├── examples/                 # Example usage
│   ├── README.md             # Examples documentation
│   ├── basic_scan.py         # Basic scanning example
│   ├── ai_script_gen.py      # AI script generation example
│   └── batch_scanning.py     # Batch scanning example
```
