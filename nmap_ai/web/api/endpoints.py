"""
API endpoints for NMAP-AI web interface.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from ...core.scanner import NmapAIScanner
from ...ai.smart_scanner import SmartScanner
from ...ai.vulnerability_detector import VulnerabilityDetector
from ...config import Config
from ...utils.logger import get_logger
from .models import (
    ScanRequest, ScanResponse, ScanStatus, 
    VulnerabilityReport, ConfigUpdate,
    ErrorResponse
)

router = APIRouter()
logger = get_logger("web.api")

# In-memory storage for scan results (in production, use a database)
active_scans: Dict[str, Dict] = {}
scan_results: Dict[str, Dict] = {}


def get_config() -> Config:
    """Get current configuration."""
    return Config()


@router.post("/scan/start", response_model=ScanResponse)
async def start_scan(
    scan_request: ScanRequest,
    background_tasks: BackgroundTasks,
    config: Config = Depends(get_config)
):
    """
    Start a new network scan.
    
    Args:
        scan_request: Scan configuration and parameters
        background_tasks: FastAPI background tasks
        config: Application configuration
        
    Returns:
        ScanResponse: Scan ID and initial status
    """
    try:
        # Generate unique scan ID
        scan_id = str(uuid.uuid4())
        
        # Initialize scan status
        active_scans[scan_id] = {
            'status': 'starting',
            'started_at': datetime.now(),
            'progress': 0,
            'target': scan_request.target,
            'options': scan_request.options.dict() if scan_request.options else {}
        }
        
        # Start scan in background
        background_tasks.add_task(
            execute_scan,
            scan_id,
            scan_request,
            config
        )
        
        logger.info(f"Started scan {scan_id} for target {scan_request.target}")
        
        return ScanResponse(
            scan_id=scan_id,
            status="starting",
            message="Scan started successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to start scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scan/{scan_id}/status", response_model=ScanStatus)
async def get_scan_status(scan_id: str):
    """
    Get status of an active or completed scan.
    
    Args:
        scan_id: Unique scan identifier
        
    Returns:
        ScanStatus: Current scan status and progress
    """
    if scan_id not in active_scans and scan_id not in scan_results:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    if scan_id in active_scans:
        scan_info = active_scans[scan_id]
        return ScanStatus(
            scan_id=scan_id,
            status=scan_info['status'],
            progress=scan_info['progress'],
            started_at=scan_info['started_at'],
            target=scan_info['target'],
            message=scan_info.get('message', '')
        )
    else:
        scan_info = scan_results[scan_id]
        return ScanStatus(
            scan_id=scan_id,
            status='completed',
            progress=100,
            started_at=scan_info['started_at'],
            completed_at=scan_info['completed_at'],
            target=scan_info['target'],
            message='Scan completed successfully'
        )


@router.get("/scan/{scan_id}/results")
async def get_scan_results(scan_id: str):
    """
    Get results of a completed scan.
    
    Args:
        scan_id: Unique scan identifier
        
    Returns:
        Dict: Scan results
    """
    if scan_id not in scan_results:
        if scan_id in active_scans:
            raise HTTPException(status_code=400, detail="Scan still in progress")
        else:
            raise HTTPException(status_code=404, detail="Scan not found")
    
    return scan_results[scan_id]['results']


@router.delete("/scan/{scan_id}")
async def cancel_scan(scan_id: str):
    """
    Cancel an active scan.
    
    Args:
        scan_id: Unique scan identifier
        
    Returns:
        Dict: Cancellation status
    """
    if scan_id not in active_scans:
        raise HTTPException(status_code=404, detail="Active scan not found")
    
    # Mark scan as cancelled
    active_scans[scan_id]['status'] = 'cancelled'
    active_scans[scan_id]['message'] = 'Scan cancelled by user'
    
    logger.info(f"Cancelled scan {scan_id}")
    
    return {"message": "Scan cancelled successfully"}


@router.get("/scans")
async def list_scans():
    """
    List all scans (active and completed).
    
    Returns:
        Dict: List of all scans with their status
    """
    scans = []
    
    # Add active scans
    for scan_id, scan_info in active_scans.items():
        scans.append({
            'scan_id': scan_id,
            'status': scan_info['status'],
            'target': scan_info['target'],
            'started_at': scan_info['started_at'],
            'progress': scan_info['progress']
        })
    
    # Add completed scans
    for scan_id, scan_info in scan_results.items():
        scans.append({
            'scan_id': scan_id,
            'status': 'completed',
            'target': scan_info['target'],
            'started_at': scan_info['started_at'],
            'completed_at': scan_info['completed_at'],
            'progress': 100
        })
    
    return {"scans": scans}


@router.post("/vulnerability/analyze")
async def analyze_vulnerabilities(
    scan_results_data: Dict[str, Any],
    config: Config = Depends(get_config)
):
    """
    Analyze scan results for vulnerabilities.
    
    Args:
        scan_results_data: Scan results to analyze
        config: Application configuration
        
    Returns:
        Dict: Vulnerability analysis report
    """
    try:
        detector = VulnerabilityDetector(config)
        vuln_report = detector.analyze_scan_results(scan_results_data)
        
        return {
            'target_ip': vuln_report.target_ip,
            'scan_time': vuln_report.scan_time.isoformat(),
            'total_vulnerabilities': vuln_report.total_vulnerabilities,
            'severity_counts': {
                'critical': vuln_report.critical_count,
                'high': vuln_report.high_count,
                'medium': vuln_report.medium_count,
                'low': vuln_report.low_count
            },
            'risk_score': vuln_report.risk_score,
            'vulnerabilities': [
                {
                    'cve_id': v.cve_id,
                    'severity': v.severity,
                    'score': v.score,
                    'description': v.description,
                    'affected_service': v.affected_service,
                    'port': v.port,
                    'exploit_available': v.exploit_available,
                    'patch_available': v.patch_available
                }
                for v in vuln_report.vulnerabilities
            ],
            'recommendations': vuln_report.recommendations
        }
        
    except Exception as e:
        logger.error(f"Vulnerability analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_configuration(config: Config = Depends(get_config)):
    """
    Get current application configuration.
    
    Returns:
        Dict: Current configuration
    """
    return {
        'scanning': {
            'default_timeout': config.scanning_timeout,
            'max_threads': config.max_threads,
            'default_ports': config.default_ports
        },
        'ai': {
            'enable_smart_scanning': config.enable_smart_scanning,
            'enable_vulnerability_detection': config.enable_vulnerability_detection,
            'confidence_threshold': config.ai_confidence_threshold
        },
        'output': {
            'default_format': config.default_output_format,
            'results_directory': config.results_dir
        }
    }


@router.put("/config")
async def update_configuration(
    config_update: ConfigUpdate,
    config: Config = Depends(get_config)
):
    """
    Update application configuration.
    
    Args:
        config_update: Configuration updates
        config: Current configuration
        
    Returns:
        Dict: Updated configuration
    """
    try:
        # Update configuration (in production, save to file)
        if config_update.scanning:
            if config_update.scanning.default_timeout:
                config.scanning_timeout = config_update.scanning.default_timeout
            if config_update.scanning.max_threads:
                config.max_threads = config_update.scanning.max_threads
        
        if config_update.ai:
            if config_update.ai.enable_smart_scanning is not None:
                config.enable_smart_scanning = config_update.ai.enable_smart_scanning
            if config_update.ai.confidence_threshold:
                config.ai_confidence_threshold = config_update.ai.confidence_threshold
        
        logger.info("Configuration updated successfully")
        
        return {"message": "Configuration updated successfully"}
        
    except Exception as e:
        logger.error(f"Failed to update configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Dict: Service health status
    """
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'services': {
            'scanner': 'available',
            'ai_engine': 'available',
            'vulnerability_detector': 'available'
        }
    }


