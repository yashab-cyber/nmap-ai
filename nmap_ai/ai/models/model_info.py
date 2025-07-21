"""
AI Model Configuration and Metadata
This file serves as a placeholder and documentation for AI model files.
"""

# AI Model Information
# ===================
# This directory should contain trained AI/ML models for NMAP-AI

# Supported Model Types:
# 1. Vulnerability Detection Model
#    - File: vulnerability_detector.pkl
#    - Type: Scikit-learn RandomForest or similar
#    - Purpose: Classify vulnerabilities from scan results
#    - Input: Feature vectors from scan data
#    - Output: Vulnerability classifications and confidence scores

# 2. Service Classification Model
#    - File: service_classifier.h5
#    - Type: TensorFlow/Keras neural network
#    - Purpose: Intelligent service identification
#    - Input: Port scan data and service banners
#    - Output: Service type predictions

# 3. Anomaly Detection Model
#    - File: anomaly_detector.joblib
#    - Type: Isolation Forest or One-Class SVM
#    - Purpose: Detect unusual network behavior
#    - Input: Network traffic patterns
#    - Output: Anomaly scores

# 4. Script Recommendation Model
#    - File: script_recommender.pkl
#    - Type: Collaborative filtering or content-based model
#    - Purpose: Recommend appropriate nmap scripts
#    - Input: Target characteristics and scan context
#    - Output: Ranked list of recommended scripts

# Model Metadata Structure:
MODEL_METADATA = {
    "vulnerability_detector": {
        "file": "vulnerability_detector.pkl",
        "version": "1.0.0",
        "created": "2025-07-21",
        "algorithm": "RandomForestClassifier",
        "features": [
            "open_ports_count",
            "service_versions",
            "os_detection_confidence",
            "script_results",
            "port_states_distribution"
        ],
        "accuracy": 0.92,
        "precision": 0.89,
        "recall": 0.94,
        "training_data_size": 10000,
        "classes": ["critical", "high", "medium", "low", "info"]
    },
    
    "service_classifier": {
        "file": "service_classifier.h5",
        "version": "1.2.1",
        "created": "2025-07-21",
        "algorithm": "Deep Neural Network",
        "architecture": "3-layer MLP with dropout",
        "input_shape": (256,),
        "output_classes": 50,
        "accuracy": 0.95,
        "training_epochs": 100,
        "batch_size": 32
    },
    
    "anomaly_detector": {
        "file": "anomaly_detector.joblib",
        "version": "1.0.0",
        "created": "2025-07-21",
        "algorithm": "IsolationForest",
        "contamination": 0.1,
        "n_estimators": 100,
        "features": [
            "connection_count",
            "packet_size_distribution",
            "timing_patterns",
            "port_access_patterns"
        ]
    }
}

# Model Loading Instructions:
# 1. Place model files in this directory
# 2. Update the MODEL_METADATA dictionary
# 3. Models will be automatically loaded by the AI engine
# 4. Ensure model dependencies are installed (sklearn, tensorflow, etc.)

# Model Training Data Requirements:
# - Labeled datasets for supervised learning
# - Network scan results with ground truth
# - Vulnerability assessment reports
# - Service identification data
# - Historical network behavior data

# Performance Benchmarks:
# Models should meet minimum performance criteria:
# - Accuracy: >= 85%
# - Precision: >= 80%
# - Recall: >= 85%
# - Inference time: <= 100ms per prediction
# - Memory usage: <= 500MB per model
