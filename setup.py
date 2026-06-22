"""
Setup script for NMAP-AI package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')


def _parse_requirements(filename):
    """Parse a requirements file into a list of requirement strings.

    Strips blank lines, full-line comments, and inline ``# ...`` comments so
    the resulting strings are valid packaging requirements (pip tolerates
    inline comments, but ``setuptools`` metadata parsers do not).
    """
    reqs = []
    try:
        with open(filename) as f:
            for line in f:
                # Drop inline comments, then trim surrounding whitespace.
                requirement = line.split('#', 1)[0].strip()
                if requirement:
                    reqs.append(requirement)
    except FileNotFoundError:
        pass
    return reqs


# Read requirements
requirements = _parse_requirements('requirements.txt')

# Read development requirements
dev_requirements = _parse_requirements('requirements-dev.txt')

setup(
    name="nmap-ai",
    version="1.0.0",
    author="Yashab Alam",
    author_email="yashabalam707@gmail.com",
    description="Heuristic-driven Nmap wrapper with rule-based scan optimization and NSE script scaffolding",
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
        "full": [
            "PyQt6>=6.4.0",
            "pyqtgraph>=0.13.0",
            "fastapi>=0.95.0",
            "uvicorn>=0.20.0",
            "jinja2>=3.1.0",
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
