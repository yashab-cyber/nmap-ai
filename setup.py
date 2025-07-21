"""
Setup script for NMAP-AI package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read development requirements
dev_requirements = []
try:
    with open('requirements-dev.txt') as f:
        dev_requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
except FileNotFoundError:
    pass

setup(
    name="nmap-ai",
    version="1.0.0",
    author="Yashab Alam",
    author_email="yashabalam707@gmail.com",
    description="AI-Powered Network Scanning & Automation Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yashab-cyber/nmap-ai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "gui": [
            "PyQt6>=6.4.0",
            "pyqtgraph>=0.13.0",
        ],
        "web": [
            "fastapi>=0.95.0",
            "uvicorn>=0.20.0",
            "jinja2>=3.1.0",
        ],
        "ai": [
            "tensorflow>=2.8.0",
            "torch>=1.11.0",
            "transformers>=4.20.0",
            "scikit-learn>=1.0.0",
        ],
        "full": [
            "PyQt6>=6.4.0",
            "pyqtgraph>=0.13.0",
            "fastapi>=0.95.0",
            "uvicorn>=0.20.0",
            "jinja2>=3.1.0",
            "tensorflow>=2.8.0",
            "torch>=1.11.0",
            "transformers>=4.20.0",
            "scikit-learn>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "nmap-ai=nmap_ai.__main__:main",
            "nmap-ai-cli=nmap_ai.cli.main:cli_main",
            "nmap-ai-gui=nmap_ai.gui.main:gui_main",
            "nmap-ai-web=nmap_ai.web.main:web_main",
        ],
    },
    include_package_data=True,
    package_data={
        "nmap_ai": [
            "config/*.yaml",
            "data/models/*",
            "assets/*",
            "assets/icons/*",
            "assets/themes/*",
            "assets/templates/*",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/yashab-cyber/nmap-ai/issues",
        "Source": "https://github.com/yashab-cyber/nmap-ai",
        "Documentation": "https://github.com/yashab-cyber/nmap-ai/wiki",
        "Funding": "https://github.com/sponsors/yashab-cyber",
    },
    keywords=[
        "nmap", "network", "security", "scanning", "ai", "automation",
        "vulnerability", "penetration-testing", "cybersecurity", "infosec"
    ],
    zip_safe=False,
)
