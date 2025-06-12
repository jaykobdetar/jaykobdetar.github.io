#!/usr/bin/env python3
"""
Advanced Security Analyzer for Influencer News CMS
==================================================
Provides comprehensive security analysis and enhanced XSS prevention
"""

import re
import html
import urllib.parse
import base64
import hashlib
from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum

from .logger import get_logger
from .sanitizer import ContentSanitizer, ValidationResult

logger = get_logger(__name__)

class ThreatLevel(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityThreat:
    """Represents a detected security threat"""
    threat_type: str
    threat_level: ThreatLevel
    description: str
    pattern: str
    location: str
    remediation: str

class AdvancedSecurityAnalyzer:
    """Advanced security analyzer with comprehensive XSS detection"""
    
    def __init__(self):
        self.base_sanitizer = ContentSanitizer()
        
        # Advanced XSS patterns
        self.xss_patterns = {
            # Script-based attacks
            'script_tags': [
                r'<script[^>]*>.*?</script>',
                r'<script[^>]*>',
                r'</script>',
            ],
            
            # Event handler attacks
            'event_handlers': [
                r'on\w+\s*=\s*["\']?[^"\'>\s]*["\']?',
                r'on(load|click|mouse|focus|blur|change|submit)\s*=',
                r'on(error|abort|resize|scroll|unload)\s*=',
            ],
            
            # JavaScript protocol attacks
            'javascript_protocols': [
                r'javascript\s*:',
                r'vbscript\s*:',
                r'livescript\s*:',
                r'mocha\s*:',
                r'data\s*:.*script',
            ],
            
            # Encoded attacks
            'encoded_attacks': [
                r'&#x?[0-9a-f]+;',  # HTML entities
                r'%[0-9a-f]{2}',    # URL encoding
                r'\\u[0-9a-f]{4}',  # Unicode escapes
                r'\\x[0-9a-f]{2}',  # Hex escapes
            ],
            
            # CSS-based attacks
            'css_attacks': [
                r'expression\s*\(',
                r'behavior\s*:',
                r'@import\s+',
                r'javascript\s*:.*url\s*\(',
                r'url\s*\(\s*["\']?javascript:',
            ],
            
            # SVG-based attacks
            'svg_attacks': [
                r'<svg[^>]*onload[^>]*>',
                r'<svg[^>]*>.*?<script',
                r'<animateTransform[^>]*onbegin',
            ],
            
            # Object/embed attacks
            'object_attacks': [
                r'<object[^>]*>',
                r'<embed[^>]*>',
                r'<applet[^>]*>',
                r'<iframe[^>]*>',
            ],
            
            # Form-based attacks
            'form_attacks': [
                r'<form[^>]*>',
                r'<input[^>]*>',
                r'<textarea[^>]*>',
                r'<select[^>]*>',
            ],
            
            # Meta/link attacks
            'meta_attacks': [
                r'<meta[^>]*http-equiv[^>]*refresh',
                r'<link[^>]*href[^>]*javascript:',
                r'<base[^>]*href',
            ],
            
            # Advanced polyglot attacks
            'polyglot_attacks': [
                r'jaVasCript:.*oNcliCk',
                r'/\*.*\*/.*alert\s*\(',
                r'<!--.*-->.*<script',
                r'</style.*<script',
            ],
            
            # Data exfiltration patterns
            'data_exfiltration': [
                r'new\s+Image\s*\(\s*\)',
                r'fetch\s*\(',
                r'XMLHttpRequest',
                r'\.send\s*\(',
                r'document\.cookie',
                r'localStorage\.',
                r'sessionStorage\.',
            ],
        }
        
        # Compile patterns for efficiency
        self.compiled_patterns = {}
        for category, patterns in self.xss_patterns.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE | re.DOTALL | re.MULTILINE)
                for pattern in patterns
            ]
        
        # Dangerous attribute patterns
        self.dangerous_attributes = {
            'event_attrs': re.compile(r'\bon\w+\s*=', re.IGNORECASE),
            'style_attrs': re.compile(r'\bstyle\s*=\s*["\'][^"\']*expression', re.IGNORECASE),
            'href_attrs': re.compile(r'\bhref\s*=\s*["\']?(javascript|vbscript|data):', re.IGNORECASE),
            'src_attrs': re.compile(r'\bsrc\s*=\s*["\']?(javascript|vbscript|data):', re.IGNORECASE),
        }
        
        # Content Security Policy recommendations
        self.csp_recommendations = {
            'script-src': "'self' 'unsafe-inline'",
            'style-src': "'self' 'unsafe-inline' fonts.googleapis.com",
            'img-src': "'self' data: https:",
            'font-src': "'self' fonts.gstatic.com",
            'connect-src': "'self'",
            'object-src': "'none'",
            'base-uri': "'self'",
            'frame-ancestors': "'none'",
        }
    
    def analyze_content_security(self, content: str, content_type: str = 'general') -> Dict[str, Any]:
        """
        Perform comprehensive security analysis of content
        
        Args:
            content: Content to analyze
            content_type: Type of content being analyzed
            
        Returns:
            Dictionary with security analysis results
        """
        analysis_results = {
            'threats_detected': [],
            'security_score': 100,
            'recommendations': [],
            'sanitized_content': content,
            'is_safe': True,
            'csp_violations': [],
        }
        
        try:
            # Detect XSS threats
            threats = self._detect_xss_threats(content)
            analysis_results['threats_detected'].extend(threats)
            
            # Calculate security score
            analysis_results['security_score'] = self._calculate_security_score(threats)
            
            # Generate recommendations
            analysis_results['recommendations'] = self._generate_security_recommendations(threats)
            
            # Enhanced sanitization
            sanitized = self._enhanced_sanitization(content, threats)
            analysis_results['sanitized_content'] = sanitized
            
            # Check if content is safe
            critical_threats = [t for t in threats if t.threat_level == ThreatLevel.CRITICAL]
            high_threats = [t for t in threats if t.threat_level == ThreatLevel.HIGH]
            analysis_results['is_safe'] = len(critical_threats) == 0 and len(high_threats) == 0
            
            # CSP analysis
            analysis_results['csp_violations'] = self._analyze_csp_violations(content)
            
            # Log security analysis
            if threats:
                threat_summary = ', '.join([f"{t.threat_type}({t.threat_level.value})" for t in threats])
                logger.warning(f"Security threats detected in {content_type} content: {threat_summary}")
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Security analysis failed: {e}")
            return {
                'threats_detected': [],
                'security_score': 0,
                'recommendations': ['Content analysis failed - manual review required'],
                'sanitized_content': '',
                'is_safe': False,
                'csp_violations': [],
                'error': str(e)
            }
    
    def _detect_xss_threats(self, content: str) -> List[SecurityThreat]:
        """Detect XSS threats in content"""
        threats = []
        
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                matches = pattern.finditer(content)
                for match in matches:
                    threat_level = self._assess_threat_level(category, match.group())
                    
                    threat = SecurityThreat(
                        threat_type=category,
                        threat_level=threat_level,
                        description=self._get_threat_description(category),
                        pattern=match.group()[:100],  # Limit pattern length
                        location=f"Position {match.start()}-{match.end()}",
                        remediation=self._get_remediation_advice(category)
                    )
                    threats.append(threat)
        
        return threats
    
    def _assess_threat_level(self, category: str, pattern: str) -> ThreatLevel:
        """Assess the threat level of a detected pattern"""
        critical_categories = ['script_tags', 'javascript_protocols', 'data_exfiltration']
        high_categories = ['event_handlers', 'object_attacks', 'svg_attacks']
        medium_categories = ['css_attacks', 'form_attacks', 'meta_attacks']
        
        if category in critical_categories:
            return ThreatLevel.CRITICAL
        elif category in high_categories:
            return ThreatLevel.HIGH
        elif category in medium_categories:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    def _get_threat_description(self, category: str) -> str:
        """Get description for threat category"""
        descriptions = {
            'script_tags': 'Script tags can execute arbitrary JavaScript code',
            'event_handlers': 'Event handlers can trigger malicious JavaScript',
            'javascript_protocols': 'JavaScript protocols can execute code in URLs',
            'encoded_attacks': 'Encoded content may bypass security filters',
            'css_attacks': 'CSS can be used to execute JavaScript or steal data',
            'svg_attacks': 'SVG elements can contain executable content',
            'object_attacks': 'Object/embed tags can load external malicious content',
            'form_attacks': 'Form elements can be used for data collection attacks',
            'meta_attacks': 'Meta tags can redirect users or modify page behavior',
            'polyglot_attacks': 'Sophisticated multi-vector attack patterns',
            'data_exfiltration': 'Code patterns that may steal user data',
        }
        return descriptions.get(category, 'Potentially dangerous content detected')
    
    def _get_remediation_advice(self, category: str) -> str:
        """Get remediation advice for threat category"""
        remediations = {
            'script_tags': 'Remove all script tags or encode them as text',
            'event_handlers': 'Remove event handler attributes from HTML elements',
            'javascript_protocols': 'Replace with safe HTTP/HTTPS URLs',
            'encoded_attacks': 'Decode and re-sanitize content',
            'css_attacks': 'Remove dangerous CSS properties and expressions',
            'svg_attacks': 'Remove SVG elements or sanitize their contents',
            'object_attacks': 'Remove object, embed, applet, and iframe elements',
            'form_attacks': 'Remove form elements or sanitize their attributes',
            'meta_attacks': 'Remove or sanitize meta and link tags',
            'polyglot_attacks': 'Apply comprehensive input sanitization',
            'data_exfiltration': 'Remove data access and network request code',
        }
        return remediations.get(category, 'Apply appropriate content filtering')
    
    def _calculate_security_score(self, threats: List[SecurityThreat]) -> int:
        """Calculate security score based on detected threats"""
        score = 100
        
        for threat in threats:
            if threat.threat_level == ThreatLevel.CRITICAL:
                score -= 40
            elif threat.threat_level == ThreatLevel.HIGH:
                score -= 25
            elif threat.threat_level == ThreatLevel.MEDIUM:
                score -= 15
            elif threat.threat_level == ThreatLevel.LOW:
                score -= 5
        
        return max(0, score)
    
    def _generate_security_recommendations(self, threats: List[SecurityThreat]) -> List[str]:
        """Generate security recommendations based on threats"""
        recommendations = []
        
        if not threats:
            recommendations.append("Content appears secure - no threats detected")
            return recommendations
        
        # Group threats by type
        threat_types = set(threat.threat_type for threat in threats)
        
        for threat_type in threat_types:
            threat_count = len([t for t in threats if t.threat_type == threat_type])
            recommendations.append(f"Address {threat_count} {threat_type.replace('_', ' ')} issues")
        
        # General recommendations
        if any(t.threat_level == ThreatLevel.CRITICAL for t in threats):
            recommendations.append("URGENT: Critical security threats detected - immediate action required")
        
        if any(t.threat_level == ThreatLevel.HIGH for t in threats):
            recommendations.append("High-priority security issues require prompt attention")
        
        recommendations.append("Implement Content Security Policy (CSP) headers")
        recommendations.append("Consider using a security-focused HTML sanitization library")
        recommendations.append("Regularly audit and test content sanitization")
        
        return recommendations
    
    def _enhanced_sanitization(self, content: str, threats: List[SecurityThreat]) -> str:
        """Apply enhanced sanitization based on detected threats"""
        sanitized_content = content
        
        # Apply base sanitization first
        base_result = self.base_sanitizer.sanitize_content(content)
        sanitized_content = base_result.cleaned_content
        
        # Apply additional sanitization for specific threats
        for threat in threats:
            if threat.threat_level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]:
                # Aggressive sanitization for high-risk content
                sanitized_content = self._aggressive_sanitization(sanitized_content, threat.threat_type)
        
        return sanitized_content
    
    def _aggressive_sanitization(self, content: str, threat_type: str) -> str:
        """Apply aggressive sanitization for high-risk content"""
        if threat_type == 'script_tags':
            # Remove all script-like content
            content = re.sub(r'</?script[^>]*>', '', content, flags=re.IGNORECASE)
            content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)
        
        elif threat_type == 'event_handlers':
            # Remove all event handlers
            content = re.sub(r'\bon\w+\s*=\s*[^>\s]*', '', content, flags=re.IGNORECASE)
        
        elif threat_type == 'object_attacks':
            # Remove object-like elements
            dangerous_tags = ['object', 'embed', 'applet', 'iframe', 'frame']
            for tag in dangerous_tags:
                content = re.sub(f'</?{tag}[^>]*>', '', content, flags=re.IGNORECASE)
        
        return content
    
    def _analyze_csp_violations(self, content: str) -> List[str]:
        """Analyze potential CSP violations"""
        violations = []
        
        # Check for inline scripts
        if re.search(r'<script[^>]*>', content, re.IGNORECASE):
            violations.append("Inline scripts violate script-src 'self' policy")
        
        # Check for inline styles
        if re.search(r'\bstyle\s*=', content, re.IGNORECASE):
            violations.append("Inline styles may violate style-src policy")
        
        # Check for data URLs
        if re.search(r'data:', content, re.IGNORECASE):
            violations.append("Data URLs may violate img-src policy")
        
        # Check for external resources
        if re.search(r'src\s*=\s*["\']?https?://', content, re.IGNORECASE):
            violations.append("External resources may violate connect-src policy")
        
        return violations
    
    def generate_security_report(self, content: str, content_type: str = 'general') -> str:
        """Generate a comprehensive security report"""
        analysis = self.analyze_content_security(content, content_type)
        
        report = f"""
SECURITY ANALYSIS REPORT
========================
Content Type: {content_type.title()}
Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SECURITY SCORE: {analysis['security_score']}/100

THREAT SUMMARY:
"""
        
        if analysis['threats_detected']:
            for threat in analysis['threats_detected']:
                report += f"""
- {threat.threat_type.replace('_', ' ').title()}: {threat.threat_level.value.upper()}
  Description: {threat.description}
  Location: {threat.location}
  Remediation: {threat.remediation}
"""
        else:
            report += "\nNo security threats detected."
        
        if analysis['csp_violations']:
            report += "\nCSP VIOLATIONS:\n"
            for violation in analysis['csp_violations']:
                report += f"- {violation}\n"
        
        report += "\nRECOMMENDATIONS:\n"
        for rec in analysis['recommendations']:
            report += f"- {rec}\n"
        
        return report

# Global security analyzer instance
security_analyzer = AdvancedSecurityAnalyzer()