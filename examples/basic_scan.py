"""
Basic example demonstrating NMAP-AI network scanning capabilities.
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from nmap_ai.core.scanner import NmapAIScanner
from nmap_ai.utils.logger import get_logger
from nmap_ai.config import Config


def main():
    """Run basic network scan example."""
    parser = argparse.ArgumentParser(description="Basic NMAP-AI scan example")
    parser.add_argument("--target", required=True, help="Target IP or range to scan")
    parser.add_argument("--ports", default="22,80,443", help="Ports to scan")
    parser.add_argument("--timeout", type=int, default=300, help="Scan timeout")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Setup logging
    logger = get_logger("basic_scan", level="DEBUG" if args.verbose else "INFO")
    
    try:
        # Initialize configuration
        config = Config()
        
        # Create scanner instance
        logger.info("Initializing NMAP-AI scanner...")
        scanner = NmapAIScanner(config)
        
        # Configure scan parameters
        scan_options = {
            'ports': args.ports,
            'timeout': args.timeout,
            'service_detection': True,
            'version_detection': True,
            'timing_template': 'T3'
        }
        
        logger.info(f"Starting scan of {args.target}")
        logger.info(f"Scan options: {scan_options}")
        
        # Perform the scan
        results = scanner.scan(args.target, **scan_options)
        
        # Display results
        print("\n" + "="*60)
        print("SCAN RESULTS")
        print("="*60)
        
        if not results or 'scan' not in results:
            print("No scan results found.")
            return
        
        scan_data = results['scan']
        
        for host_ip, host_data in scan_data.items():
            if host_ip == 'target':
                continue
                
            print(f"\nHost: {host_ip}")
            print(f"Status: {host_data.get('status', {}).get('state', 'unknown')}")
            
            # Display TCP ports
            tcp_ports = host_data.get('tcp', {})
            if tcp_ports:
                print("\nOpen TCP Ports:")
                for port, port_data in tcp_ports.items():
                    state = port_data.get('state', 'unknown')
                    service = port_data.get('name', 'unknown')
                    product = port_data.get('product', '')
                    version = port_data.get('version', '')
                    
                    service_info = f"{service}"
                    if product:
                        service_info += f" ({product}"
                        if version:
                            service_info += f" {version}"
                        service_info += ")"
                    
                    print(f"  {port:>5}/{state:<8} {service_info}")
            
            # Display UDP ports if any
            udp_ports = host_data.get('udp', {})
            if udp_ports:
                print("\nOpen UDP Ports:")
                for port, port_data in udp_ports.items():
                    state = port_data.get('state', 'unknown')
                    service = port_data.get('name', 'unknown')
                    print(f"  {port:>5}/udp/{state:<8} {service}")
        
        # Display scan statistics
        print(f"\nScan completed successfully!")
        print(f"Scan time: {results.get('runtime', {}).get('elapsed', 'unknown')} seconds")
        
        # Save results
        output_file = f"basic_scan_{args.target.replace('/', '_')}.json"
        scanner.save_results(results, output_file)
        logger.info(f"Results saved to {output_file}")
        
    except KeyboardInterrupt:
        logger.info("Scan interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during scan: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
