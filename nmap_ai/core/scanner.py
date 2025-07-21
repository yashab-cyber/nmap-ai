"""
Main scanning engine for NMAP-AI
"""

import asyncio
import nmap
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path
import json

from ..config import get_config
from ..utils.logger import get_logger
from ..utils.validators import validate_target, validate_ports
from .parser import ResultParser
from .ai_engine import AIEngine


class NmapAIScanner:
    """
    Advanced Nmap scanner with AI capabilities.
    """
    
    def __init__(self, ai_enabled: bool = True):
        """Initialize the scanner."""
        self.config = get_config()
        self.logger = get_logger(__name__)
        self.nm = nmap.PortScanner()
        self.ai_enabled = ai_enabled
        self.ai_engine = AIEngine() if ai_enabled else None
        self.parser = ResultParser()
        self.scan_history: List[Dict[str, Any]] = []
    
    def scan(
        self,
        targets: Union[str, List[str]],
        ports: Optional[str] = None,
        arguments: Optional[str] = None,
        ai_optimize: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform a network scan.
        
        Args:
            targets: Target hosts or networks to scan
            ports: Port specification (e.g., '1-1000', '80,443,22')
            arguments: Additional nmap arguments
            ai_optimize: Whether to use AI optimization
            **kwargs: Additional options
        
        Returns:
            Dictionary containing scan results
        """
        start_time = datetime.now()
        
        # Validate inputs
        if isinstance(targets, str):
            targets = [targets]
        
        for target in targets:
            if not validate_target(target):
                raise ValueError(f"Invalid target: {target}")
        
        if ports and not validate_ports(ports):
            raise ValueError(f"Invalid port specification: {ports}")
        
        # Set default values
        ports = ports or self.config.scanning.default_ports
        arguments = arguments or ""
        
        # AI optimization
        if ai_optimize and self.ai_enabled:
            optimized_args = self.ai_engine.optimize_scan_arguments(
                targets, ports, arguments
            )
            arguments = optimized_args
            self.logger.info(f"AI-optimized arguments: {arguments}")
        
        # Perform the scan
        results = {}
        for target in targets:
            self.logger.info(f"Scanning target: {target}")
            try:
                scan_result = self._perform_single_scan(target, ports, arguments)
                results[target] = scan_result
            except Exception as e:
                self.logger.error(f"Error scanning {target}: {e}")
                results[target] = {"error": str(e)}
        
        # Process results with AI
        if self.ai_enabled:
            results = self.ai_engine.enhance_results(results)
        
        # Create scan summary
        end_time = datetime.now()
        scan_summary = {
            "scan_id": self._generate_scan_id(),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration": (end_time - start_time).total_seconds(),
            "targets": targets,
            "ports": ports,
            "arguments": arguments,
            "ai_enabled": self.ai_enabled,
            "results": results
        }
        
        # Store in history
        self.scan_history.append(scan_summary)
        
        return scan_summary
    
    def _perform_single_scan(
        self, 
        target: str, 
        ports: str, 
        arguments: str
    ) -> Dict[str, Any]:
        """Perform a single target scan."""
        try:
            # Build nmap command
            nmap_args = f"-p {ports} {arguments}"
            
            # Execute scan
            self.nm.scan(target, arguments=nmap_args)
            
            # Parse results
            raw_result = self.nm[target] if target in self.nm.all_hosts() else {}
            parsed_result = self.parser.parse_scan_result(raw_result)
            
            return {
                "status": "success",
                "raw": raw_result,
                "parsed": parsed_result,
                "command": self.nm.command_line()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "command": getattr(self.nm, 'command_line', lambda: "N/A")()
            }
    
    def async_scan(
        self,
        targets: Union[str, List[str]],
        ports: Optional[str] = None,
        arguments: Optional[str] = None,
        max_concurrent: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform asynchronous scanning of multiple targets.
        """
        return asyncio.run(
            self._async_scan_impl(targets, ports, arguments, max_concurrent, **kwargs)
        )
    
    async def _async_scan_impl(
        self,
        targets: Union[str, List[str]],
        ports: Optional[str],
        arguments: Optional[str],
        max_concurrent: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Implementation of async scanning."""
        if isinstance(targets, str):
            targets = [targets]
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scan_target(target: str) -> tuple[str, Dict[str, Any]]:
            async with semaphore:
                # Run sync scan in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, 
                    lambda: self.scan([target], ports, arguments, **kwargs)
                )
                return target, result["results"][target]
        
        # Execute all scans concurrently
        tasks = [scan_target(target) for target in targets]
        scan_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        results = {}
        for i, result in enumerate(scan_results):
            if isinstance(result, Exception):
                results[targets[i]] = {"error": str(result)}
            else:
                target, target_result = result
                results[target] = target_result
        
        return {
            "scan_id": self._generate_scan_id(),
            "scan_type": "async",
            "targets": targets,
            "results": results
        }
    
    def generate_ai_script(
        self,
        target_info: Dict[str, Any],
        script_type: str = "general",
        requirements: Optional[List[str]] = None
    ) -> str:
        """
        Generate AI-powered Nmap script.
        
        Args:
            target_info: Information about the target
            script_type: Type of script to generate
            requirements: Specific requirements for the script
        
        Returns:
            Generated Nmap script content
        """
        if not self.ai_enabled:
            raise RuntimeError("AI features are disabled")
        
        return self.ai_engine.generate_script(target_info, script_type, requirements)
    
    def smart_scan(
        self,
        target: str,
        scan_profile: str = "adaptive",
        learn_from_previous: bool = True
    ) -> Dict[str, Any]:
        """
        Perform an AI-powered smart scan.
        
        Args:
            target: Target to scan
            scan_profile: Scanning profile (adaptive, fast, thorough, stealth)
            learn_from_previous: Whether to learn from previous scans
        
        Returns:
            Smart scan results with AI insights
        """
        if not self.ai_enabled:
            return self.scan([target])
        
        # AI-driven scan planning
        scan_plan = self.ai_engine.create_scan_plan(
            target, scan_profile, self.scan_history if learn_from_previous else []
        )
        
        # Execute the planned scan
        result = self.scan(
            targets=[target],
            ports=scan_plan.get("ports"),
            arguments=scan_plan.get("arguments"),
            ai_optimize=True
        )
        
        # Add AI insights
        result["ai_insights"] = scan_plan.get("insights", {})
        result["scan_profile"] = scan_profile
        
        return result
    
    def batch_scan(
        self,
        targets_file: str,
        output_format: str = "json",
        output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform batch scanning from a file of targets.
        
        Args:
            targets_file: Path to file containing targets (one per line)
            output_format: Output format (json, xml, csv)
            output_file: Output file path
        
        Returns:
            Batch scan results
        """
        # Read targets from file
        targets = []
        try:
            with open(targets_file, 'r') as f:
                targets = [line.strip() for line in f if line.strip()]
        except Exception as e:
            raise ValueError(f"Could not read targets file {targets_file}: {e}")
        
        if not targets:
            raise ValueError("No targets found in file")
        
        # Perform async scan for efficiency
        results = self.async_scan(targets, max_concurrent=self.config.scanning.max_parallel_hosts)
        
        # Save results if output file specified
        if output_file:
            self._save_results(results, output_file, output_format)
        
        return results
    
    def get_scan_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get scan history."""
        if limit:
            return self.scan_history[-limit:]
        return self.scan_history.copy()
    
    def clear_scan_history(self) -> None:
        """Clear scan history."""
        self.scan_history.clear()
    
    def _generate_scan_id(self) -> str:
        """Generate unique scan ID."""
        return f"scan_{int(datetime.now().timestamp())}_{len(self.scan_history)}"
    
    def _save_results(
        self, 
        results: Dict[str, Any], 
        output_file: str, 
        format: str
    ) -> None:
        """Save scan results to file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == "json":
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
        elif format.lower() == "xml":
            # XML export implementation
            self._export_xml(results, output_path)
        elif format.lower() == "csv":
            # CSV export implementation
            self._export_csv(results, output_path)
        else:
            raise ValueError(f"Unsupported output format: {format}")
        
        self.logger.info(f"Results saved to {output_path}")
    
    def _export_xml(self, results: Dict[str, Any], output_path: Path) -> None:
        """Export results to XML format."""
        # Implementation for XML export
        pass
    
    def _export_csv(self, results: Dict[str, Any], output_path: Path) -> None:
        """Export results to CSV format."""
        # Implementation for CSV export
        pass
