"""
Result parser for NMAP-AI
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..utils.logger import get_logger


class ResultParser:
    """
    Parser for Nmap scan results.
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def parse_scan_result(self, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse raw Nmap scan result into structured format.
        
        Args:
            raw_result: Raw scan result from python-nmap
        
        Returns:
            Parsed and structured scan result
        """
        if not raw_result:
            return {
                'status': 'no_data',
                'open_ports': [],
                'services': [],
                'os': {},
                'vulnerabilities': []
            }
        
        parsed = {
            'status': raw_result.get('state', 'unknown'),
            'open_ports': [],
            'services': [],
            'os': {},
            'hostnames': [],
            'vulnerabilities': [],
            'scan_time': datetime.now().isoformat()
        }
        
        # Parse hostnames
        if 'hostnames' in raw_result:
            for hostname_info in raw_result['hostnames']:
                parsed['hostnames'].append({
                    'name': hostname_info.get('name', ''),
                    'type': hostname_info.get('type', '')
                })
        
        # Parse protocols and ports
        if hasattr(raw_result, 'all_protocols'):
            for protocol in raw_result.all_protocols():
                if protocol in raw_result:
                    for port in raw_result[protocol].keys():
                        port_info = raw_result[protocol][port]
                        
                        if port_info.get('state') == 'open':
                            parsed['open_ports'].append({
                                'port': port,
                                'protocol': protocol,
                                'state': port_info.get('state'),
                                'reason': port_info.get('reason', ''),
                                'name': port_info.get('name', ''),
                                'product': port_info.get('product', ''),
                                'version': port_info.get('version', ''),
                                'extrainfo': port_info.get('extrainfo', ''),
                                'conf': port_info.get('conf', '')
                            })
                            
                            # Add to services list
                            service_name = port_info.get('name', 'unknown')
                            if service_name not in parsed['services']:
                                parsed['services'].append(service_name)
        else:
            # Fallback for dictionary-like raw results
            for protocol in ['tcp', 'udp', 'sctp']:
                if protocol in raw_result:
                    for port, port_info in raw_result[protocol].items():
                        if port_info.get('state') == 'open':
                            parsed['open_ports'].append({
                                'port': port,
                                'protocol': protocol,
                                'state': port_info.get('state'),
                                'reason': port_info.get('reason', ''),
                                'name': port_info.get('name', ''),
                                'product': port_info.get('product', ''),
                                'version': port_info.get('version', ''),
                                'extrainfo': port_info.get('extrainfo', ''),
                                'conf': port_info.get('conf', '')
                            })
                            
                            service_name = port_info.get('name', 'unknown')
                            if service_name not in parsed['services']:
                                parsed['services'].append(service_name)
        
        # Parse OS information
        if 'osmatch' in raw_result:
            parsed['os']['matches'] = raw_result['osmatch']
        
        if 'osclass' in raw_result:
            parsed['os']['classes'] = raw_result['osclass']
        
        # Parse fingerprint
        if 'fingerprint' in raw_result:
            parsed['fingerprint'] = raw_result['fingerprint']
        
        return parsed
    
    def parse_xml_result(self, xml_content: str) -> Dict[str, Any]:
        """
        Parse Nmap XML output.
        
        Args:
            xml_content: XML content from Nmap
        
        Returns:
            Parsed scan results
        """
        try:
            root = ET.fromstring(xml_content)
            
            results = {
                'scan_info': self._parse_scan_info(root),
                'hosts': [],
                'run_stats': self._parse_run_stats(root)
            }
            
            # Parse each host
            for host_elem in root.findall('host'):
                host_result = self._parse_host_xml(host_elem)
                results['hosts'].append(host_result)
            
            return results
            
        except ET.ParseError as e:
            self.logger.error(f"XML parsing error: {e}")
            return {'error': f'XML parsing failed: {e}'}
    
    def _parse_scan_info(self, root: ET.Element) -> Dict[str, Any]:
        """Parse scan information from XML."""
        scan_info = {}
        
        scaninfo_elem = root.find('scaninfo')
        if scaninfo_elem is not None:
            scan_info = {
                'type': scaninfo_elem.get('type', ''),
                'protocol': scaninfo_elem.get('protocol', ''),
                'numservices': scaninfo_elem.get('numservices', ''),
                'services': scaninfo_elem.get('services', '')
            }
        
        return scan_info
    
    def _parse_run_stats(self, root: ET.Element) -> Dict[str, Any]:
        """Parse run statistics from XML."""
        run_stats = {}
        
        runstats_elem = root.find('runstats')
        if runstats_elem is not None:
            finished_elem = runstats_elem.find('finished')
            if finished_elem is not None:
                run_stats = {
                    'time': finished_elem.get('time', ''),
                    'timestr': finished_elem.get('timestr', ''),
                    'elapsed': finished_elem.get('elapsed', ''),
                    'summary': finished_elem.get('summary', ''),
                    'exit': finished_elem.get('exit', '')
                }
        
        return run_stats
    
    def _parse_host_xml(self, host_elem: ET.Element) -> Dict[str, Any]:
        """Parse individual host from XML."""
        host_result = {
            'addresses': [],
            'hostnames': [],
            'status': {},
            'ports': [],
            'os': {},
            'uptime': {},
            'distance': {}
        }
        
        # Parse status
        status_elem = host_elem.find('status')
        if status_elem is not None:
            host_result['status'] = {
                'state': status_elem.get('state', ''),
                'reason': status_elem.get('reason', ''),
                'reason_ttl': status_elem.get('reason_ttl', '')
            }
        
        # Parse addresses
        for addr_elem in host_elem.findall('address'):
            host_result['addresses'].append({
                'addr': addr_elem.get('addr', ''),
                'addrtype': addr_elem.get('addrtype', ''),
                'vendor': addr_elem.get('vendor', '')
            })
        
        # Parse hostnames
        hostnames_elem = host_elem.find('hostnames')
        if hostnames_elem is not None:
            for hostname_elem in hostnames_elem.findall('hostname'):
                host_result['hostnames'].append({
                    'name': hostname_elem.get('name', ''),
                    'type': hostname_elem.get('type', '')
                })
        
        # Parse ports
        ports_elem = host_elem.find('ports')
        if ports_elem is not None:
            for port_elem in ports_elem.findall('port'):
                port_result = self._parse_port_xml(port_elem)
                host_result['ports'].append(port_result)
        
        # Parse OS information
        os_elem = host_elem.find('os')
        if os_elem is not None:
            host_result['os'] = self._parse_os_xml(os_elem)
        
        # Parse uptime
        uptime_elem = host_elem.find('uptime')
        if uptime_elem is not None:
            host_result['uptime'] = {
                'seconds': uptime_elem.get('seconds', ''),
                'lastboot': uptime_elem.get('lastboot', '')
            }
        
        # Parse distance
        distance_elem = host_elem.find('distance')
        if distance_elem is not None:
            host_result['distance'] = {
                'value': distance_elem.get('value', '')
            }
        
        return host_result
    
    def _parse_port_xml(self, port_elem: ET.Element) -> Dict[str, Any]:
        """Parse individual port from XML."""
        port_result = {
            'protocol': port_elem.get('protocol', ''),
            'portid': port_elem.get('portid', ''),
            'state': {},
            'service': {},
            'scripts': []
        }
        
        # Parse state
        state_elem = port_elem.find('state')
        if state_elem is not None:
            port_result['state'] = {
                'state': state_elem.get('state', ''),
                'reason': state_elem.get('reason', ''),
                'reason_ttl': state_elem.get('reason_ttl', '')
            }
        
        # Parse service
        service_elem = port_elem.find('service')
        if service_elem is not None:
            port_result['service'] = {
                'name': service_elem.get('name', ''),
                'product': service_elem.get('product', ''),
                'version': service_elem.get('version', ''),
                'extrainfo': service_elem.get('extrainfo', ''),
                'method': service_elem.get('method', ''),
                'conf': service_elem.get('conf', '')
            }
        
        # Parse scripts
        for script_elem in port_elem.findall('script'):
            script_result = {
                'id': script_elem.get('id', ''),
                'output': script_elem.get('output', ''),
                'elements': []
            }
            
            # Parse script elements
            for elem in script_elem.findall('.//elem'):
                script_result['elements'].append({
                    'key': elem.get('key', ''),
                    'value': elem.text or ''
                })
            
            port_result['scripts'].append(script_result)
        
        return port_result
    
    def _parse_os_xml(self, os_elem: ET.Element) -> Dict[str, Any]:
        """Parse OS information from XML."""
        os_result = {
            'portused': [],
            'osmatch': [],
            'osclass': [],
            'osfingerprint': []
        }
        
        # Parse port used for OS detection
        for portused_elem in os_elem.findall('portused'):
            os_result['portused'].append({
                'state': portused_elem.get('state', ''),
                'proto': portused_elem.get('proto', ''),
                'portid': portused_elem.get('portid', '')
            })
        
        # Parse OS matches
        for osmatch_elem in os_elem.findall('osmatch'):
            osmatch_result = {
                'name': osmatch_elem.get('name', ''),
                'accuracy': osmatch_elem.get('accuracy', ''),
                'line': osmatch_elem.get('line', ''),
                'osclass': []
            }
            
            for osclass_elem in osmatch_elem.findall('osclass'):
                osmatch_result['osclass'].append({
                    'type': osclass_elem.get('type', ''),
                    'vendor': osclass_elem.get('vendor', ''),
                    'osfamily': osclass_elem.get('osfamily', ''),
                    'osgen': osclass_elem.get('osgen', ''),
                    'accuracy': osclass_elem.get('accuracy', '')
                })
            
            os_result['osmatch'].append(osmatch_result)
        
        return os_result
    
    def extract_vulnerabilities(self, parsed_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract potential vulnerabilities from scan results.
        
        Args:
            parsed_result: Parsed scan result
        
        Returns:
            List of potential vulnerabilities
        """
        vulnerabilities = []
        
        # Check for common vulnerable services
        vulnerable_services = {
            'ftp': {'port': 21, 'issues': ['Anonymous access', 'Weak encryption']},
            'ssh': {'port': 22, 'issues': ['Weak keys', 'Version vulnerabilities']},
            'telnet': {'port': 23, 'issues': ['Unencrypted communication', 'Weak authentication']},
            'smtp': {'port': 25, 'issues': ['Open relay', 'Weak authentication']},
            'http': {'port': 80, 'issues': ['Unencrypted web traffic', 'Web vulnerabilities']},
            'pop3': {'port': 110, 'issues': ['Unencrypted authentication', 'Weak passwords']},
            'snmp': {'port': 161, 'issues': ['Default community strings', 'Information disclosure']},
            'https': {'port': 443, 'issues': ['SSL/TLS vulnerabilities', 'Certificate issues']}
        }
        
        if 'open_ports' in parsed_result:
            for port_info in parsed_result['open_ports']:
                service_name = port_info.get('name', '').lower()
                port_number = port_info.get('port')
                
                if service_name in vulnerable_services:
                    vuln_info = vulnerable_services[service_name]
                    for issue in vuln_info['issues']:
                        vulnerabilities.append({
                            'type': 'service_vulnerability',
                            'service': service_name,
                            'port': port_number,
                            'issue': issue,
                            'severity': 'medium',
                            'description': f"Potential {issue.lower()} on {service_name} service"
                        })
        
        return vulnerabilities
