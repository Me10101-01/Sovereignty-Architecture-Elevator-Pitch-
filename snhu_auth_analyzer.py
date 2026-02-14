#!/usr/bin/env python3
"""
LEGION Web Authentication Intelligence Analysis
Browser Fingerprinting and Session State Analysis Framework
"""

import requests
import json
import re
from urllib.parse import urlparse, parse_qs
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import base64
import hashlib

@dataclass
class BrowserSession:
    browser_type: str
    privacy_mode: bool
    cookies_enabled: bool
    session_data: Dict
    headers: Dict
    fingerprint_resistance: float

@dataclass
class AuthFlowAnalysis:
    url: str
    redirect_chain: List[str]
    session_tracking: List[str]
    authentication_method: str
    privacy_leakage: Dict
    tracking_mechanisms: List[str]

class SNHUAuthAnalyzer:
    """Analyze SNHU authentication flow differences between browser modes"""
    
    def __init__(self):
        self.target_url = "https://unify-snhu.my.site.com/mysnhu/s/"
        self.auth_patterns = {
            'sso_redirect': r'services/auth/sso/([^?]+)',
            'csrf_token': r'csrfToken["\']?\s*[:=]\s*["\']([^"\']+)',
            'session_id': r'session[_-]?id["\']?\s*[:=]\s*["\']([^"\']+)',
            'strivacity': r'Strivacity([^"\'&?]+)',
            'salesforce': r'SfdcApp|projectOneNavigator',
            'starturl': r'startURL=([^&]+)'
        }
        
        self.tracking_indicators = [
            'PreferenceBits',
            'csrfToken',
            'SfdcApp',
            'projectOneNavigator',
            'window.location',
            'bodyOnLoad',
            'bodyOnBeforeUnload'
        ]
    
    def analyze_html_response(self, html_content: str) -> AuthFlowAnalysis:
        """Analyze HTML response for authentication patterns"""
        
        # Extract redirect URLs
        redirect_chain = []
        redirect_matches = re.findall(r'location\.(replace|href)\s*=\s*["\']([^"\']+)', html_content)
        for method, url in redirect_matches:
            redirect_chain.append(f"{method}: {url}")
        
        # Find authentication method
        auth_method = "unknown"
        if "StrivacityMySNHUOIDC" in html_content:
            auth_method = "OIDC_SSO_Strivacity"
        elif "SfdcApp" in html_content:
            auth_method = "Salesforce_Community"
        
        # Identify tracking mechanisms
        tracking_mechanisms = []
        for indicator in self.tracking_indicators:
            if indicator in html_content:
                tracking_mechanisms.append(indicator)
        
        # Extract session tracking elements
        session_tracking = []
        for pattern_name, pattern in self.auth_patterns.items():
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                session_tracking.append(f"{pattern_name}: {matches}")
        
        # Analyze privacy leakage
        privacy_leakage = {
            'javascript_redirects': len(re.findall(r'window\.location', html_content)),
            'csrf_tokens': len(re.findall(r'csrfToken', html_content)),
            'session_handlers': len(re.findall(r'bodyOn\w+', html_content)),
            'tracking_scripts': len(re.findall(r'<script', html_content)),
            'meta_no_cache': 'PRAGMA.*NO-CACHE' in html_content
        }
        
        return AuthFlowAnalysis(
            url=self.target_url,
            redirect_chain=redirect_chain,
            session_tracking=session_tracking,
            authentication_method=auth_method,
            privacy_leakage=privacy_leakage,
            tracking_mechanisms=tracking_mechanisms
        )
    
    def simulate_browser_requests(self) -> Dict[str, AuthFlowAnalysis]:
        """Simulate different browser configurations"""
        
        results = {}
        
        # Normal Firefox headers (with tracking)
        normal_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '0',  # Do Not Track disabled
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        # Private Firefox headers (enhanced privacy)
        private_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',  # Do Not Track enabled
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache'
        }
        
        return {
            'normal_firefox': normal_headers,
            'private_firefox': private_headers
        }
    
    def analyze_differences(self, normal_response: str, private_response: str) -> Dict:
        """Analyze key differences between browser modes"""
        
        normal_analysis = self.analyze_html_response(normal_response)
        private_analysis = self.analyze_html_response(private_response)
        
        differences = {
            'redirect_differences': {
                'normal': normal_analysis.redirect_chain,
                'private': private_analysis.redirect_chain,
                'different': normal_analysis.redirect_chain != private_analysis.redirect_chain
            },
            'tracking_differences': {
                'normal': normal_analysis.tracking_mechanisms,
                'private': private_analysis.tracking_mechanisms,
                'additional_tracking_normal': list(set(normal_analysis.tracking_mechanisms) - set(private_analysis.tracking_mechanisms)),
                'blocked_in_private': list(set(normal_analysis.tracking_mechanisms) - set(private_analysis.tracking_mechanisms))
            },
            'privacy_leakage_comparison': {
                'normal': normal_analysis.privacy_leakage,
                'private': private_analysis.privacy_leakage,
                'privacy_improvement': {}
            },
            'session_tracking_differences': {
                'normal': normal_analysis.session_tracking,
                'private': private_analysis.session_tracking,
                'session_persistence_blocked': len(normal_analysis.session_tracking) > len(private_analysis.session_tracking)
            }
        }
        
        # Calculate privacy improvements
        for key in normal_analysis.privacy_leakage:
            normal_val = normal_analysis.privacy_leakage[key]
            private_val = private_analysis.privacy_leakage[key]
            if isinstance(normal_val, (int, float)) and isinstance(private_val, (int, float)):
                differences['privacy_leakage_comparison']['privacy_improvement'][key] = normal_val - private_val
        
        return differences
    
    def generate_curl_commands(self) -> List[str]:
        """Generate curl commands to test different scenarios"""
        
        base_url = self.target_url
        
        commands = [
            # Normal browser simulation
            f'curl -L -s -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0" -H "DNT: 0" "{base_url}"',
            
            # Private browser simulation  
            f'curl -L -s -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0" -H "DNT: 1" -H "Cache-Control: no-cache" "{base_url}"',
            
            # Minimal headers (stealth mode)
            f'curl -L -s -H "User-Agent: curl/7.68.0" "{base_url}"',
            
            # Mobile browser simulation
            f'curl -L -s -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1" "{base_url}"',
            
            # Tor browser simulation
            f'curl -L -s -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0" -H "Accept-Language: en-US,en;q=0.5" "{base_url}"'
        ]
        
        return commands

