"""
Report generation and management command for NMAP-AI CLI.
Handles report creation, formatting, and export functionality.
"""
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from nmap_ai.core.parser import NmapResultParser
from nmap_ai.ai.vulnerability_detector import VulnerabilityDetector
from nmap_ai.utils.logger import get_logger

logger = get_logger(__name__)


def report_command(args: argparse.Namespace) -> int:
    """
    Handle report generation and management commands.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        if args.report_action == 'generate':
            return generate_report(args)
        elif args.report_action == 'list':
            return list_reports(args)
        elif args.report_action == 'export':
            return export_report(args)
        elif args.report_action == 'delete':
            return delete_report(args)
        else:
            logger.error(f"Unknown report action: {args.report_action}")
            return 1
            
    except Exception as e:
        logger.error(f"Report command failed: {e}")
        return 1


def generate_report(args: argparse.Namespace) -> int:
    """Generate a report from scan results."""
    try:
        scan_file = Path(args.scan_file)
        if not scan_file.exists():
            logger.error(f"Scan file not found: {scan_file}")
            return 1
            
        print(f"Generating report from: {scan_file}")
        
        # Parse scan results
        parser = NmapResultParser()
        scan_results = parser.parse_file(str(scan_file))
        
        # Generate vulnerability analysis if requested
        vulnerabilities = []
        if args.include_vulnerabilities:
            print("Running vulnerability analysis...")
            detector = VulnerabilityDetector()
            vulnerabilities = detector.analyze_scan_results(scan_results)
            
        # Generate report based on format
        if args.format == 'json':
            report_data = generate_json_report(scan_results, vulnerabilities)
            output_file = save_json_report(report_data, args.output)
        elif args.format == 'html':
            report_content = generate_html_report(scan_results, vulnerabilities)
            output_file = save_html_report(report_content, args.output)
        elif args.format == 'csv':
            report_content = generate_csv_report(scan_results, vulnerabilities)
            output_file = save_csv_report(report_content, args.output)
        elif args.format == 'xml':
            report_content = generate_xml_report(scan_results, vulnerabilities)
            output_file = save_xml_report(report_content, args.output)
        else:
            logger.error(f"Unsupported format: {args.format}")
            return 1
            
        print(f"Report generated successfully: {output_file}")
        
        # Display summary if verbose
        if args.verbose:
            display_report_summary(scan_results, vulnerabilities)
            
        return 0
        
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        return 1


def list_reports(args: argparse.Namespace) -> int:
    """List available reports."""
    try:
        reports_dir = Path("reports")
        if not reports_dir.exists():
            print("No reports directory found")
            return 0
            
        reports = list(reports_dir.glob("*"))
        if not reports:
            print("No reports found")
            return 0
            
        print(f"Found {len(reports)} reports:")
        print("-" * 60)
        
        for report_file in sorted(reports):
            file_size = report_file.stat().st_size
            file_time = datetime.fromtimestamp(report_file.stat().st_mtime)
            
            print(f"Name: {report_file.name}")
            print(f"Size: {file_size:,} bytes")
            print(f"Modified: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 60)
            
        return 0
        
    except Exception as e:
        logger.error(f"Failed to list reports: {e}")
        return 1


def export_report(args: argparse.Namespace) -> int:
    """Export report to different format."""
    try:
        input_file = Path(args.input_file)
        if not input_file.exists():
            logger.error(f"Report file not found: {input_file}")
            return 1
            
        print(f"Exporting report: {input_file} -> {args.format}")
        
        # Load the report data (assuming it's JSON)
        with open(input_file, 'r') as f:
            report_data = json.load(f)
            
        # Convert to requested format
        if args.format == 'html':
            content = convert_json_to_html(report_data)
            output_file = input_file.with_suffix('.html')
            with open(output_file, 'w') as f:
                f.write(content)
        elif args.format == 'csv':
            content = convert_json_to_csv(report_data)
            output_file = input_file.with_suffix('.csv')
            with open(output_file, 'w') as f:
                f.write(content)
        elif args.format == 'xml':
            content = convert_json_to_xml(report_data)
            output_file = input_file.with_suffix('.xml')
            with open(output_file, 'w') as f:
                f.write(content)
        else:
            logger.error(f"Unsupported export format: {args.format}")
            return 1
            
        print(f"Report exported successfully: {output_file}")
        return 0
        
    except Exception as e:
        logger.error(f"Failed to export report: {e}")
        return 1


def delete_report(args: argparse.Namespace) -> int:
    """Delete a report file."""
    try:
        report_file = Path(args.report_file)
        if not report_file.exists():
            logger.error(f"Report file not found: {report_file}")
            return 1
            
        if not args.force:
            response = input(f"Delete report '{report_file.name}'? [y/N]: ")
            if response.lower() not in ('y', 'yes'):
                print("Delete cancelled")
                return 0
                
        report_file.unlink()
        print(f"Report deleted: {report_file.name}")
        return 0
        
    except Exception as e:
        logger.error(f"Failed to delete report: {e}")
        return 1


def generate_json_report(scan_results: Dict[str, Any], vulnerabilities: List[Dict]) -> Dict[str, Any]:
    """Generate JSON format report."""
    return {
        "report_metadata": {
            "generated_at": datetime.now().isoformat(),
            "tool": "NMAP-AI",
            "version": "1.0.0"
        },
        "scan_results": scan_results,
        "vulnerabilities": vulnerabilities,
        "summary": {
            "total_hosts": len(scan_results.get('hosts', [])),
            "total_vulnerabilities": len(vulnerabilities),
            "scan_duration": scan_results.get('scan_info', {}).get('elapsed', 0)
        }
    }


def generate_html_report(scan_results: Dict[str, Any], vulnerabilities: List[Dict]) -> str:
    """Generate HTML format report."""
    # This would generate a comprehensive HTML report
    # For now, return a basic template
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>NMAP-AI Scan Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background: #2c3e50; color: white; padding: 20px; }}
            .summary {{ background: #ecf0f1; padding: 15px; margin: 20px 0; }}
            .vulnerability {{ border-left: 4px solid #e74c3c; padding: 10px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>NMAP-AI Scan Report</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        <div class="summary">
            <h2>Summary</h2>
            <p>Total Hosts: {len(scan_results.get('hosts', []))}</p>
            <p>Total Vulnerabilities: {len(vulnerabilities)}</p>
        </div>
        <!-- Additional report content would go here -->
    </body>
    </html>
    """