async def execute_scan(scan_id: str, scan_request: ScanRequest, config: Config):
    """
    Execute scan in background task.
    
    Args:
        scan_id: Unique scan identifier
        scan_request: Scan parameters
        config: Application configuration
    """
    try:
        # Update status
        active_scans[scan_id]['status'] = 'running'
        active_scans[scan_id]['progress'] = 10
        
        # Initialize scanner
        if scan_request.ai_scan:
            scanner = SmartScanner(config)
        else:
            scanner = NmapAIScanner(config)
        
        active_scans[scan_id]['progress'] = 20
        
        # Prepare scan options
        scan_options = {}
        if scan_request.options:
            scan_options.update(scan_request.options.dict())
        
        active_scans[scan_id]['progress'] = 30
        
        # Execute scan
        results = scanner.scan(scan_request.target, **scan_options)
        
        active_scans[scan_id]['progress'] = 80
        
        # Store results
        scan_results[scan_id] = {
            'scan_id': scan_id,
            'target': scan_request.target,
            'started_at': active_scans[scan_id]['started_at'],
            'completed_at': datetime.now(),
            'results': results
        }
        
        # Remove from active scans
        del active_scans[scan_id]
        
        logger.info(f"Completed scan {scan_id}")
        
    except Exception as e:
        logger.error(f"Scan {scan_id} failed: {e}")
        
        # Update status to failed
        if scan_id in active_scans:
            active_scans[scan_id]['status'] = 'failed'
            active_scans[scan_id]['message'] = str(e)
            active_scans[scan_id]['progress'] = 0