def main():
    """Execute SNHU browser fingerprinting analysis"""
    
    print("🕵️ LEGION SNHU AUTHENTICATION FLOW ANALYSIS")
    print("=" * 60)
    
    analyzer = SNHUAuthAnalyzer()
    
    # Analyze the provided HTML response
    snhu_response = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
    <meta HTTP-EQUIV="PRAGMA" CONTENT="NO-CACHE">
<script>
function redirectOnLoad() {
if (this.SfdcApp && this.SfdcApp.projectOneNavigator) { SfdcApp.projectOneNavigator.handleRedirect('https://unify-snhu.my.site.com/mysnhu/services/auth/sso/StrivacityMySNHUOIDC?startURL=%2Fmysnhu%2Fs%2F'); }  else
if (window.location.replace){
window.location.replace('https://unify-snhu.my.site.com/mysnhu/services/auth/sso/StrivacityMySNHUOIDC?startURL=%2Fmysnhu%2Fs%2F');
} else {
window.location.href ='https://unify-snhu.my.site.com/mysnhu/services/auth/sso/StrivacityMySNHUOIDC?startURL=%2Fmysnhu%2Fs%2F';
}
}
redirectOnLoad();
</script>
</head>
</html>
<script type="text/javascript">function bodyOnLoad(){if(window.PreferenceBits){window.PreferenceBits.prototype.csrfToken="null";};}function bodyOnBeforeUnload(){}function bodyOnFocus(){}function bodyOnUnload(){}</script>
</body>
</html>'''
    
    analysis = analyzer.analyze_html_response(snhu_response)
    
    print(f"\n🔍 SNHU Authentication Flow Analysis:")
    print(f"Target URL: {analysis.url}")
    print(f"Authentication Method: {analysis.authentication_method}")
    
    print(f"\n📍 Redirect Chain:")
    for redirect in analysis.redirect_chain:
        print(f"  • {redirect}")
    
    print(f"\n🎯 Tracking Mechanisms Detected:")
    for mechanism in analysis.tracking_mechanisms:
        print(f"  • {mechanism}")
    
    print(f"\n🔒 Session Tracking Elements:")
    for element in analysis.session_tracking:
        print(f"  • {element}")
    
    print(f"\n🛡️ Privacy Leakage Analysis:")
    for key, value in analysis.privacy_leakage.items():
        print(f"  • {key}: {value}")
    
    print(f"\n🧬 Browser Behavior Differences:")
    print(f"🔍 Why Firefox Private vs Normal Shows Different Responses:")
    print(f"")
    print(f"1. 🍪 COOKIE HANDLING:")
    print(f"   • Normal Firefox: Accepts/stores cookies from previous sessions")
    print(f"   • Private Firefox: Blocks persistent cookies, no session history")
    print(f"   • Impact: Different authentication state detection")
    print(f"")
    print(f"2. 🔐 SESSION PERSISTENCE:")
    print(f"   • Normal Firefox: May have cached authentication tokens")
    print(f"   • Private Firefox: Fresh session, no stored credentials")
    print(f"   • Impact: Forces full authentication flow")
    print(f"")
    print(f"3. 📊 TRACKING PROTECTION:")
    print(f"   • Normal Firefox: Standard tracking protection")
    print(f"   • Private Firefox: Enhanced tracking protection enabled")
    print(f"   • Impact: Blocks some analytics/tracking scripts")
    print(f"")
    print(f"4. 🌐 REFERRER POLICY:")
    print(f"   • Normal Firefox: Sends referrer information")
    print(f"   • Private Firefox: Restricted referrer policy")
    print(f"   • Impact: Server may behave differently based on referrer")
    print(f"")
    print(f"5. 🛠️ JAVASCRIPT EXECUTION:")
    print(f"   • Both execute JavaScript, but private mode may:")
    print(f"     - Block certain tracking APIs")
    print(f"     - Limit localStorage/sessionStorage")
    print(f"     - Modify navigator properties")
    
    print(f"\n🔧 Curl Testing Commands:")
    commands = analyzer.generate_curl_commands()
    for i, cmd in enumerate(commands, 1):
        print(f"  {i}. {cmd}")
    
    print(f"\n🏆 ANALYSIS COMPLETE")
    print(f"Key Finding: SNHU portal uses Salesforce Community + Strivacity OIDC SSO")
    print(f"Browser differences likely due to session state and tracking protection")
    
    return analysis

if __name__ == "__main__":
    main()