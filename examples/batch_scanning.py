"""
Batch Scanning Example for NMAP-AI.

This example demonstrates how to perform batch scanning of multiple targets
using NMAP-AI with various configurations and automated report generation.
"""

import argparse
import sys
import asyncio
import json
import csv
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from nmap_ai.core.scanner import NmapAIScanner
from nmap_ai.ai.smart_scanner import SmartScanner
from nmap_ai.ai.vulnerability_detector import VulnerabilityDetector
from nmap_ai.config import Config
from nmap_ai.utils.logger import get_logger


class BatchScanner:
    """Batch scanning manager for NMAP-AI."""
    
    def __init__(self, config: Config):
        """Initialize batch scanner."""
        self.config = config
        self.logger = get_logger("batch_scanner")
        self.results = []
        
    def load_targets_from_file(self, filepath: str) -> List[str]:
        """Load scan targets from file."""
        targets = []
        file_path = Path(filepath)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Targets file not found: {filepath}")
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        targets.append(line)
            
            self.logger.info(f"Loaded {len(targets)} targets from {filepath}")
            return targets
            
        except Exception as e:
            self.logger.error(f"Failed to load targets from {filepath}: {e}")
            raise
    
    def scan_single_target(self, target: str, scan_config: Dict[str, Any]) -> Dict[str, Any]:
        """Scan a single target."""
        try:
            self.logger.info(f"Starting scan of {target}")
            
            # Initialize scanner
            if scan_config.get('ai_scan', False):
                scanner = SmartScanner(self.config)
            else:
                scanner = NmapAIScanner(self.config)
            
            # Perform scan
            scan_result = scanner.scan(target, **scan_config)
            
            # Add vulnerability analysis if requested
            if scan_config.get('vuln_scan', False):
                self.logger.info(f"Analyzing vulnerabilities for {target}")
                detector = VulnerabilityDetector(self.config)
                vuln_report = detector.analyze_scan_results(scan_result)
                
                scan_result['vulnerability_analysis'] = {
                    'total_vulnerabilities': vuln_report.total_vulnerabilities,
                    'risk_score': vuln_report.risk_score,
                    'severity_counts': {
                        'critical': vuln_report.critical_count,
                        'high': vuln_report.high_count,
                        'medium': vuln_report.medium_count,
                        'low': vuln_report.low_count
                    },
                    'recommendations': vuln_report.recommendations
                }
            
            # Add metadata
            scan_result['batch_scan_metadata'] = {
                'target': target,
                'scan_time': datetime.now().isoformat(),
                'scan_config': scan_config,
                'status': 'completed'
            }
            
            self.logger.info(f"Successfully scanned {target}")
            return scan_result
            
        except Exception as e:
            self.logger.error(f"Failed to scan {target}: {e}")
            return {
                'batch_scan_metadata': {
                    'target': target,
                    'scan_time': datetime.now().isoformat(),
                    'scan_config': scan_config,
                    'status': 'failed',
                    'error': str(e)
                }
            }
    
    def scan_targets_parallel(self, targets: List[str], scan_config: Dict[str, Any], 
                             max_workers: int = 5) -> List[Dict[str, Any]]:
        """Scan multiple targets in parallel."""
        self.logger.info(f"Starting parallel scan of {len(targets)} targets with {max_workers} workers")
        
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all scan tasks
            future_to_target = {
                executor.submit(self.scan_single_target, target, scan_config): target 
                for target in targets
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_target):
                target = future_to_target[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Log progress
                    completed = len(results)
                    total = len(targets)
                    progress = (completed / total) * 100
                    self.logger.info(f"Progress: {completed}/{total} ({progress:.1f}%) - Completed {target}")
                    
                except Exception as e:
                    self.logger.error(f"Exception for target {target}: {e}")
                    results.append({
                        'batch_scan_metadata': {
                            'target': target,
                            'scan_time': datetime.now().isoformat(),
                            'status': 'exception',
                            'error': str(e)
                        }
                    })
        
        self.logger.info(f"Parallel scan completed. {len(results)} results collected")
        return results
    
    def scan_targets_sequential(self, targets: List[str], scan_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scan multiple targets sequentially."""
        self.logger.info(f"Starting sequential scan of {len(targets)} targets")
        
        results = []
        
        for i, target in enumerate(targets, 1):
            self.logger.info(f"Scanning target {i}/{len(targets)}: {target}")
            
            result = self.scan_single_target(target, scan_config)
            results.append(result)
            
            # Log progress
            progress = (i / len(targets)) * 100
            self.logger.info(f"Progress: {i}/{len(targets)} ({progress:.1f}%)")
        
        self.logger.info("Sequential scan completed")
        return results
    
    def generate_batch_report(self, results: List[Dict[str, Any]], output_dir: str):
        """Generate comprehensive batch scan reports."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate summary report
        self._generate_summary_report(results, output_path / f"batch_summary_{timestamp}.json")
        
        # Generate detailed CSV report
        self._generate_csv_report(results, output_path / f"batch_detailed_{timestamp}.csv")
        
        # Generate HTML report
        self._generate_html_report(results, output_path / f"batch_report_{timestamp}.html")
        
        # Generate vulnerability summary if vulnerability scanning was performed
        vuln_results = [r for r in results if 'vulnerability_analysis' in r]
        if vuln_results:
            self._generate_vulnerability_report(vuln_results, output_path / f"vulnerability_summary_{timestamp}.json")
        
        self.logger.info(f"Batch reports generated in {output_path}")
    
    def _generate_summary_report(self, results: List[Dict[str, Any]], output_file: Path):
        """Generate JSON summary report."""
        summary = {
            'batch_scan_summary': {
                'total_targets': len(results),
                'successful_scans': len([r for r in results if r.get('batch_scan_metadata', {}).get('status') == 'completed']),
                'failed_scans': len([r for r in results if r.get('batch_scan_metadata', {}).get('status') in ['failed', 'exception']]),
                'scan_timestamp': datetime.now().isoformat(),
            },
            'target_results': []
        }
        
        for result in results:
            metadata = result.get('batch_scan_metadata', {})
            target_summary = {
                'target': metadata.get('target', 'unknown'),
                'status': metadata.get('status', 'unknown'),
                'scan_time': metadata.get('scan_time', ''),
            }
            
            if result.get('stats'):
                target_summary.update({
                    'hosts_up': result['stats'].get('uphosts', 0),
                    'hosts_total': result['stats'].get('totalhosts', 0)
                })
            
            if 'vulnerability_analysis' in result:
                vuln_data = result['vulnerability_analysis']
                target_summary['vulnerability_summary'] = {
                    'total_vulnerabilities': vuln_data.get('total_vulnerabilities', 0),
                    'risk_score': vuln_data.get('risk_score', 0),
                    'critical_count': vuln_data.get('severity_counts', {}).get('critical', 0),
                    'high_count': vuln_data.get('severity_counts', {}).get('high', 0)
                }
            
            summary['target_results'].append(target_summary)
        
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
    
    def _generate_csv_report(self, results: List[Dict[str, Any]], output_file: Path):
        """Generate CSV detailed report."""
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'Target', 'Status', 'Scan Time', 'Host IP', 'Host Status',
                'Port', 'Protocol', 'State', 'Service', 'Product', 'Version',
                'Vulnerability Count', 'Risk Score'
            ])
            
            # Write data
            for result in results:
                metadata = result.get('batch_scan_metadata', {})
                target = metadata.get('target', 'unknown')
                status = metadata.get('status', 'unknown')
                scan_time = metadata.get('scan_time', '')
                
                vuln_count = 0
                risk_score = 0
                if 'vulnerability_analysis' in result:
                    vuln_data = result['vulnerability_analysis']
                    vuln_count = vuln_data.get('total_vulnerabilities', 0)
                    risk_score = vuln_data.get('risk_score', 0)
                
                if status == 'completed' and 'scan' in result:
                    # Process scan results
                    for host_ip, host_data in result['scan'].items():
                        if host_ip == 'target':
                            continue
                        
                        host_status = host_data.get('status', {}).get('state', 'unknown')
                        
                        # Process TCP ports
                        for port, port_data in host_data.get('tcp', {}).items():
                            writer.writerow([
                                target, status, scan_time, host_ip, host_status,
                                port, 'tcp', port_data.get('state', ''),
                                port_data.get('name', ''), port_data.get('product', ''),
                                port_data.get('version', ''), vuln_count, risk_score
                            ])
                        
                        # If no ports, write host info only
                        if not host_data.get('tcp') and not host_data.get('udp'):
                            writer.writerow([
                                target, status, scan_time, host_ip, host_status,
                                '', '', '', '', '', '', vuln_count, risk_score
                            ])
                else:
                    # Failed scan
                    writer.writerow([
                        target, status, scan_time, '', '',
                        '', '', '', '', '', '', 0, 0
                    ])
    
    def _generate_html_report(self, results: List[Dict[str, Any]], output_file: Path):
        """Generate HTML report."""
        successful_scans = [r for r in results if r.get('batch_scan_metadata', {}).get('status') == 'completed']
        failed_scans = len(results) - len(successful_scans)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>NMAP-AI Batch Scan Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
                .summary {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .stat-box {{ text-align: center; padding: 15px; border-radius: 5px; background: #e9ecef; }}
                .target {{ margin: 15px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .success {{ border-left: 5px solid #28a745; }}
                .failed {{ border-left: 5px solid #dc3545; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>NMAP-AI Batch Scan Report</h1>
                <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Total Targets:</strong> {len(results)}</p>
            </div>
            
            <div class="summary">
                <div class="stat-box">
                    <h3>{len(successful_scans)}</h3>
                    <p>Successful Scans</p>
                </div>
                <div class="stat-box">
                    <h3>{failed_scans}</h3>
                    <p>Failed Scans</p>
                </div>
                <div class="stat-box">
                    <h3>{sum(len(r.get('scan', {}).get(host, {}).get('tcp', {})) for r in successful_scans for host in r.get('scan', {}) if host != 'target')}</h3>
                    <p>Open Ports Found</p>
                </div>
            </div>
            
            <h2>Scan Results</h2>
        """
        
        for result in results:
            metadata = result.get('batch_scan_metadata', {})
            target = metadata.get('target', 'unknown')
            status = metadata.get('status', 'unknown')
            
            status_class = 'success' if status == 'completed' else 'failed'
            
            html_content += f"""
            <div class="target {status_class}">
                <h3>Target: {target}</h3>
                <p><strong>Status:</strong> {status}</p>
                <p><strong>Scan Time:</strong> {metadata.get('scan_time', 'unknown')}</p>
            """
            
            if status == 'completed' and 'scan' in result:
                # Show scan results
                html_content += "<h4>Discovered Hosts and Ports:</h4>"
                html_content += """
                <table>
                    <tr><th>Host</th><th>Port</th><th>Service</th><th>Version</th></tr>
                """
                
                for host_ip, host_data in result['scan'].items():
                    if host_ip == 'target':
                        continue
                    
                    for port, port_data in host_data.get('tcp', {}).items():
                        if port_data.get('state') == 'open':
                            html_content += f"""
                            <tr>
                                <td>{host_ip}</td>
                                <td>{port}/tcp</td>
                                <td>{port_data.get('name', '')}</td>
                                <td>{port_data.get('product', '')} {port_data.get('version', '')}</td>
                            </tr>
                            """
                
                html_content += "</table>"
                
                # Show vulnerability summary if available
                if 'vulnerability_analysis' in result:
                    vuln_data = result['vulnerability_analysis']
                    html_content += f"""
                    <h4>Vulnerability Summary:</h4>
                    <p><strong>Total Vulnerabilities:</strong> {vuln_data.get('total_vulnerabilities', 0)}</p>
                    <p><strong>Risk Score:</strong> {vuln_data.get('risk_score', 0):.1f}/10</p>
                    """
            
            elif status in ['failed', 'exception']:
                error = metadata.get('error', 'Unknown error')
                html_content += f"<p><strong>Error:</strong> {error}</p>"
            
            html_content += "</div>"
        
        html_content += """
        </body>
        </html>
        """
        
        with open(output_file, 'w') as f:
            f.write(html_content)
    
    def _generate_vulnerability_report(self, results: List[Dict[str, Any]], output_file: Path):
        """Generate vulnerability-focused report."""
        vuln_summary = {
            'vulnerability_batch_report': {
                'total_targets_analyzed': len(results),
                'total_vulnerabilities': sum(r.get('vulnerability_analysis', {}).get('total_vulnerabilities', 0) for r in results),
                'average_risk_score': sum(r.get('vulnerability_analysis', {}).get('risk_score', 0) for r in results) / len(results) if results else 0,
                'report_timestamp': datetime.now().isoformat()
            },
            'target_vulnerabilities': []
        }
        
        for result in results:
            metadata = result.get('batch_scan_metadata', {})
            vuln_data = result.get('vulnerability_analysis', {})
            
            target_vuln = {
                'target': metadata.get('target', 'unknown'),
                'total_vulnerabilities': vuln_data.get('total_vulnerabilities', 0),
                'risk_score': vuln_data.get('risk_score', 0),
                'severity_breakdown': vuln_data.get('severity_counts', {}),
                'top_recommendations': vuln_data.get('recommendations', [])[:5]  # Top 5 recommendations
            }
            
            vuln_summary['target_vulnerabilities'].append(target_vuln)
        
        with open(output_file, 'w') as f:
            json.dump(vuln_summary, f, indent=2)


def main():
    """Main function for batch scanning example."""
    parser = argparse.ArgumentParser(description="NMAP-AI Batch Scanning Example")
    parser.add_argument("--targets-file", "-f", required=True, help="File containing target IPs/ranges (one per line)")
    parser.add_argument("--output-dir", "-o", default="batch_results", help="Output directory for results")
    parser.add_argument("--parallel", action="store_true", help="Perform parallel scanning")
    parser.add_argument("--workers", type=int, default=5, help="Number of parallel workers (default: 5)")
    parser.add_argument("--ports", "-p", default="1-1000", help="Port range to scan")
    parser.add_argument("--ai-scan", action="store_true", help="Use AI-powered scanning")
    parser.add_argument("--vuln-scan", action="store_true", help="Enable vulnerability detection")
    parser.add_argument("--timing", default="T3", help="Timing template (T0-T5)")
    parser.add_argument("--timeout", type=int, default=300, help="Scan timeout per target")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Setup logging
    logger = get_logger("batch_scan_example", level="DEBUG" if args.verbose else "INFO")
    
    try:
        # Initialize configuration
        config = Config()
        
        # Create batch scanner
        batch_scanner = BatchScanner(config)
        
        # Load targets
        logger.info(f"Loading targets from {args.targets_file}")
        targets = batch_scanner.load_targets_from_file(args.targets_file)
        
        if not targets:
            logger.error("No targets loaded")
            sys.exit(1)
        
        # Configure scan options
        scan_config = {
            'ports': args.ports,
            'timing_template': args.timing,
            'timeout': args.timeout,
            'ai_scan': args.ai_scan,
            'vuln_scan': args.vuln_scan,
            'service_detection': True,
            'version_detection': True
        }
        
        logger.info(f"Batch scan configuration: {scan_config}")
        
        # Perform batch scanning
        start_time = datetime.now()
        
        if args.parallel:
            logger.info(f"Starting parallel batch scan with {args.workers} workers")
            results = batch_scanner.scan_targets_parallel(targets, scan_config, args.workers)
        else:
            logger.info("Starting sequential batch scan")
            results = batch_scanner.scan_targets_sequential(targets, scan_config)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"Batch scan completed in {duration:.2f} seconds")
        
        # Generate reports
        logger.info(f"Generating batch reports in {args.output_dir}")
        batch_scanner.generate_batch_report(results, args.output_dir)
        
        # Print summary
        successful = len([r for r in results if r.get('batch_scan_metadata', {}).get('status') == 'completed'])
        failed = len(results) - successful
        
        print(f"\nBatch Scan Summary:")
        print(f"  Total Targets: {len(targets)}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Duration: {duration:.2f} seconds")
        print(f"  Reports saved to: {args.output_dir}")
        
        if args.vuln_scan:
            total_vulns = sum(r.get('vulnerability_analysis', {}).get('total_vulnerabilities', 0) for r in results)
            avg_risk = sum(r.get('vulnerability_analysis', {}).get('risk_score', 0) for r in results) / len(results) if results else 0
            print(f"  Total Vulnerabilities Found: {total_vulns}")
            print(f"  Average Risk Score: {avg_risk:.2f}/10")
        
        logger.info("Batch scanning completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Batch scan interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Batch scan failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
