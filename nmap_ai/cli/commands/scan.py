"""
Scan command implementation for NMAP-AI CLI.
"""

import click
from typing import Optional, List
from pathlib import Path

from ...core.scanner import NmapAIScanner
from ...ai.smart_scanner import SmartScanner
from ...ai.vulnerability_detector import VulnerabilityDetector
from ...config import Config
from ...utils.logger import get_logger


@click.command()
@click.option('--target', '-t', required=True, help='Target IP address, hostname, or CIDR range')
@click.option('--ports', '-p', default='1-1000', help='Port range to scan (default: 1-1000)')
@click.option('--timing', default='T3', help='Timing template (T0-T5, default: T3)')
@click.option('--scan-type', '-s', default='syn', help='Scan type (syn, tcp, udp, ack, etc.)')
@click.option('--output', '-o', help='Output file path')
@click.option('--format', '-f', default='json', help='Output format (json, xml, csv, html)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--ai-scan', is_flag=True, help='Use AI-powered smart scanning')
@click.option('--vuln-scan', is_flag=True, help='Enable vulnerability detection')
@click.option('--script', multiple=True, help='Nmap scripts to run')
@click.option('--script-args', help='Arguments for nmap scripts')
@click.option('--service-detection', is_flag=True, help='Enable service version detection')
@click.option('--os-detection', is_flag=True, help='Enable OS detection')
@click.option('--aggressive', is_flag=True, help='Enable aggressive scanning (-A)')
@click.option('--stealth', is_flag=True, help='Enable stealth scanning')
@click.option('--fragment', is_flag=True, help='Fragment packets')
@click.option('--decoy', help='Use decoy hosts')
@click.option('--source-port', type=int, help='Source port number')
@click.option('--max-rate', type=int, help='Maximum packet rate')
@click.option('--min-rate', type=int, help='Minimum packet rate')
@click.option('--timeout', type=int, default=300, help='Scan timeout in seconds')
@click.option('--threads', type=int, help='Number of parallel threads')
@click.option('--config', help='Configuration file path')
@click.option('--profile', help='Scan profile name')
@click.option('--save-raw', is_flag=True, help='Save raw nmap output')
@click.pass_context
def scan_command(ctx, **kwargs):
    """
    Perform network scanning with optional AI enhancements.
    
    Examples:
        nmap-ai scan -t 192.168.1.1 -p 22,80,443
        nmap-ai scan -t 192.168.1.0/24 --ai-scan --vuln-scan
        nmap-ai scan -t example.com --aggressive -o scan_results.json
    """
    logger = get_logger("cli.scan")
    
    try:
        # Load configuration
        config_path = kwargs.get('config')
        config = Config(config_path) if config_path else Config()
        
        # Apply profile if specified
        profile = kwargs.get('profile')
        if profile:
            config.load_profile(profile)
        
        # Set up scan options
        scan_options = build_scan_options(kwargs, config)
        
        # Initialize scanner
        if kwargs.get('ai_scan'):
            scanner = SmartScanner(config)
            logger.info("Using AI-powered smart scanner")
        else:
            scanner = NmapAIScanner(config)
            logger.info("Using standard scanner")
        
        # Perform scan
        target = kwargs['target']
        logger.info(f"Starting scan of {target}")
        
        if kwargs.get('verbose'):
            click.echo(f"Target: {target}")
            click.echo(f"Ports: {kwargs.get('ports', '1-1000')}")
            click.echo(f"Options: {scan_options}")
        
        results = scanner.scan(target, **scan_options)
        
        # Post-process results
        if kwargs.get('vuln_scan'):
            logger.info("Running vulnerability detection")
            vuln_detector = VulnerabilityDetector(config)
            vuln_report = vuln_detector.analyze_scan_results(results)
            
            # Add vulnerability report to results
            results['vulnerability_report'] = {
                'total_vulnerabilities': vuln_report.total_vulnerabilities,
                'risk_score': vuln_report.risk_score,
                'vulnerabilities': [
                    {
                        'cve_id': v.cve_id,
                        'severity': v.severity,
                        'score': v.score,
                        'description': v.description,
                        'affected_service': v.affected_service,
                        'port': v.port
                    }
                    for v in vuln_report.vulnerabilities
                ],
                'recommendations': vuln_report.recommendations
            }
        
        # Output results
        output_path = kwargs.get('output')
        output_format = kwargs.get('format', 'json')
        
        if output_path:
            save_results(results, output_path, output_format, logger)
        else:
            display_results(results, output_format, kwargs.get('verbose', False))
        
        # Save raw output if requested
        if kwargs.get('save_raw'):
            raw_output_path = f"{target.replace('/', '_')}_raw.xml"
            scanner.save_raw_results(raw_output_path)
            logger.info(f"Raw scan results saved to {raw_output_path}")
        
        logger.info("Scan completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Scan interrupted by user")
        ctx.exit(1)
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        if kwargs.get('verbose'):
            import traceback
            traceback.print_exc()
        ctx.exit(1)


