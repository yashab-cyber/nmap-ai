# Integration Tests Directory

This directory contains integration tests for NMAP-AI that test the interaction between multiple components and systems.

## Test Categories

### API Integration Tests
- **test_api_endpoints.py**: REST API endpoint integration
- **test_auth_flow.py**: Authentication and authorization flow
- **test_scan_api.py**: Scanning API integration
- **test_report_api.py**: Report generation API integration

### Database Integration Tests
- **test_database_operations.py**: Database CRUD operations
- **test_scan_persistence.py**: Scan result storage and retrieval
- **test_config_storage.py**: Configuration persistence
- **test_data_migration.py**: Database migration testing

### External Service Integration
- **test_nmap_integration.py**: Nmap command execution and parsing
- **test_vulnerability_db.py**: External vulnerability database integration
- **test_plugin_system.py**: Plugin loading and execution
- **test_export_formats.py**: Data export functionality

### Cross-component Tests
- **test_cli_to_core.py**: CLI to core component integration
- **test_gui_to_core.py**: GUI to core component integration
- **test_web_to_core.py**: Web interface to core integration
- **test_ai_pipeline.py**: AI processing pipeline integration

## Test Environment

### Setup Requirements
- Docker containers for isolated testing
- Test databases with sample data
- Mock external services
- Temporary file system setup

### Test Data
- Sample network configurations
- Mock scan results
- Test vulnerability data
- Configuration fixtures

### Network Simulation
- Virtual network environments
- Controlled target systems
- Network topology simulation
- Service emulation

## Running Integration Tests

```bash
# Run all integration tests
pytest tests/integration/

# Run specific test category
pytest tests/integration/test_api_endpoints.py

# Run with coverage
pytest --cov=nmap_ai tests/integration/

# Run with verbose output
pytest -v tests/integration/
```

## Test Utilities

- Database setup/teardown helpers
- Network environment simulators
- Mock service providers
- Test data generators
