"""
AI-powered script generator for NMAP-AI
"""

import re
import json
import random
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..utils.logger import get_logger


class AIScriptGenerator:
    """
    AI-powered Nmap script generator.
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.script_templates = self._load_script_templates()
        self.vulnerability_patterns = self._load_vulnerability_patterns()
    
    def create_script(
        self,
        target_type: str = "general",
        vulnerabilities: Optional[List[str]] = None,
        stealth_level: str = "medium",
        custom_requirements: Optional[List[str]] = None
    ) -> str:
        """
        Generate a custom Nmap script using AI.
        
        Args:
            target_type: Type of target (web_server, network_device, database, etc.)
            vulnerabilities: List of vulnerabilities to check for
            stealth_level: Stealth level (low, medium, high)
            custom_requirements: Additional custom requirements
        
        Returns:
            Generated Nmap script content
        """
        self.logger.info(f"Generating AI script for {target_type} with stealth level {stealth_level}")
        
        # Select appropriate template based on target type
        template = self._select_template(target_type)
        
        # Generate script components
        script_components = {
            'description': self._generate_description(target_type, vulnerabilities),
            'categories': self._generate_categories(target_type, vulnerabilities),
            'dependencies': self._generate_dependencies(target_type, vulnerabilities),
            'author': 'NMAP-AI Script Generator',
            'license': 'MIT',
            'portrule': self._generate_portrule(target_type),
            'action_function': self._generate_action_function(target_type, vulnerabilities, stealth_level)
        }
        
        # Compile final script
        final_script = self._compile_script(template, script_components)
        
        return final_script
    
    def _load_script_templates(self) -> Dict[str, str]:
        """Load Nmap script templates."""
        return {
            'web_server': '''
description = [[{description}]]

---
-- @usage nmap --script {script_name} <target>
-- @output
-- PORT   STATE SERVICE
-- 80/tcp open  http
-- | {script_name}:
-- |   {output_description}
---

author = "{author}"
license = "{license}"
categories = {{{categories}}}

{dependencies}

{portrule}

{action_function}
''',
            'network_device': '''
description = [[{description}]]

---
-- @usage nmap --script {script_name} <target>
-- @args {script_name}.timeout Script timeout in seconds (default: 30)
---

author = "{author}"
license = "{license}"
categories = {{{categories}}}

{dependencies}

{portrule}

{action_function}
''',
            'database': '''
description = [[{description}]]

---
-- @usage nmap --script {script_name} <target>
-- @args {script_name}.database Database name to test (default: tries common names)
---

author = "{author}"
license = "{license}"
categories = {{{categories}}}

{dependencies}

{portrule}

{action_function}
''',
            'general': '''
description = [[{description}]]

author = "{author}"
license = "{license}"
categories = {{{categories}}}

{dependencies}

{portrule}

{action_function}
'''
        }
    
    def _load_vulnerability_patterns(self) -> Dict[str, Dict]:
        """Load vulnerability detection patterns."""
        return {
            'sql_injection': {
                'payloads': ["' OR '1'='1", "'; DROP TABLE users--", "1' UNION SELECT NULL--"],
                'indicators': ['SQL syntax error', 'mysql_fetch', 'ORA-', 'PostgreSQL query failed'],
                'ports': [1433, 3306, 5432, 1521]
            },
            'xss': {
                'payloads': ['<script>alert("XSS")</script>', '<img src="x" onerror="alert(1)">'],
                'indicators': ['<script>', 'onerror=', 'javascript:'],
                'ports': [80, 443, 8080, 8443]
            },
            'directory_traversal': {
                'payloads': ['../../../etc/passwd', '..\\..\\..\\windows\\system32\\drivers\\etc\\hosts'],
                'indicators': ['root:', 'daemon:', '[boot loader]'],
                'ports': [80, 443, 21, 22]
            },
            'rce': {
                'payloads': ['|id', ';whoami', '`uname -a`'],
                'indicators': ['uid=', 'gid=', 'Linux', 'Windows'],
                'ports': [80, 443, 22, 23]
            },
            'weak_authentication': {
                'credentials': [('admin', 'admin'), ('root', ''), ('admin', 'password')],
                'indicators': ['Authentication successful', 'Login successful'],
                'ports': [22, 23, 21, 3389]
            }
        }
    
    def _select_template(self, target_type: str) -> str:
        """Select appropriate script template."""
        return self.script_templates.get(target_type, self.script_templates['general'])
    
    def _generate_description(self, target_type: str, vulnerabilities: Optional[List[str]]) -> str:
        """Generate script description."""
        base_descriptions = {
            'web_server': 'Performs comprehensive security testing on web servers',
            'network_device': 'Tests network devices for common vulnerabilities and misconfigurations',
            'database': 'Scans database services for security issues and weak configurations',
            'general': 'Performs general security scanning and vulnerability detection'
        }
        
        base_desc = base_descriptions.get(target_type, base_descriptions['general'])
        
        if vulnerabilities:
            vuln_desc = ', '.join(vulnerabilities)
            return f"{base_desc}, specifically testing for: {vuln_desc}"
        
        return base_desc
    
    def _generate_categories(self, target_type: str, vulnerabilities: Optional[List[str]]) -> str:
        """Generate script categories."""
        categories = ['discovery', 'safe']
        
        if vulnerabilities:
            if any(v in ['sql_injection', 'xss', 'rce'] for v in vulnerabilities):
                categories.append('intrusive')
            if any(v in ['weak_authentication', 'default_credentials'] for v in vulnerabilities):
                categories.append('auth')
            if 'web' in target_type.lower():
                categories.append('http')
        
        return ', '.join([f'"{cat}"' for cat in categories])
    
    def _generate_dependencies(self, target_type: str, vulnerabilities: Optional[List[str]]) -> str:
        """Generate script dependencies."""
        deps = ['stdnse', 'shortport']
        
        if 'web' in target_type.lower() or (vulnerabilities and any('web' in str(v) for v in vulnerabilities)):
            deps.extend(['http', 'httpspider'])
        
        if vulnerabilities and 'sql_injection' in vulnerabilities:
            deps.append('sql')
        
        return '\n'.join([f'local {dep} = require "{dep}"' for dep in deps])
    
    def _generate_portrule(self, target_type: str) -> str:
        """Generate port rule for the script."""
        if 'web' in target_type.lower():
            return 'portrule = shortport.http'
        elif 'database' in target_type.lower():
            return 'portrule = shortport.port_or_service({1433, 3306, 5432, 1521}, {"mssql", "mysql", "postgresql", "oracle"})'
        elif 'ssh' in target_type.lower():
            return 'portrule = shortport.port_or_service(22, "ssh")'
        else:
            return 'portrule = function(host, port) return port.state == "open" end'
    
    def _generate_action_function(
        self, 
        target_type: str, 
        vulnerabilities: Optional[List[str]], 
        stealth_level: str
    ) -> str:
        """Generate the main action function."""
        
        # Base function structure
        function_start = '''action = function(host, port)
    local results = {}
    local target = host.ip
    local port_number = port.number
    
    stdnse.debug1("Starting scan on %s:%s", target, port_number)
'''
        
        # Generate vulnerability-specific checks
        vuln_checks = self._generate_vulnerability_checks(vulnerabilities, stealth_level)
        
        # Generate timing controls based on stealth level
        timing_controls = self._generate_timing_controls(stealth_level)
        
        function_end = '''
    if #results > 0 then
        return stdnse.format_output(true, results)
    else
        return "No vulnerabilities detected"
    end
end'''
        
        return function_start + timing_controls + vuln_checks + function_end
    
    def _generate_vulnerability_checks(self, vulnerabilities: Optional[List[str]], stealth_level: str) -> str:
        """Generate vulnerability-specific check code."""
        if not vulnerabilities:
            return '''
    -- Basic service detection
    table.insert(results, "Service: " .. (port.service or "unknown"))
    table.insert(results, "Version: " .. (port.version.version or "unknown"))
'''
        
        checks = []
        for vuln in vulnerabilities:
            if vuln in self.vulnerability_patterns:
                pattern = self.vulnerability_patterns[vuln]
                check_code = self._generate_vuln_check_code(vuln, pattern, stealth_level)
                checks.append(check_code)
        
        return '\n'.join(checks)
    
    def _generate_vuln_check_code(self, vuln: str, pattern: Dict, stealth_level: str) -> str:
        """Generate specific vulnerability check code."""
        if vuln == 'sql_injection':
            return '''
    -- SQL Injection Test
    local sql_payloads = {"' OR '1'='1", "'; DROP TABLE test--"}
    for _, payload in ipairs(sql_payloads) do
        -- Test payload (implementation depends on service)
        stdnse.debug2("Testing SQL injection with: %s", payload)
        -- Add actual test logic here
    end
'''
        elif vuln == 'xss':
            return '''
    -- Cross-Site Scripting Test
    local xss_payloads = {'<script>alert("XSS")</script>', '<img src="x" onerror="alert(1)">'}
    for _, payload in ipairs(xss_payloads) do
        stdnse.debug2("Testing XSS with: %s", payload)
        -- Add actual test logic here
    end
'''
        elif vuln == 'weak_authentication':
            return '''
    -- Weak Authentication Test
    local common_creds = {{"admin", "admin"}, {"root", ""}, {"admin", "password"}}
    for _, cred in ipairs(common_creds) do
        stdnse.debug2("Testing credentials: %s/%s", cred[1], cred[2])
        -- Add actual authentication test logic here
    end
'''
        else:
            return f'''
    -- {vuln.replace('_', ' ').title()} Test
    stdnse.debug2("Testing for {vuln}")
    -- Add {vuln} test logic here
'''
    
    def _generate_timing_controls(self, stealth_level: str) -> str:
        """Generate timing controls based on stealth level."""
        if stealth_level == 'high':
            return '''
    -- High stealth mode - add delays
    local delay = math.random(1, 3)
    stdnse.sleep(delay)
'''
        elif stealth_level == 'medium':
            return '''
    -- Medium stealth mode - moderate delays
    local delay = math.random(0.5, 1.5)
    stdnse.sleep(delay)
'''
        else:  # low stealth
            return '''
    -- Low stealth mode - minimal delays
    stdnse.sleep(0.1)
'''
    
    def _compile_script(self, template: str, components: Dict[str, str]) -> str:
        """Compile the final script from template and components."""
        script_name = f"ai_generated_{int(datetime.now().timestamp())}"
        
        # Replace placeholders in template
        compiled_script = template.format(
            script_name=script_name,
            output_description="AI-generated security scan results",
            **components
        )
        
        return compiled_script
    
    def generate_targeted_script(
        self,
        target_info: Dict[str, Any],
        scan_results: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a targeted script based on target information and previous scan results.
        """
        target_type = target_info.get('type', 'general')
        detected_services = []
        
        if scan_results:
            # Analyze previous scan results to determine services
            detected_services = self._analyze_services(scan_results)
        
        # Generate script based on detected services
        if 'http' in detected_services or 'https' in detected_services:
            return self.create_script(
                target_type='web_server',
                vulnerabilities=['xss', 'sql_injection', 'directory_traversal'],
                stealth_level=target_info.get('stealth_level', 'medium')
            )
        elif 'ssh' in detected_services:
            return self.create_script(
                target_type='network_device',
                vulnerabilities=['weak_authentication'],
                stealth_level=target_info.get('stealth_level', 'medium')
            )
        elif any(db in detected_services for db in ['mysql', 'postgresql', 'mssql']):
            return self.create_script(
                target_type='database',
                vulnerabilities=['sql_injection', 'weak_authentication'],
                stealth_level=target_info.get('stealth_level', 'medium')
            )
        else:
            return self.create_script(
                target_type='general',
                stealth_level=target_info.get('stealth_level', 'medium')
            )
    
    def _analyze_services(self, scan_results: Dict[str, Any]) -> List[str]:
        """Analyze scan results to extract detected services."""
        services = []
        
        # Extract services from scan results
        if 'results' in scan_results:
            for target_results in scan_results['results'].values():
                if 'parsed' in target_results and 'services' in target_results['parsed']:
                    services.extend(target_results['parsed']['services'])
        
        return list(set(services))  # Remove duplicates
