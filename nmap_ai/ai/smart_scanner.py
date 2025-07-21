"""
Smart scanner with AI optimization for NMAP-AI
"""

import time
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from ..utils.logger import get_logger
from ..core.scanner import NmapAIScanner
from ..core.ai_engine import AIEngine


class SmartScanner:
    """
    AI-powered smart scanner with adaptive capabilities.
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.base_scanner = NmapAIScanner(ai_enabled=True)
        self.ai_engine = AIEngine()
        self.learning_data = []
    
    def smart_scan(
        self,
        target: str,
        optimization_level: str = "balanced",
        ai_model: str = "fast_scan_v2",
        learn_from_previous: bool = True
    ) -> Dict[str, Any]:
        """
        Perform AI-optimized smart scanning.
        
        Args:
            target: Target to scan
            optimization_level: Level of optimization (conservative, balanced, aggressive)
            ai_model: AI model to use for optimization
            learn_from_previous: Whether to use previous scan data for optimization
        
        Returns:
            Smart scan results with AI insights
        """
        self.logger.info(f"Starting smart scan of {target} with {optimization_level} optimization")
        
        start_time = time.time()
        
        # Phase 1: Intelligence Gathering
        intelligence = self._gather_target_intelligence(target)
        self.logger.info(f"Target intelligence gathered: {intelligence['confidence']}% confidence")
        
        # Phase 2: Scan Strategy Planning
        strategy = self._plan_scan_strategy(target, intelligence, optimization_level)
        self.logger.info(f"Scan strategy: {strategy['approach']} with {len(strategy['phases'])} phases")
        
        # Phase 3: Adaptive Scanning
        scan_results = self._execute_adaptive_scan(target, strategy)
        
        # Phase 4: AI Analysis and Enhancement
        enhanced_results = self._enhance_with_ai_analysis(scan_results, intelligence)
        
        # Phase 5: Learning Integration
        if learn_from_previous:
            self._update_learning_data(target, scan_results, enhanced_results)
        
        end_time = time.time()
        
        # Compile final results
        final_results = {
            'scan_id': f"smart_{int(start_time)}",
            'target': target,
            'start_time': datetime.fromtimestamp(start_time).isoformat(),
            'end_time': datetime.fromtimestamp(end_time).isoformat(),
            'duration': end_time - start_time,
            'optimization_level': optimization_level,
            'ai_model': ai_model,
            'intelligence': intelligence,
            'strategy': strategy,
            'results': enhanced_results,
            'ai_confidence': enhanced_results.get('ai_confidence', 0.7),
            'recommendations': enhanced_results.get('recommendations', [])
        }
        
        self.logger.info(f"Smart scan completed in {end_time - start_time:.2f} seconds")
        return final_results
    
    def adaptive_scan(
        self,
        target: str,
        learn_from_previous: bool = True,
        adjust_timing: bool = True,
        max_phases: int = 5
    ) -> Dict[str, Any]:
        """
        Perform adaptive scanning that adjusts based on target responses.
        
        Args:
            target: Target to scan
            learn_from_previous: Use historical data for adaptation
            adjust_timing: Automatically adjust scan timing
            max_phases: Maximum number of scanning phases
        
        Returns:
            Adaptive scan results
        """
        self.logger.info(f"Starting adaptive scan of {target}")
        
        phases = []
        current_knowledge = {}
        
        for phase_num in range(1, max_phases + 1):
            self.logger.info(f"Adaptive scan phase {phase_num}")
            
            # Determine what to scan next based on current knowledge
            phase_plan = self._plan_adaptive_phase(target, current_knowledge, phase_num)
            
            if not phase_plan['worth_continuing']:
                self.logger.info("Adaptive scan determined no further phases needed")
                break
            
            # Execute the phase
            phase_results = self._execute_scan_phase(target, phase_plan)
            phases.append({
                'phase': phase_num,
                'plan': phase_plan,
                'results': phase_results,
                'duration': phase_results.get('duration', 0)
            })
            
            # Update knowledge base
            current_knowledge = self._update_knowledge_base(current_knowledge, phase_results)
            
            # Check if we have enough information
            if self._sufficient_information_gathered(current_knowledge):
                self.logger.info("Sufficient information gathered, ending adaptive scan")
                break
        
        # Compile adaptive results
        adaptive_results = {
            'scan_type': 'adaptive',
            'target': target,
            'phases': phases,
            'total_phases': len(phases),
            'final_knowledge': current_knowledge,
            'adaptive_insights': self._generate_adaptive_insights(phases, current_knowledge)
        }
        
        return adaptive_results
    
    def _gather_target_intelligence(self, target: str) -> Dict[str, Any]:
        """Gather intelligence about the target before main scanning."""
        intelligence = {
            'target': target,
            'target_type': 'unknown',
            'likely_services': [],
            'confidence': 0.0,
            'recommendations': []
        }
        
        # Perform lightweight reconnaissance
        try:
            # Quick ping to check if target is alive
            ping_result = self._quick_ping(target)
            if ping_result['alive']:
                intelligence['confidence'] += 0.3
                intelligence['response_time'] = ping_result['response_time']
            
            # Quick port check on common ports
            common_ports = [22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 993, 995, 1723, 3389, 5900]
            open_ports = self._quick_port_check(target, common_ports)
            
            if open_ports:
                intelligence['confidence'] += 0.4
                intelligence['initial_open_ports'] = open_ports
                
                # Infer likely services
                if 80 in open_ports or 443 in open_ports:
                    intelligence['likely_services'].append('web_server')
                if 22 in open_ports:
                    intelligence['likely_services'].append('ssh_server')
                if 25 in open_ports:
                    intelligence['likely_services'].append('mail_server')
                if 3389 in open_ports:
                    intelligence['likely_services'].append('rdp_server')
            
            # Hostname resolution
            hostname_info = self._resolve_hostname(target)
            if hostname_info:
                intelligence['confidence'] += 0.2
                intelligence['hostname_info'] = hostname_info
            
            # Final confidence adjustment
            intelligence['confidence'] = min(intelligence['confidence'], 1.0)
            
        except Exception as e:
            self.logger.warning(f"Intelligence gathering failed: {e}")
            intelligence['error'] = str(e)
        
        return intelligence
    
    def _plan_scan_strategy(
        self, 
        target: str, 
        intelligence: Dict[str, Any], 
        optimization_level: str
    ) -> Dict[str, Any]:
        """Plan the scanning strategy based on intelligence and optimization level."""
        strategy = {
            'approach': 'adaptive',
            'phases': [],
            'estimated_duration': '5-10 minutes',
            'stealth_level': 'medium'
        }
        
        confidence = intelligence.get('confidence', 0.0)
        likely_services = intelligence.get('likely_services', [])
        
        # Adjust strategy based on optimization level
        if optimization_level == 'aggressive':
            strategy['approach'] = 'comprehensive'
            strategy['stealth_level'] = 'low'
            strategy['phases'] = [
                {'name': 'fast_port_scan', 'ports': '1-65535', 'timing': 'T4'},
                {'name': 'service_detection', 'args': '-sV -O', 'timing': 'T4'},
                {'name': 'script_scanning', 'args': '--script=default,vuln', 'timing': 'T4'}
            ]
        elif optimization_level == 'conservative':
            strategy['approach'] = 'careful'
            strategy['stealth_level'] = 'high'
            strategy['phases'] = [
                {'name': 'slow_port_scan', 'ports': '1-1000', 'timing': 'T1'},
                {'name': 'service_detection', 'args': '-sV', 'timing': 'T2'}
            ]
        else:  # balanced
            strategy['approach'] = 'balanced'
            strategy['stealth_level'] = 'medium'
            
            if confidence > 0.7:
                # High confidence - use targeted approach
                if 'web_server' in likely_services:
                    strategy['phases'] = [
                        {'name': 'web_focused_scan', 'ports': '80,443,8080,8443', 'args': '-sV --script=http-*'},
                        {'name': 'common_ports', 'ports': '1-1000', 'timing': 'T3'}
                    ]
                else:
                    strategy['phases'] = [
                        {'name': 'common_ports', 'ports': '1-1000', 'args': '-sV', 'timing': 'T3'},
                        {'name': 'extended_scan', 'ports': '1001-5000', 'timing': 'T3'}
                    ]
            else:
                # Low confidence - use exploratory approach
                strategy['phases'] = [
                    {'name': 'discovery_scan', 'ports': '1-1000', 'timing': 'T3'},
                    {'name': 'service_analysis', 'args': '-sV -O', 'timing': 'T3'}
                ]
        
        return strategy
    
    def _execute_adaptive_scan(self, target: str, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the planned scanning strategy."""
        scan_results = {
            'phases_completed': 0,
            'total_ports_scanned': 0,
            'open_ports_found': [],
            'services_identified': [],
            'errors': []
        }
        
        for i, phase in enumerate(strategy['phases']):
            self.logger.info(f"Executing phase {i+1}: {phase['name']}")
            
            try:
                # Execute the phase using the base scanner
                phase_result = self._execute_single_phase(target, phase)
                
                # Aggregate results
                if 'open_ports' in phase_result:
                    for port in phase_result['open_ports']:
                        if port not in scan_results['open_ports_found']:
                            scan_results['open_ports_found'].append(port)
                
                if 'services' in phase_result:
                    for service in phase_result['services']:
                        if service not in scan_results['services_identified']:
                            scan_results['services_identified'].append(service)
                
                scan_results['phases_completed'] += 1
                
                # Adaptive decision: should we continue?
                if self._should_stop_scanning(scan_results, phase_result):
                    self.logger.info("Adaptive scan stopping early - sufficient information gathered")
                    break
                
            except Exception as e:
                self.logger.error(f"Phase {phase['name']} failed: {e}")
                scan_results['errors'].append(f"Phase {phase['name']}: {e}")
        
        return scan_results
    
    def _execute_single_phase(self, target: str, phase: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single scanning phase."""
        ports = phase.get('ports', '1-1000')
        args = phase.get('args', '')
        timing = phase.get('timing', 'T3')
        
        # Build arguments
        scan_args = f"-{timing} {args}".strip()
        
        # Use the base scanner
        result = self.base_scanner.scan(
            targets=[target],
            ports=ports,
            arguments=scan_args,
            ai_optimize=False  # We're doing our own optimization
        )
        
        # Extract relevant information
        if target in result.get('results', {}):
            target_result = result['results'][target]
            if 'parsed' in target_result:
                return target_result['parsed']
        
        return {'error': 'No results from phase'}
    
    def _enhance_with_ai_analysis(
        self, 
        scan_results: Dict[str, Any], 
        intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance scan results with AI analysis."""
        enhanced = scan_results.copy()
        
        # AI confidence scoring
        confidence_factors = []
        
        if scan_results.get('phases_completed', 0) > 0:
            confidence_factors.append(0.3)
        
        if len(scan_results.get('open_ports_found', [])) > 0:
            confidence_factors.append(0.4)
        
        if len(scan_results.get('services_identified', [])) > 0:
            confidence_factors.append(0.3)
        
        enhanced['ai_confidence'] = sum(confidence_factors)
        
        # Generate AI recommendations
        recommendations = []
        
        open_ports = scan_results.get('open_ports_found', [])
        if 23 in [p.get('port') for p in open_ports if isinstance(p, dict)]:
            recommendations.append({
                'type': 'security',
                'severity': 'high',
                'message': 'Telnet service detected - consider using SSH instead'
            })
        
        if len(open_ports) > 10:
            recommendations.append({
                'type': 'security',
                'severity': 'medium',
                'message': 'Many open ports detected - review if all are necessary'
            })
        
        enhanced['recommendations'] = recommendations
        
        # Add AI insights
        enhanced['ai_insights'] = {
            'target_profile': self._generate_target_profile(scan_results, intelligence),
            'security_posture': self._assess_security_posture(scan_results),
            'further_testing': self._suggest_further_testing(scan_results)
        }
        
        return enhanced
    
    def _quick_ping(self, target: str) -> Dict[str, Any]:
        """Perform a quick ping test."""
        # Simplified ping implementation
        # In a real implementation, this would use actual ping
        return {
            'alive': True,  # Assume alive for demo
            'response_time': random.uniform(1, 50)  # Random response time
        }
    
    def _quick_port_check(self, target: str, ports: List[int]) -> List[int]:
        """Quick check of common ports."""
        # Simplified port check - in real implementation would use socket connections
        # Return some random ports as "open" for demo
        open_ports = random.sample(ports, random.randint(1, min(5, len(ports))))
        return open_ports
    
    def _resolve_hostname(self, target: str) -> Optional[Dict[str, Any]]:
        """Resolve hostname information."""
        # Simplified hostname resolution
        return {
            'hostname': f"host-{target.replace('.', '-')}.example.com",
            'resolved': True
        }
    
    def _should_stop_scanning(
        self, 
        current_results: Dict[str, Any], 
        phase_result: Dict[str, Any]
    ) -> bool:
        """Decide if scanning should stop early."""
        # Stop if we found enough information
        if len(current_results.get('open_ports_found', [])) >= 20:
            return True
        
        # Stop if last phase found nothing new
        if not phase_result.get('open_ports', []) and current_results['phases_completed'] > 2:
            return True
        
        return False
    
    def _generate_target_profile(
        self, 
        scan_results: Dict[str, Any], 
        intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate AI target profile."""
        services = scan_results.get('services_identified', [])
        
        profile = {
            'type': 'unknown',
            'confidence': 0.5,
            'characteristics': []
        }
        
        if 'http' in services or 'https' in services:
            profile['type'] = 'web_server'
            profile['confidence'] = 0.8
            profile['characteristics'].append('Web services detected')
        
        return profile
    
    def _assess_security_posture(self, scan_results: Dict[str, Any]) -> Dict[str, str]:
        """Assess security posture based on scan results."""
        open_ports_count = len(scan_results.get('open_ports_found', []))
        
        if open_ports_count > 15:
            return {'level': 'concerning', 'reason': 'Many open ports detected'}
        elif open_ports_count > 5:
            return {'level': 'moderate', 'reason': 'Several open ports detected'}
        else:
            return {'level': 'good', 'reason': 'Few open ports detected'}
    
    def _suggest_further_testing(self, scan_results: Dict[str, Any]) -> List[str]:
        """Suggest further testing based on results."""
        suggestions = []
        
        services = scan_results.get('services_identified', [])
        
        if 'http' in services or 'https' in services:
            suggestions.append('Consider web application security testing')
        
        if 'ssh' in services:
            suggestions.append('Consider SSH security assessment')
        
        return suggestions
    
    # Additional methods for adaptive scanning
    def _plan_adaptive_phase(
        self, 
        target: str, 
        current_knowledge: Dict[str, Any], 
        phase_num: int
    ) -> Dict[str, Any]:
        """Plan next phase of adaptive scanning."""
        return {
            'phase': phase_num,
            'ports': f"{phase_num * 1000}-{(phase_num + 1) * 1000 - 1}",
            'args': '-sV' if phase_num > 1 else '',
            'worth_continuing': phase_num <= 3
        }
    
    def _execute_scan_phase(self, target: str, phase_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single adaptive scanning phase."""
        return {
            'phase': phase_plan['phase'],
            'open_ports': [],
            'duration': random.uniform(30, 120)  # Simulated duration
        }
    
    def _update_knowledge_base(
        self, 
        current_knowledge: Dict[str, Any], 
        phase_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update knowledge base with new phase results."""
        updated = current_knowledge.copy()
        updated[f"phase_{phase_results['phase']}"] = phase_results
        return updated
    
    def _sufficient_information_gathered(self, knowledge: Dict[str, Any]) -> bool:
        """Check if sufficient information has been gathered."""
        return len(knowledge) >= 3  # Stop after 3 phases for demo
    
    def _generate_adaptive_insights(
        self, 
        phases: List[Dict[str, Any]], 
        knowledge: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate insights from adaptive scanning."""
        return {
            'total_phases': len(phases),
            'efficiency': 'high' if len(phases) <= 3 else 'moderate',
            'pattern': 'adaptive_successful'
        }
    
    def _update_learning_data(
        self, 
        target: str, 
        scan_results: Dict[str, Any], 
        enhanced_results: Dict[str, Any]
    ) -> None:
        """Update learning data for future scans."""
        learning_entry = {
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'results': scan_results,
            'ai_insights': enhanced_results.get('ai_insights', {}),
            'success_indicators': {
                'ports_found': len(scan_results.get('open_ports_found', [])),
                'services_identified': len(scan_results.get('services_identified', [])),
                'phases_completed': scan_results.get('phases_completed', 0)
            }
        }
        
        self.learning_data.append(learning_entry)
        
        # Keep only last 100 entries
        if len(self.learning_data) > 100:
            self.learning_data = self.learning_data[-100:]
