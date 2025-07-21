# Documentation

This directory contains comprehensive documentation for the NMAP-AI project.

## Documentation Structure

- `api/` - API documentation and references
- `user-guide/` - User guides and tutorials
- `developer-guide/` - Developer documentation
- `deployment/` - Deployment and installation guides
- `changelog/` - Version history and release notes
- `assets/` - Images, diagrams, and other documentation assets

## Available Documentation

### User Documentation
- **Getting Started Guide** - Quick start tutorial
- **CLI Reference** - Complete command-line interface documentation
- **GUI User Manual** - Graphical interface guide
- **Web Interface Guide** - Web dashboard documentation
- **Configuration Guide** - Configuration options and settings

### Developer Documentation
- **Architecture Overview** - System design and architecture
- **API Documentation** - REST API endpoints and usage
- **Plugin Development** - Creating custom plugins and scripts
- **Contributing Guide** - How to contribute to the project
- **Code Style Guide** - Coding standards and conventions

### Technical Documentation
- **AI Models** - Machine learning models and algorithms used
- **Security Features** - Security implementations and best practices
- **Performance Tuning** - Optimization tips and benchmarks
- **Troubleshooting** - Common issues and solutions

## Building Documentation

If you're using a documentation generator like Sphinx:

```bash
# Install documentation dependencies
pip install sphinx sphinx-rtd-theme

# Build HTML documentation
cd docs/
make html

# Build PDF documentation
make latexpdf
```

## Contributing to Documentation

1. Use clear, concise language
2. Include code examples where appropriate
3. Keep documentation up-to-date with code changes
4. Use proper Markdown formatting
5. Include screenshots for UI documentation

## Documentation Standards

- Use Markdown for most documentation files
- Include table of contents for longer documents
- Use proper heading hierarchy (H1, H2, H3, etc.)
- Include cross-references between related documents
- Keep line length under 80 characters where possible
