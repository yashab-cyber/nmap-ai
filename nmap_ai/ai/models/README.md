# AI Models Directory

This directory contains AI/ML model files for NMAP-AI's intelligent scanning capabilities.

## Contents

- **Trained Models**: Pre-trained models for vulnerability detection and pattern recognition
- **Model Configurations**: Configuration files for different AI models
- **Model Artifacts**: Serialized model files, weights, and metadata

## Supported Model Types

- **Vulnerability Detection Models**: Models trained to identify security vulnerabilities
- **Port Service Classification**: Models for intelligent service identification
- **Anomaly Detection**: Models for detecting unusual network patterns
- **Script Generation Models**: AI models for automated nmap script generation

## Model Format Support

- TensorFlow SavedModel format
- PyTorch model files (.pth)
- Scikit-learn pickle files (.pkl)
- ONNX model format (.onnx)

## Usage

Models are automatically loaded by the AI engine based on configuration settings. Place model files in this directory and update the configuration to use them.

## Note

This directory may be empty initially. Models will be downloaded or trained as needed by the application.
