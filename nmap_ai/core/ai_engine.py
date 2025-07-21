"""
AI Engine for NMAP-AI - Core AI processing functionality
"""

import json
import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from ..utils.logger import get_logger
from .parser import ResultParser


class AIEngine:
    """
    Core AI engine for NMAP-AI providing intelligent scanning capabilities.
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.parser = ResultParser()
        self.scan_patterns = self._load_scan_patterns()
        self.vulnerability_database = self._load_vulnerability_database()
    
    def optimize_scan_arguments(
        self, 
        targets: List[str], 
        ports: str, 
        base_arguments: str
    ) -> str:
        """
        Use AI to optimize Nmap scan arguments based on targets and context.
        
        Args:
            targets: List of target hosts/networks
            ports: Port specification
            base_arguments: Base Nmap arguments
        
        Returns:
            Optimized Nmap arguments
        """
        self.logger.info("AI optimizing scan arguments")
        
        optimizations = []
        
        # Analyze target patterns
        target_analysis = self._analyze_targets(targets)
        
        # Add timing optimization based on target count
        if len(targets) > 100:
            optimizations.append('-T4')  # Aggressive timing for large scans
        elif len(targets) > 10:
            optimizations.append('-T3')  # Normal timing
        else:
            optimizations.append('-T2')  # Polite timing for small scans
        
        # Add service detection if not present
        if '-sV' not in base_arguments and '--version-detect' not in base_arguments:
            optimizations.append('-sV')
        
        # Add OS detection for comprehensive scanning
        if '-O' not in base_arguments and len(targets) <= 50:  # Avoid OS detection for large scans
            optimizations.append('-O')
        
        # Add script scanning based on target analysis
        if target_analysis['likely_web_servers'] and '--script' not in base_arguments:
            optimizations.append('--script=http-*')
        elif target_analysis['mixed_services']:
            optimizations.append('--script=safe')
        
        # Combine optimizations
        optimized_args = base_arguments + ' ' + ' '.join(optimizations)
        
        self.logger.info(f"Optimized arguments: {optimized_args}")
        return optimized_args.strip()
    
    def _analyze_targets(self, targets: List[str]) -> Dict[str, Any]:
        """Analyze target patterns to determine likely services."""
        analysis = {
            'likely_web_servers': False,
            'likely_databases': False,
            'mixed_services': True,
            'network_size': len(targets)
        }
        
        # Simple heuristics based on common patterns
        web_indicators = ['web', 'www', 'http', 'api']
        db_indicators = ['db', 'database', 'mysql', 'postgres', 'sql']
        
        for target in targets:
            target_lower = target.lower()
            if any(indicator in target_lower for indicator in web_indicators):
                analysis['likely_web_servers'] = True
            if any(indicator in target_lower for indicator in db_indicators):
                analysis['likely_databases'] = True
        
        return analysis
    
    def enhance_results(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance scan results with AI analysis and insights.
        
        Args:
            scan_results: Raw scan results
        
        Returns:
            Enhanced results with AI insights
        """
        self.logger.info("AI enhancing scan results")
        
        enhanced_results = scan_results.copy()
        
        # Add AI analysis for each target
        if 'results' in enhanced_results:
            for target, result in enhanced_results['results'].items():
                if 'parsed' in result:
                    ai_analysis = self._analyze_target_result(target, result['parsed'])
                    result['ai_analysis'] = ai_analysis
        
        # Add overall scan insights
        enhanced_results['ai_insights'] = self._generate_scan_insights(enhanced_results)
        
        return enhanced_results
    
    def _analyze_target_result(self, target: str, parsed_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze individual target results."""
        analysis = {
            'risk_level': 'low',
            'security_issues': [],
            'recommendations': [],
            'service_fingerprints': []
        }
        
        open_ports = parsed_result.get('open_ports', [])
        services = parsed_result.get('services', [])
        
        # Assess risk level based on open ports and services
        high_risk_ports = [21, 23, 135, 139, 445, 1433, 3306, 3389, 5432]
        medium_risk_ports = [25, 53, 80, 110, 143, 993, 995]
        
        high_risk_count = sum(1 for port_info in open_ports 
                             if port_info.get('port') in high_risk_ports)
        medium_risk_count = sum(1 for port_info in open_ports 
                               if port_info.get('port') in medium_risk_ports)
        
        if high_risk_count > 0:
            analysis['risk_level'] = 'high'
        elif medium_risk_count > 2:
            analysis['risk_level'] = 'medium'
        
        # Identify security issues
        for port_info in open_ports:
            port = port_info.get('port')
            service = port_info.get('name', '').lower()
            
            if port == 23:  # Telnet
                analysis['security_issues'].append({
                    'type': 'unencrypted_protocol',
                    'port': port,
                    'service': service,
                    'severity': 'high',
                    'description': 'Telnet transmits data in plaintext'
                })
            
            elif port == 21 and 'ftp' in service:  # FTP
                analysis['security_issues'].append({
                    'type': 'potentially_insecure',
                    'port': port,
                    'service': service,
                    'severity': 'medium',
                    'description': 'FTP may allow anonymous access or use weak authentication'
                })
            
            elif port in [135, 139, 445]:  # Windows services
                analysis['security_issues'].append({
                    'type': 'windows_services',
                    'port': port,
                    'service': service,
                    'severity': 'medium',
                    'description': 'Windows networking services exposed'
                })
        
        # Generate recommendations
        if analysis['risk_level'] == 'high':
            analysis['recommendations'].append("Immediate security review recommended")
            analysis['recommendations'].append("Consider firewall rules to restrict access")
        
        if any(issue['type'] == 'unencrypted_protocol' for issue in analysis['security_issues']):
            analysis['recommendations'].append("Replace unencrypted protocols with secure alternatives")
        
        if len(open_ports) > 10:
            analysis['recommendations'].append("Review if all open ports are necessary")
        
        return analysis
    
    def _generate_scan_insights(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall scan insights."""
        insights = {
            'summary': {},
            'trends': [],
            'recommendations': [],
            'statistics': {}
        }
        
        if 'results' not in results:
            return insights
        
        total_targets = len(results['results'])
        successful_scans = sum(1 for r in results['results'].values() 
                              if 'error' not in r)
        
        # Calculate statistics
        insights['statistics'] = {
            'total_targets': total_targets,
            'successful_scans': successful_scans,
            'scan_success_rate': (successful_scans / total_targets) * 100 if total_targets > 0 else 0
        }
        
        # Analyze risk distribution
        risk_distribution = {'high': 0, 'medium': 0, 'low': 0}
        common_services = {}
        
        for result in results['results'].values():
            if 'ai_analysis' in result:
                risk_level = result['ai_analysis'].get('risk_level', 'low')
                risk_distribution[risk_level] += 1
            
            if 'parsed' in result:
                for service in result['parsed'].get('services', []):
                    common_services[service] = common_services.get(service, 0) + 1
        
        insights['summary'] = {
            'risk_distribution': risk_distribution,
            'most_common_services': sorted(common_services.items(), 
                                         key=lambda x: x[1], reverse=True)[:5]
        }
        
        # Generate recommendations
        if risk_distribution['high'] > 0:
            insights['recommendations'].append("High-risk hosts detected - immediate review required")
        
        if successful_scans < total_targets * 0.8:
            insights['recommendations'].append("Low scan success rate - check network connectivity")
        
        return insights
    
    def create_scan_plan(
        self, 
        target: str, 
        profile: str, 
        previous_scans: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create an AI-driven scan plan based on profile and historical data.
        
        Args:
            target: Target to scan
            profile: Scan profile (adaptive, fast, thorough, stealth)
            previous_scans: Previous scan history for learning
        
        Returns:
            Scan plan with optimized parameters
        """
        self.logger.info(f"Creating AI scan plan for {target} with profile {profile}")
        
        plan = {
            'target': target,
            'profile': profile,
            'ports': None,
            'arguments': '',
            'timing': 'T3',
            'insights': {}
        }
        
        # Analyze previous scans for this target
        target_history = [scan for scan in previous_scans 
                         if target in scan.get('targets', [])]
        
        # Set parameters based on profile
        if profile == 'fast':
            plan['ports'] = '1-1000'
            plan['arguments'] = '-T4 -F'
            plan['timing'] = 'T4'
        elif profile == 'thorough':
            plan['ports'] = '1-65535'
            plan['arguments'] = '-T3 -sV -O -A'
            plan['timing'] = 'T3'
        elif profile == 'stealth':
            plan['ports'] = '1-1000'
            plan['arguments'] = '-T1 -sS -f'
            plan['timing'] = 'T1'
        else:  # adaptive
            plan = self._create_adaptive_plan(target, target_history)
        
        # Add insights about the plan
        plan['insights'] = {
            'reasoning': f"Plan optimized for {profile} scanning",
            'estimated_duration': self._estimate_scan_duration(plan),
            'historical_context': f"Based on {len(target_history)} previous scans" if target_history else "No historical data"
        }
        
        return plan
    
    def _create_adaptive_plan(self, target: str, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create adaptive scan plan based on target and history."""
        plan = {
            'ports': '1-1000',
            'arguments': '-T3 -sV',
            'timing': 'T3'
        }
        
        # Adapt based on historical success
        if history:
            # If previous scans were successful, use more comprehensive scanning
            recent_success = any(
                'error' not in scan.get('results', {}).get(target, {})
                for scan in history[-3:]  # Last 3 scans
            )
            
            if recent_success:
                plan['ports'] = '1-10000'
                plan['arguments'] = '-T3 -sV -O --script=safe'
            else:
                # If previous scans failed, use lighter approach
                plan['ports'] = '1-100'
                plan['arguments'] = '-T2'
        
        return plan
    
    def _estimate_scan_duration(self, plan: Dict[str, Any]) -> str:
        """Estimate scan duration based on plan parameters."""
        # Simple estimation based on port count and timing
        port_range = plan.get('ports', '1-1000')
        timing = plan.get('timing', 'T3')
        
        # Parse port count
        port_count = 1000  # Default
        if '-' in port_range:
            try:
                start, end = port_range.split('-')
                port_count = int(end) - int(start) + 1
            except ValueError:
                pass
        
        # Timing multipliers
        timing_multipliers = {'T1': 4.0, 'T2': 2.0, 'T3': 1.0, 'T4': 0.5, 'T5': 0.25}
        multiplier = timing_multipliers.get(timing, 1.0)
        
        # Base estimation: ~1 second per 100 ports
        base_duration = (port_count / 100) * multiplier
        
        if base_duration < 60:
            return f"{base_duration:.0f} seconds"
        elif base_duration < 3600:
            return f"{base_duration/60:.1f} minutes"
        else:
            return f"{base_duration/3600:.1f} hours"
    
    def generate_script(
        self, 
        target_info: Dict[str, Any], 
        script_type: str, 
        requirements: Optional[List[str]]
    ) -> str:
        """
        Generate Nmap script using AI analysis.
        This is a wrapper that delegates to the AIScriptGenerator.
        """
        from ..ai.script_generator import AIScriptGenerator
        
        generator = AIScriptGenerator()
        return generator.create_script(
            target_type=script_type,
            vulnerabilities=requirements,
            stealth_level=target_info.get('stealth_level', 'medium')
        )
    
    def _load_scan_patterns(self) -> Dict[str, Any]:
        """Load scan patterns for AI analysis."""
        return {
            'web_services': {
                'ports': [80, 443, 8080, 8443, 8000, 8888],
                'indicators': ['http', 'https', 'web', 'apache', 'nginx']
            },
            'database_services': {
                'ports': [1433, 3306, 5432, 1521, 27017],
                'indicators': ['mysql', 'postgresql', 'mssql', 'oracle', 'mongodb']
            },
            'network_services': {
                'ports': [22, 23, 21, 25, 53, 69, 123, 161],
                'indicators': ['ssh', 'telnet', 'ftp', 'smtp', 'dns', 'tftp', 'ntp', 'snmp']
            }
        }
    
    def _load_vulnerability_database(self) -> Dict[str, Any]:
        """Load vulnerability database for AI analysis."""
        return {
            'high_risk_services': {
                'telnet': {'port': 23, 'risk': 'high', 'reason': 'Unencrypted protocol'},
                'ftp': {'port': 21, 'risk': 'medium', 'reason': 'Potential anonymous access'},
                'snmp': {'port': 161, 'risk': 'medium', 'reason': 'Information disclosure'},
            },
            'common_vulnerabilities': {
                'web_services': ['XSS', 'SQL Injection', 'Directory Traversal'],
                'ssh_services': ['Weak keys', 'Brute force attacks'],
                'database_services': ['Default credentials', 'SQL injection']
            }
        }