def generate_csv_report(scan_results: Dict[str, Any], vulnerabilities: List[Dict]) -> str:
    """Generate CSV format report."""
    # Basic CSV header
    csv_content = "Host,Port,Service,Version,Vulnerability,Severity\n"
    
    # Add scan data
    for host in scan_results.get('hosts', []):
        for port in host.get('ports', []):
            csv_content += f"{host.get('address', '')},{port.get('port', '')},{port.get('service', '')},{port.get('version', '')},None,None\n"
    
    return csv_content


def generate_xml_report(scan_results: Dict[str, Any], vulnerabilities: List[Dict]) -> str:
    """Generate XML format report."""
    # Basic XML structure
    return f"""<?xml version="1.0" encoding="UTF-8"?>
    <nmap_ai_report>
        <metadata>
            <generated>{datetime.now().isoformat()}</generated>
            <tool>NMAP-AI</tool>
            <version>1.0.0</version>
        </metadata>
        <summary>
            <total_hosts>{len(scan_results.get('hosts', []))}</total_hosts>
            <total_vulnerabilities>{len(vulnerabilities)}</total_vulnerabilities>
        </summary>
        <!-- Additional XML content would go here -->
    </nmap_ai_report>"""


def save_json_report(report_data: Dict[str, Any], output_path: Optional[str]) -> Path:
    """Save JSON report to file."""
    if output_path:
        output_file = Path(output_path)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path(f"reports/nmap_ai_report_{timestamp}.json")
        
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(report_data, f, indent=2)
        
    return output_file


