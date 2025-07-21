"""
Pydantic models for NMAP-AI web API.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class ScanType(str, Enum):
    """Supported scan types."""
    SYN = "syn"
    TCP = "tcp"
    UDP = "udp"
    ACK = "ack"
    CONNECT = "connect"


class TimingTemplate(str, Enum):
    """Nmap timing templates."""
    T0 = "T0"  # Paranoid
    T1 = "T1"  # Sneaky
    T2 = "T2"  # Polite
    T3 = "T3"  # Normal
    T4 = "T4"  # Aggressive
    T5 = "T5"  # Insane


class OutputFormat(str, Enum):
    """Supported output formats."""
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    HTML = "html"


class ScanOptions(BaseModel):
    """Scan configuration options."""
    ports: Optional[str] = Field(default="1-1000", description="Port range to scan")
    scan_type: Optional[ScanType] = Field(default=ScanType.SYN, description="Scan technique")
    timing: Optional[TimingTemplate] = Field(default=TimingTemplate.T3, description="Timing template")
    timeout: Optional[int] = Field(default=300, ge=1, le=3600, description="Scan timeout in seconds")
    threads: Optional[int] = Field(default=None, ge=1, le=100, description="Number of parallel threads")
    service_detection: Optional[bool] = Field(default=True, description="Enable service detection")
    version_detection: Optional[bool] = Field(default=True, description="Enable version detection")
    os_detection: Optional[bool] = Field(default=False, description="Enable OS detection")
    aggressive: Optional[bool] = Field(default=False, description="Enable aggressive scanning")
    stealth: Optional[bool] = Field(default=False, description="Enable stealth mode")
    scripts: Optional[List[str]] = Field(default=None, description="Nmap scripts to run")
    script_args: Optional[str] = Field(default=None, description="Script arguments")
    fragment: Optional[bool] = Field(default=False, description="Fragment packets")
    decoy: Optional[str] = Field(default=None, description="Decoy hosts")
    source_port: Optional[int] = Field(default=None, description="Source port number")
    max_rate: Optional[int] = Field(default=None, description="Maximum packet rate")
    min_rate: Optional[int] = Field(default=None, description="Minimum packet rate")


class ScanRequest(BaseModel):
    """Request model for starting a scan."""
    target: str = Field(..., description="Target IP, hostname, or CIDR range")
    ai_scan: Optional[bool] = Field(default=False, description="Use AI-powered scanning")
    vuln_scan: Optional[bool] = Field(default=False, description="Enable vulnerability detection")
    options: Optional[ScanOptions] = Field(default=None, description="Scan options")
    
    @validator('target')
    def validate_target(cls, v):
        """Validate target format."""
        if not v or not v.strip():
            raise ValueError("Target cannot be empty")
        return v.strip()


class ScanResponse(BaseModel):
    """Response model for scan start."""
    scan_id: str = Field(..., description="Unique scan identifier")
    status: str = Field(..., description="Initial scan status")
    message: str = Field(..., description="Status message")


class ScanStatus(BaseModel):
    """Scan status information."""
    scan_id: str = Field(..., description="Unique scan identifier")
    status: str = Field(..., description="Current scan status")
    progress: int = Field(..., ge=0, le=100, description="Progress percentage")
    started_at: datetime = Field(..., description="Scan start time")
    completed_at: Optional[datetime] = Field(default=None, description="Scan completion time")
    target: str = Field(..., description="Scan target")
    message: Optional[str] = Field(default="", description="Status message")


class PortInfo(BaseModel):
    """Information about a scanned port."""
    port: int = Field(..., description="Port number")
    protocol: str = Field(..., description="Protocol (tcp/udp)")
    state: str = Field(..., description="Port state")
    service: Optional[str] = Field(default=None, description="Service name")
    product: Optional[str] = Field(default=None, description="Product name")
    version: Optional[str] = Field(default=None, description="Version information")
    extra_info: Optional[str] = Field(default=None, description="Additional information")


class HostInfo(BaseModel):
    """Information about a scanned host."""
    ip: str = Field(..., description="IP address")
    hostname: Optional[str] = Field(default=None, description="Hostname")
    status: str = Field(..., description="Host status")
    open_ports: List[PortInfo] = Field(default=[], description="Open ports")
    os_info: Optional[Dict[str, Any]] = Field(default=None, description="OS detection results")


class ScanResults(BaseModel):
    """Complete scan results."""
    scan_id: str = Field(..., description="Scan identifier")
    target: str = Field(..., description="Scan target")
    started_at: datetime = Field(..., description="Scan start time")
    completed_at: datetime = Field(..., description="Scan completion time")
    elapsed_time: float = Field(..., description="Scan duration in seconds")
    hosts_scanned: int = Field(..., description="Total hosts scanned")
    hosts_up: int = Field(..., description="Number of hosts up")
    hosts: List[HostInfo] = Field(default=[], description="Host information")
    raw_results: Optional[Dict[str, Any]] = Field(default=None, description="Raw nmap results")


class VulnerabilityInfo(BaseModel):
    """Vulnerability information."""
    cve_id: str = Field(..., description="CVE identifier")
    severity: str = Field(..., description="Severity level")
    score: float = Field(..., ge=0.0, le=10.0, description="CVSS score")
    description: str = Field(..., description="Vulnerability description")
    affected_service: str = Field(..., description="Affected service")
    port: int = Field(..., description="Affected port")
    exploit_available: bool = Field(..., description="Exploit availability")
    patch_available: bool = Field(..., description="Patch availability")
    references: List[str] = Field(default=[], description="Reference links")


class VulnerabilityReport(BaseModel):
    """Vulnerability assessment report."""
    target_ip: str = Field(..., description="Target IP address")
    scan_time: datetime = Field(..., description="Scan timestamp")
    total_vulnerabilities: int = Field(..., description="Total vulnerabilities found")
    severity_counts: Dict[str, int] = Field(..., description="Count by severity")
    risk_score: float = Field(..., ge=0.0, le=10.0, description="Overall risk score")
    vulnerabilities: List[VulnerabilityInfo] = Field(default=[], description="Vulnerability details")
    recommendations: List[str] = Field(default=[], description="Security recommendations")


class ConfigScanningSettings(BaseModel):
    """Scanning configuration settings."""
    default_timeout: Optional[int] = Field(default=None, ge=1, le=3600)
    max_threads: Optional[int] = Field(default=None, ge=1, le=100)
    default_ports: Optional[str] = Field(default=None)


class ConfigAISettings(BaseModel):
    """AI configuration settings."""
    enable_smart_scanning: Optional[bool] = Field(default=None)
    enable_vulnerability_detection: Optional[bool] = Field(default=None)
    confidence_threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class ConfigOutputSettings(BaseModel):
    """Output configuration settings."""
    default_format: Optional[OutputFormat] = Field(default=None)
    results_directory: Optional[str] = Field(default=None)


class ConfigUpdate(BaseModel):
    """Configuration update request."""
    scanning: Optional[ConfigScanningSettings] = Field(default=None)
    ai: Optional[ConfigAISettings] = Field(default=None)
    output: Optional[ConfigOutputSettings] = Field(default=None)


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")


class HealthStatus(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(..., description="Check timestamp")
    version: str = Field(..., description="Application version")
    services: Dict[str, str] = Field(..., description="Service status")


class ReportRequest(BaseModel):
    """Report generation request."""
    scan_id: str = Field(..., description="Scan ID to generate report for")
    format: OutputFormat = Field(default=OutputFormat.HTML, description="Report format")
    include_raw_results: Optional[bool] = Field(default=False, description="Include raw scan data")
    include_vulnerability_analysis: Optional[bool] = Field(default=True, description="Include vulnerability analysis")


class ReportResponse(BaseModel):
    """Report generation response."""
    report_id: str = Field(..., description="Generated report ID")
    format: OutputFormat = Field(..., description="Report format")
    download_url: str = Field(..., description="Report download URL")
    generated_at: datetime = Field(..., description="Report generation time")
    expires_at: datetime = Field(..., description="Report expiration time")


class Plugin(BaseModel):
    """Plugin information."""
    name: str = Field(..., description="Plugin name")
    version: str = Field(..., description="Plugin version")
    description: str = Field(..., description="Plugin description")
    author: str = Field(..., description="Plugin author")
    enabled: bool = Field(..., description="Plugin enabled status")
    category: str = Field(..., description="Plugin category")


class PluginList(BaseModel):
    """List of available plugins."""
    plugins: List[Plugin] = Field(default=[], description="Available plugins")


class AIModelInfo(BaseModel):
    """AI model information."""
    name: str = Field(..., description="Model name")
    type: str = Field(..., description="Model type")
    version: str = Field(..., description="Model version")
    status: str = Field(..., description="Model status")
    accuracy: Optional[float] = Field(default=None, description="Model accuracy")
    last_updated: Optional[datetime] = Field(default=None, description="Last update time")


class AIModelsResponse(BaseModel):
    """AI models status response."""
    models: List[AIModelInfo] = Field(default=[], description="AI models")
    total_models: int = Field(..., description="Total number of models")
    loaded_models: int = Field(..., description="Number of loaded models")


class WebSocketMessage(BaseModel):
    """WebSocket message format."""
    type: str = Field(..., description="Message type")
    data: Dict[str, Any] = Field(default={}, description="Message data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")


class ScanProgress(BaseModel):
    """Real-time scan progress update."""
    scan_id: str = Field(..., description="Scan identifier")
    progress: int = Field(..., ge=0, le=100, description="Progress percentage")
    status: str = Field(..., description="Current status")
    current_host: Optional[str] = Field(default=None, description="Currently scanning host")
    hosts_completed: int = Field(default=0, description="Number of hosts completed")
    total_hosts: int = Field(default=0, description="Total number of hosts")
    message: Optional[str] = Field(default="", description="Progress message")


# Response models for different HTTP status codes
class ValidationError(BaseModel):
    """Validation error response."""
    detail: List[Dict[str, Any]] = Field(..., description="Validation error details")


class NotFoundError(BaseModel):
    """Not found error response."""
    detail: str = Field(..., description="Not found message")


class InternalServerError(BaseModel):
    """Internal server error response."""
    detail: str = Field(..., description="Internal error message")
