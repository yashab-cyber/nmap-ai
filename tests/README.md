# Tests Directory

This directory contains all test files for the NMAP-AI project.

## Structure

- `unit/` - Unit tests for individual modules
- `integration/` - Integration tests for component interactions  
- `e2e/` - End-to-end tests for complete workflows
- `fixtures/` - Test data and mock files
- `conftest.py` - Pytest configuration and fixtures

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=nmap_ai tests/

# Run specific test file
python -m pytest tests/test_scanner.py

# Run with verbose output
python -m pytest -v tests/
```

## Test Categories

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **Performance Tests**: Test scanning performance and AI model efficiency
- **Security Tests**: Test security features and vulnerability detection
- **UI Tests**: Test GUI and web interface functionality

## Contributing

When adding new features, please include appropriate tests:

1. Unit tests for all new functions
2. Integration tests for new workflows
3. Update existing tests when modifying functionality
4. Ensure all tests pass before submitting PR

## Test Data

Test data should be stored in the `fixtures/` directory and should not contain any real sensitive information.