def save_html_report(content: str, output_path: Optional[str]) -> Path:
    """Save HTML report to file."""
    if output_path:
        output_file = Path(output_path)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path(f"reports/nmap_ai_report_{timestamp}.html")
        
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(content)
        
    return output_file


def save_csv_report(content: str, output_path: Optional[str]) -> Path:
    """Save CSV report to file."""
    if output_path:
        output_file = Path(output_path)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path(f"reports/nmap_ai_report_{timestamp}.csv")
        
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(content)
        
    return output_file


def save_xml_report(content: str, output_path: Optional[str]) -> Path:
    """Save XML report to file."""
    if output_path:
        output_file = Path(output_path)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path(f"reports/nmap_ai_report_{timestamp}.xml")
        
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(content)
        
    return output_file


def display_report_summary(scan_results: Dict[str, Any], vulnerabilities: List[Dict]):
    """Display a summary of the generated report."""
    print("\n" + "=" * 50)
    print("REPORT SUMMARY")
    print("=" * 50)
    
    print(f"Total Hosts Scanned: {len(scan_results.get('hosts', []))}")
    print(f"Total Open Ports: {sum(len(host.get('ports', [])) for host in scan_results.get('hosts', []))}")
    print(f"Total Vulnerabilities: {len(vulnerabilities)}")
    
    if vulnerabilities:
        severity_counts = {}
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
        print("\nVulnerability Breakdown:")
        for severity, count in severity_counts.items():
            print(f"  {severity.upper()}: {count}")


def convert_json_to_html(report_data: Dict[str, Any]) -> str:
    """Convert JSON report to HTML format."""
    # Implementation would convert JSON data to HTML
    return generate_html_report(
        report_data.get('scan_results', {}),
        report_data.get('vulnerabilities', [])
    )


def convert_json_to_csv(report_data: Dict[str, Any]) -> str:
    """Convert JSON report to CSV format."""
    # Implementation would convert JSON data to CSV
    return generate_csv_report(
        report_data.get('scan_results', {}),
        report_data.get('vulnerabilities', [])
    )


def convert_json_to_xml(report_data: Dict[str, Any]) -> str:
    """Convert JSON report to XML format."""
    # Implementation would convert JSON data to XML
    return generate_xml_report(
        report_data.get('scan_results', {}),
        report_data.get('vulnerabilities', [])
    )


def add_report_parser(subparsers):
    """Add report command parser."""
    report_parser = subparsers.add_parser(
        'report',
        help='Generate and manage scan reports',
        description='Create, export, and manage NMAP-AI scan reports'
    )
    
    report_subparsers = report_parser.add_subparsers(
        dest='report_action',
        help='Report actions',
        required=True
    )
    
    # Generate report
    generate_parser = report_subparsers.add_parser(
        'generate',
        help='Generate report from scan results'
    )
    generate_parser.add_argument(
        'scan_file',
        help='Path to scan results file (XML format)'
    )
    generate_parser.add_argument(
        '--format', '-f',
        choices=['json', 'html', 'csv', 'xml'],
        default='json',
        help='Report format (default: json)'
    )
    generate_parser.add_argument(
        '--output', '-o',
        help='Output file path (default: auto-generated)'
    )
    generate_parser.add_argument(
        '--include-vulnerabilities', '-v',
        action='store_true',
        help='Include vulnerability analysis'
    )
    generate_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Display detailed report summary'
    )
    
    # List reports
    report_subparsers.add_parser(
        'list',
        help='List available reports'
    )
    
    # Export report
    export_parser = report_subparsers.add_parser(
        'export',
        help='Export report to different format'
    )
    export_parser.add_argument(
        'input_file',
        help='Input report file path'
    )
    export_parser.add_argument(
        '--format', '-f',
        choices=['html', 'csv', 'xml'],
        required=True,
        help='Export format'
    )
    
    # Delete report
    delete_parser = report_subparsers.add_parser(
        'delete',
        help='Delete a report file'
    )
    delete_parser.add_argument(
        'report_file',
        help='Report file to delete'
    )
    delete_parser.add_argument(
        '--force',
        action='store_true',
        help='Skip confirmation prompt'
    )
    
    return report_parser