def build_scan_options(kwargs: dict, config: Config) -> dict:
    """Build scan options dictionary from CLI arguments and config."""
    options = {}
    
    # Basic scan options
    if kwargs.get('ports'):
        options['ports'] = kwargs['ports']
    if kwargs.get('timing'):
        options['timing_template'] = kwargs['timing']
    if kwargs.get('scan_type'):
        options['scan_type'] = kwargs['scan_type']
    if kwargs.get('timeout'):
        options['timeout'] = kwargs['timeout']
    if kwargs.get('threads'):
        options['threads'] = kwargs['threads']
    
    # Detection options
    if kwargs.get('service_detection'):
        options['service_detection'] = True
    if kwargs.get('os_detection'):
        options['os_detection'] = True
    if kwargs.get('aggressive'):
        options['aggressive'] = True
    
    # Stealth options
    if kwargs.get('stealth'):
        options['stealth'] = True
    if kwargs.get('fragment'):
        options['fragment'] = True
    if kwargs.get('decoy'):
        options['decoy'] = kwargs['decoy']
    if kwargs.get('source_port'):
        options['source_port'] = kwargs['source_port']
    
    # Rate limiting
    if kwargs.get('max_rate'):
        options['max_rate'] = kwargs['max_rate']
    if kwargs.get('min_rate'):
        options['min_rate'] = kwargs['min_rate']
    
    # Scripts
    if kwargs.get('script'):
        options['scripts'] = list(kwargs['script'])
    if kwargs.get('script_args'):
        options['script_args'] = kwargs['script_args']
    
    return options


def save_results(results: dict, output_path: str, format_type: str, logger):
    """Save scan results to file."""
    import json
    import csv
    from xml.etree.ElementTree import Element, SubElement, tostring
    from xml.dom import minidom
    
    output_file = Path(output_path)
    
    try:
        if format_type.lower() == 'json':
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
        
        elif format_type.lower() == 'csv':
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Host', 'Port', 'State', 'Service', 'Version'])
                
                for host_ip, host_data in results.get('scan', {}).items():
                    if host_ip == 'target':
                        continue
                    
                    for port, port_data in host_data.get('tcp', {}).items():
                        writer.writerow([
                            host_ip,
                            port,
                            port_data.get('state', ''),
                            port_data.get('name', ''),
                            f"{port_data.get('product', '')} {port_data.get('version', '')}".strip()
                        ])
        
        elif format_type.lower() == 'xml':
            root = Element('nmapai_scan')
            
            for host_ip, host_data in results.get('scan', {}).items():
                if host_ip == 'target':
                    continue
                    
                host_elem = SubElement(root, 'host')
                host_elem.set('ip', host_ip)
                
                ports_elem = SubElement(host_elem, 'ports')
                for port, port_data in host_data.get('tcp', {}).items():
                    port_elem = SubElement(ports_elem, 'port')
                    port_elem.set('portid', str(port))
                    port_elem.set('protocol', 'tcp')
                    
                    state_elem = SubElement(port_elem, 'state')
                    state_elem.set('state', port_data.get('state', ''))
                    
                    service_elem = SubElement(port_elem, 'service')
                    service_elem.set('name', port_data.get('name', ''))
                    service_elem.set('product', port_data.get('product', ''))
                    service_elem.set('version', port_data.get('version', ''))
            
            xml_str = minidom.parseString(tostring(root)).toprettyxml(indent="  ")
            with open(output_file, 'w') as f:
                f.write(xml_str)
        
        elif format_type.lower() == 'html':
            html_content = generate_html_report(results)
            with open(output_file, 'w') as f:
                f.write(html_content)
        
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        logger.info(f"Results saved to {output_file}")
        
    except Exception as e:
        logger.error(f"Failed to save results: {e}")
        raise


def display_results(results: dict, format_type: str, verbose: bool):
    """Display scan results to console."""
    if format_type.lower() == 'json':
        import json
        click.echo(json.dumps(results, indent=2, default=str))
        return
    
    # Default text format
    scan_data = results.get('scan', {})
    
    for host_ip, host_data in scan_data.items():
        if host_ip == 'target':
            continue
        
        click.echo(f"\nHost: {host_ip}")
        
        status = host_data.get('status', {})
        if status:
            click.echo(f"Status: {status.get('state', 'unknown')}")
        
        # TCP ports
        tcp_ports = host_data.get('tcp', {})
        if tcp_ports:
            click.echo("\nOpen TCP Ports:")
            for port, port_data in tcp_ports.items():
                state = port_data.get('state', 'unknown')
                service = port_data.get('name', 'unknown')
                product = port_data.get('product', '')
                version = port_data.get('version', '')
                
                service_info = service
                if product:
                    service_info += f" ({product}"
                    if version:
                        service_info += f" {version}"
                    service_info += ")"
                
                click.echo(f"  {port:>5}/{state:<8} {service_info}")
        
        # UDP ports
        udp_ports = host_data.get('udp', {})
        if udp_ports:
            click.echo("\nOpen UDP Ports:")
            for port, port_data in udp_ports.items():
                state = port_data.get('state', 'unknown')
                service = port_data.get('name', 'unknown')
                click.echo(f"  {port:>5}/udp/{state:<8} {service}")
        
        # Vulnerability report if available
        vuln_report = results.get('vulnerability_report')
        if vuln_report and verbose:
            click.echo(f"\nVulnerability Summary:")
            click.echo(f"  Total Vulnerabilities: {vuln_report['total_vulnerabilities']}")
            click.echo(f"  Risk Score: {vuln_report['risk_score']:.1f}/10")
            
            if vuln_report['vulnerabilities']:
                click.echo("\nTop Vulnerabilities:")
                for vuln in vuln_report['vulnerabilities'][:5]:  # Show top 5
                    click.echo(f"  {vuln['cve_id']} ({vuln['severity']}) - {vuln['description'][:80]}...")


def generate_html_report(results: dict) -> str:
    """Generate HTML report from scan results."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NMAP-AI Scan Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { background: #f8f9fa; padding: 20px; border-radius: 5px; }
            .host { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
            .port-table { width: 100%; border-collapse: collapse; margin: 10px 0; }
            .port-table th, .port-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            .port-table th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>NMAP-AI Scan Report</h1>
            <p><strong>Generated:</strong> """ + str(results.get('runtime', {}).get('timestr', '')) + """</p>
        </div>
    """
    
    scan_data = results.get('scan', {})
    for host_ip, host_data in scan_data.items():
        if host_ip == 'target':
            continue
        
        html += f"""
        <div class="host">
            <h2>Host: {host_ip}</h2>
            <p><strong>Status:</strong> {host_data.get('status', {}).get('state', 'unknown')}</p>
        """
        
        tcp_ports = host_data.get('tcp', {})
        if tcp_ports:
            html += """
            <h3>TCP Ports</h3>
            <table class="port-table">
                <tr><th>Port</th><th>State</th><th>Service</th><th>Version</th></tr>
            """
            
            for port, port_data in tcp_ports.items():
                html += f"""
                <tr>
                    <td>{port}</td>
                    <td>{port_data.get('state', '')}</td>
                    <td>{port_data.get('name', '')}</td>
                    <td>{port_data.get('product', '')} {port_data.get('version', '')}</td>
                </tr>
                """
            
            html += "</table>"
        
        html += "</div>"
    
    html += """
    </body>
    </html>
    """
    
    return html
