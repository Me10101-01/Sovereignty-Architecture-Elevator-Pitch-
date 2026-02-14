#!/usr/bin/env python3
"""
🕵️ X.COM INTELLIGENCE PARSER v1.0
Advanced Web Application Source Code Analysis & API Intelligence System
Extracts authentication patterns, API endpoints, feature flags, and user metadata
"""

import re
import json
import base64
import hashlib
import time
import requests
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urljoin
import html
import gzip
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import fake_useragent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import threading
import queue

@dataclass
class APIEndpoint:
    url: str
    method: str
    endpoint_type: str
    authentication_required: bool
    parameters: List[str]
    response_format: str
    rate_limit: Optional[str] = None
    documentation: Optional[str] = None

@dataclass
class AuthenticationPattern:
    token_type: str
    token_value: str
    expiry: Optional[datetime] = None
    scope: Optional[str] = None
    extraction_method: str = "regex"

@dataclass
class FeatureFlag:
    name: str
    enabled: bool
    rollout_percentage: Optional[float] = None
    target_audience: Optional[str] = None
    description: Optional[str] = None

@dataclass
class UserMetadata:
    user_id: Optional[str] = None
    guest_id: Optional[str] = None
    session_id: Optional[str] = None
    country: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    client_info: Optional[Dict] = None

@dataclass
class IntelligenceReport:
    timestamp: datetime
    target_url: str
    api_endpoints: List[APIEndpoint]
    auth_patterns: List[AuthenticationPattern]
    feature_flags: List[FeatureFlag]
    user_metadata: UserMetadata
    security_headers: Dict[str, str]
    performance_metrics: Dict[str, Any]
    source_code_hash: str

class XComIntelligenceParser:
    def __init__(self):
        self.user_agent_rotator = fake_useragent.UserAgent()
        self.session = requests.Session()
        self.selenium_driver = None
        self.intelligence_cache = {}
        self.api_patterns = self._compile_api_patterns()
        self.auth_patterns = self._compile_auth_patterns()
        self.feature_flag_patterns = self._compile_feature_flag_patterns()
        
    def _compile_api_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for API endpoint detection"""
        patterns = {
            'graphql': re.compile(r'https?://[^"\']*\.twitter\.com[^"\']*/graphql/[^"\']*', re.IGNORECASE),
            'api_v1': re.compile(r'https?://[^"\']*\.twitter\.com[^"\']*/1\.1/[^"\']*', re.IGNORECASE),
            'api_v2': re.compile(r'https?://[^"\']*\.twitter\.com[^"\']*/2/[^"\']*', re.IGNORECASE),
            'internal': re.compile(r'https?://[^"\']*\.twitter\.com[^"\']*/i/api/[^"\']*', re.IGNORECASE),
            'media': re.compile(r'https?://[^"\']*\.twimg\.com[^"\']*', re.IGNORECASE),
            'websocket': re.compile(r'wss?://[^"\']*\.twitter\.com[^"\']*', re.IGNORECASE),
            'streaming': re.compile(r'https?://[^"\']*stream[^"\']*\.twitter\.com[^"\']*', re.IGNORECASE)
        }
        return patterns
    
    def _compile_auth_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for authentication token detection"""
        patterns = {
            'csrf_token': re.compile(r'["\']csrf[_-]?token["\']:\s*["\']([^"\']+)["\']', re.IGNORECASE),
            'auth_token': re.compile(r'["\']auth[_-]?token["\']:\s*["\']([^"\']+)["\']', re.IGNORECASE),
            'bearer_token': re.compile(r'bearer[\s:]+([A-Za-z0-9\-_]+)', re.IGNORECASE),
            'session_token': re.compile(r'["\']session[_-]?token["\']:\s*["\']([^"\']+)["\']', re.IGNORECASE),
            'guest_token': re.compile(r'["\']guest[_-]?token["\']:\s*["\']([^"\']+)["\']', re.IGNORECASE),
            'api_key': re.compile(r'["\']api[_-]?key["\']:\s*["\']([^"\']+)["\']', re.IGNORECASE),
            'oauth_token': re.compile(r'oauth[_-]?token[=:]\s*["\']?([^"\'&\s]+)', re.IGNORECASE),
            'x_auth_token': re.compile(r'x-auth-token["\']?\s*[:=]\s*["\']?([^"\'&\s]+)', re.IGNORECASE)
        }
        return patterns
    
    def _compile_feature_flag_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for feature flag detection"""
        patterns = {
            'feature_switches': re.compile(r'["\']featureSwitch["\']:\s*{[^}]*}', re.IGNORECASE | re.DOTALL),
            'ab_tests': re.compile(r'["\']abTest["\']:\s*{[^}]*}', re.IGNORECASE | re.DOTALL),
            'experiments': re.compile(r'["\']experiment["\']:\s*{[^}]*}', re.IGNORECASE | re.DOTALL),
            'rollouts': re.compile(r'["\']rollout["\']:\s*{[^}]*}', re.IGNORECASE | re.DOTALL),
            'config_flags': re.compile(r'["\']config["\']:\s*{[^}]*["\']enabled["\'][^}]*}', re.IGNORECASE | re.DOTALL)
        }
        return patterns
    
    def setup_selenium(self, headless: bool = True) -> bool:
        """Setup Selenium WebDriver for dynamic content extraction"""
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument(f'--user-agent={self.user_agent_rotator.random}')
            
            self.selenium_driver = webdriver.Chrome(options=chrome_options)
            return True
        except Exception as e:
            print(f"Selenium setup failed: {e}")
            return False
    
    def parse_html_source(self, html_source: str, source_url: str = "unknown") -> IntelligenceReport:
        """Parse HTML source code for comprehensive intelligence"""
        start_time = time.time()
        
        # Calculate source code hash
        source_hash = hashlib.sha256(html_source.encode()).hexdigest()
        
        # Extract API endpoints
        api_endpoints = self._extract_api_endpoints(html_source)
        
        # Extract authentication patterns
        auth_patterns = self._extract_auth_patterns(html_source)
        
        # Extract feature flags
        feature_flags = self._extract_feature_flags(html_source)
        
        # Extract user metadata
        user_metadata = self._extract_user_metadata(html_source)
        
        # Extract security headers (from meta tags and scripts)
        security_headers = self._extract_security_headers(html_source)
        
        # Performance metrics
        performance_metrics = {
            'parsing_time': time.time() - start_time,
            'source_size': len(html_source),
            'api_endpoints_found': len(api_endpoints),
            'auth_tokens_found': len(auth_patterns),
            'feature_flags_found': len(feature_flags)
        }
        
        report = IntelligenceReport(
            timestamp=datetime.now(),
            target_url=source_url,
            api_endpoints=api_endpoints,
            auth_patterns=auth_patterns,
            feature_flags=feature_flags,
            user_metadata=user_metadata,
            security_headers=security_headers,
            performance_metrics=performance_metrics,
            source_code_hash=source_hash
        )
        
        # Cache the report
        self.intelligence_cache[source_hash] = report
        
        return report
    
    def _extract_api_endpoints(self, html_source: str) -> List[APIEndpoint]:
        """Extract API endpoints from HTML source"""
        endpoints = []
        found_urls = set()
        
        for endpoint_type, pattern in self.api_patterns.items():
            matches = pattern.findall(html_source)
            
            for url in matches:
                if url not in found_urls:
                    found_urls.add(url)
                    
                    # Analyze endpoint
                    parsed_url = urlparse(url)
                    
                    # Determine HTTP method (basic heuristic)
                    method = "GET"
                    if any(keyword in url.lower() for keyword in ['post', 'create', 'update', 'delete']):
                        method = "POST"
                    
                    # Check if authentication is required
                    auth_required = any(keyword in url.lower() for keyword in ['auth', 'login', 'token', 'secure'])
                    
                    # Extract parameters from URL
                    parameters = list(parse_qs(parsed_url.query).keys()) if parsed_url.query else []
                    
                    # Determine response format
                    response_format = "JSON"
                    if any(ext in url.lower() for ext in ['.xml', '.rss']):
                        response_format = "XML"
                    elif any(ext in url.lower() for ext in ['.jpg', '.png', '.gif', '.webp']):
                        response_format = "IMAGE"
                    
                    endpoint = APIEndpoint(
                        url=url,
                        method=method,
                        endpoint_type=endpoint_type,
                        authentication_required=auth_required,
                        parameters=parameters,
                        response_format=response_format
                    )
                    endpoints.append(endpoint)
        
        return endpoints
    
    def _extract_auth_patterns(self, html_source: str) -> List[AuthenticationPattern]:
        """Extract authentication tokens and patterns"""
        auth_patterns = []
        
        for token_type, pattern in self.auth_patterns.items():
            matches = pattern.findall(html_source)
            
            for token_value in matches:
                # Skip obviously fake or placeholder tokens
                if len(token_value) < 8 or token_value.lower() in ['test', 'example', 'placeholder']:
                    continue
                
                auth_pattern = AuthenticationPattern(
                    token_type=token_type,
                    token_value=token_value[:50] + "..." if len(token_value) > 50 else token_value,
                    extraction_method="regex"
                )
                auth_patterns.append(auth_pattern)
        
        return auth_patterns
    
    def _extract_feature_flags(self, html_source: str) -> List[FeatureFlag]:
        """Extract feature flags and A/B test configurations"""
        feature_flags = []
        
        # Look for __INITIAL_STATE__ or similar configuration objects
        initial_state_pattern = re.compile(r'__INITIAL_STATE__\s*=\s*({.*?});', re.DOTALL)
        config_pattern = re.compile(r'window\.[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*({.*?});', re.DOTALL)
        
        for pattern in [initial_state_pattern, config_pattern]:
            matches = pattern.findall(html_source)
            
            for match in matches:
                try:
                    # Try to extract feature flags from the configuration
                    feature_flags.extend(self._parse_config_for_flags(match))
                except:
                    continue
        
        # Look for specific feature flag patterns
        for flag_type, pattern in self.feature_flag_patterns.items():
            matches = pattern.findall(html_source)
            
            for match in matches:
                feature_flags.extend(self._parse_feature_flag_block(match, flag_type))
        
        return feature_flags
    
    def _parse_config_for_flags(self, config_text: str) -> List[FeatureFlag]:
        """Parse configuration text for feature flags"""
        flags = []
        
        # Look for boolean configuration values that might be feature flags
        bool_pattern = re.compile(r'["\']([a-zA-Z][a-zA-Z0-9_]*)["\']:\s*(true|false)', re.IGNORECASE)
        matches = bool_pattern.findall(config_text)
        
        for flag_name, enabled_str in matches:
            # Filter out obvious non-feature flags
            if any(keyword in flag_name.lower() for keyword in ['feature', 'enable', 'experiment', 'test', 'rollout']):
                flag = FeatureFlag(
                    name=flag_name,
                    enabled=enabled_str.lower() == 'true'
                )
                flags.append(flag)
        
        return flags
    
    def _parse_feature_flag_block(self, flag_block: str, flag_type: str) -> List[FeatureFlag]:
        """Parse a block of text containing feature flags"""
        flags = []
        
        # Extract individual flag configurations
        flag_entries = re.findall(r'["\']([a-zA-Z][a-zA-Z0-9_]*)["\']:\s*{([^}]+)}', flag_block)
        
        for flag_name, flag_config in flag_entries:
            enabled_match = re.search(r'["\']enabled["\']:\s*(true|false)', flag_config, re.IGNORECASE)
            percentage_match = re.search(r'["\']percentage["\']:\s*(\d+(?:\.\d+)?)', flag_config)
            
            flag = FeatureFlag(
                name=flag_name,
                enabled=enabled_match.group(1).lower() == 'true' if enabled_match else False,
                rollout_percentage=float(percentage_match.group(1)) if percentage_match else None,
                description=f"Found in {flag_type} configuration"
            )
            flags.append(flag)
        
        return flags
    
    def _extract_user_metadata(self, html_source: str) -> UserMetadata:
        """Extract user and session metadata"""
        metadata = UserMetadata()
        
        # User ID patterns
        user_id_patterns = [
            re.compile(r'["\']user_id["\']:\s*["\']?(\d+)["\']?', re.IGNORECASE),
            re.compile(r'["\']userId["\']:\s*["\']?(\d+)["\']?', re.IGNORECASE),
            re.compile(r'data-user-id=["\'](\d+)["\']', re.IGNORECASE)
        ]
        
        for pattern in user_id_patterns:
            match = pattern.search(html_source)
            if match:
                metadata.user_id = match.group(1)
                break
        
        # Guest ID patterns
        guest_id_patterns = [
            re.compile(r'["\']guest_id["\']:\s*["\']?(\d+)["\']?', re.IGNORECASE),
            re.compile(r'["\']guestId["\']:\s*["\']?(\d+)["\']?', re.IGNORECASE)
        ]
        
        for pattern in guest_id_patterns:
            match = pattern.search(html_source)
            if match:
                metadata.guest_id = match.group(1)
                break
        
        # Session ID patterns
        session_patterns = [
            re.compile(r'["\']session_id["\']:\s*["\']([^"\']+)["\']', re.IGNORECASE),
            re.compile(r'["\']sessionId["\']:\s*["\']([^"\']+)["\']', re.IGNORECASE)
        ]
        
        for pattern in session_patterns:
            match = pattern.search(html_source)
            if match:
                metadata.session_id = match.group(1)
                break
        
        # Geographic and language info
        geo_patterns = {
            'country': re.compile(r'["\']country["\']:\s*["\']([^"\']+)["\']', re.IGNORECASE),
            'language': re.compile(r'["\']lang(?:uage)?["\']:\s*["\']([^"\']+)["\']', re.IGNORECASE),
            'timezone': re.compile(r'["\']timezone["\']:\s*["\']([^"\']+)["\']', re.IGNORECASE)
        }
        
        for field, pattern in geo_patterns.items():
            match = pattern.search(html_source)
            if match:
                setattr(metadata, field, match.group(1))
        
        # Client information
        client_info = {}
        client_patterns = {
            'version': re.compile(r'["\']version["\']:\s*["\']([^"\']+)["\']', re.IGNORECASE),
            'build': re.compile(r'["\']build["\']:\s*["\']([^"\']+)["\']', re.IGNORECASE),
            'platform': re.compile(r'["\']platform["\']:\s*["\']([^"\']+)["\']', re.IGNORECASE)
        }
        
        for field, pattern in client_patterns.items():
            match = pattern.search(html_source)
            if match:
                client_info[field] = match.group(1)
        
        if client_info:
            metadata.client_info = client_info
        
        return metadata
    
    def _extract_security_headers(self, html_source: str) -> Dict[str, str]:
        """Extract security-related headers and meta tags"""
        headers = {}
        
        # Content Security Policy
        csp_pattern = re.compile(r'<meta[^>]*http-equiv=["\']Content-Security-Policy["\'][^>]*content=["\']([^"\']+)["\']', re.IGNORECASE)
        csp_match = csp_pattern.search(html_source)
        if csp_match:
            headers['Content-Security-Policy'] = csp_match.group(1)
        
        # X-Frame-Options
        frame_pattern = re.compile(r'<meta[^>]*http-equiv=["\']X-Frame-Options["\'][^>]*content=["\']([^"\']+)["\']', re.IGNORECASE)
        frame_match = frame_pattern.search(html_source)
        if frame_match:
            headers['X-Frame-Options'] = frame_match.group(1)
        
        # Other security headers from meta tags
        security_meta_pattern = re.compile(r'<meta[^>]*http-equiv=["\']([^"\']*Security[^"\']*)["\'][^>]*content=["\']([^"\']+)["\']', re.IGNORECASE)
        security_matches = security_meta_pattern.findall(html_source)
        for header_name, header_value in security_matches:
            headers[header_name] = header_value
        
        return headers
    
    def fetch_and_analyze_url(self, url: str, use_selenium: bool = False) -> IntelligenceReport:
        """Fetch URL and perform comprehensive analysis"""
        if use_selenium and self.selenium_driver:
            return self._analyze_with_selenium(url)
        else:
            return self._analyze_with_requests(url)
    
    def _analyze_with_requests(self, url: str) -> IntelligenceReport:
        """Analyze URL using requests library"""
        try:
            # Rotate user agent
            headers = {
                'User-Agent': self.user_agent_rotator.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            html_source = response.text
            return self.parse_html_source(html_source, url)
            
        except Exception as e:
            # Return empty report on error
            return IntelligenceReport(
                timestamp=datetime.now(),
                target_url=url,
                api_endpoints=[],
                auth_patterns=[],
                feature_flags=[],
                user_metadata=UserMetadata(),
                security_headers={},
                performance_metrics={'error': str(e)},
                source_code_hash=hashlib.sha256(b'').hexdigest()
            )
    
    def _analyze_with_selenium(self, url: str) -> IntelligenceReport:
        """Analyze URL using Selenium for dynamic content"""
        try:
            self.selenium_driver.get(url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Get page source
            html_source = self.selenium_driver.page_source
            
            # Execute JavaScript to get additional runtime data
            try:
                js_data = self.selenium_driver.execute_script("""
                    return {
                        localStorage: JSON.stringify(localStorage),
                        sessionStorage: JSON.stringify(sessionStorage),
                        cookies: document.cookie,
                        location: window.location.href,
                        userAgent: navigator.userAgent
                    };
                """)
                
                # Incorporate JS data into analysis
                html_source += f"\\n<!-- JS_RUNTIME_DATA: {json.dumps(js_data)} -->"
                
            except:
                pass
            
            return self.parse_html_source(html_source, url)
            
        except Exception as e:
            return IntelligenceReport(
                timestamp=datetime.now(),
                target_url=url,
                api_endpoints=[],
                auth_patterns=[],
                feature_flags=[],
                user_metadata=UserMetadata(),
                security_headers={},
                performance_metrics={'selenium_error': str(e)},
                source_code_hash=hashlib.sha256(b'').hexdigest()
            )
    
    def analyze_multiple_sources(self, sources: List[Dict]) -> List[IntelligenceReport]:
        """Analyze multiple sources concurrently"""
        reports = []
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            
            for source in sources:
                if 'url' in source:
                    future = executor.submit(
                        self.fetch_and_analyze_url, 
                        source['url'], 
                        source.get('use_selenium', False)
                    )
                elif 'html' in source:
                    future = executor.submit(
                        self.parse_html_source,
                        source['html'],
                        source.get('source_url', 'provided_html')
                    )
                else:
                    continue
                
                futures.append(future)
            
            for future in as_completed(futures):
                try:
                    report = future.result(timeout=60)
                    reports.append(report)
                except Exception as e:
                    print(f"Analysis failed: {e}")
        
        return reports
    
    def generate_intelligence_summary(self, reports: List[IntelligenceReport]) -> Dict:
        """Generate comprehensive intelligence summary from multiple reports"""
        if not reports:
            return {'error': 'No reports to analyze'}
        
        summary = {
            'analysis_overview': {
                'total_reports': len(reports),
                'total_api_endpoints': sum(len(r.api_endpoints) for r in reports),
                'total_auth_tokens': sum(len(r.auth_patterns) for r in reports),
                'total_feature_flags': sum(len(r.feature_flags) for r in reports),
                'analysis_timespan': {
                    'start': min(r.timestamp for r in reports).isoformat(),
                    'end': max(r.timestamp for r in reports).isoformat()
                }
            },
            'api_intelligence': self._summarize_api_endpoints(reports),
            'authentication_intelligence': self._summarize_auth_patterns(reports),
            'feature_intelligence': self._summarize_feature_flags(reports),
            'security_intelligence': self._summarize_security_headers(reports),
            'user_intelligence': self._summarize_user_metadata(reports)
        }
        
        return summary
    
    def _summarize_api_endpoints(self, reports: List[IntelligenceReport]) -> Dict:
        """Summarize API endpoint findings"""
        all_endpoints = []
        for report in reports:
            all_endpoints.extend(report.api_endpoints)
        
        # Group by type
        by_type = {}
        by_domain = {}
        
        for endpoint in all_endpoints:
            endpoint_type = endpoint.endpoint_type
            by_type[endpoint_type] = by_type.get(endpoint_type, 0) + 1
            
            domain = urlparse(endpoint.url).netloc
            by_domain[domain] = by_domain.get(domain, 0) + 1
        
        return {
            'total_endpoints': len(all_endpoints),
            'by_type': dict(sorted(by_type.items(), key=lambda x: x[1], reverse=True)),
            'by_domain': dict(sorted(by_domain.items(), key=lambda x: x[1], reverse=True)),
            'authentication_required': sum(1 for e in all_endpoints if e.authentication_required),
            'unique_urls': len(set(e.url for e in all_endpoints))
        }
    
    def _summarize_auth_patterns(self, reports: List[IntelligenceReport]) -> Dict:
        """Summarize authentication pattern findings"""
        all_patterns = []
        for report in reports:
            all_patterns.extend(report.auth_patterns)
        
        by_type = {}
        for pattern in all_patterns:
            by_type[pattern.token_type] = by_type.get(pattern.token_type, 0) + 1
        
        return {
            'total_tokens': len(all_patterns),
            'by_type': dict(sorted(by_type.items(), key=lambda x: x[1], reverse=True)),
            'unique_tokens': len(set(p.token_value for p in all_patterns))
        }
    
    def _summarize_feature_flags(self, reports: List[IntelligenceReport]) -> Dict:
        """Summarize feature flag findings"""
        all_flags = []
        for report in reports:
            all_flags.extend(report.feature_flags)
        
        enabled_count = sum(1 for f in all_flags if f.enabled)
        disabled_count = len(all_flags) - enabled_count
        
        return {
            'total_flags': len(all_flags),
            'enabled': enabled_count,
            'disabled': disabled_count,
            'unique_flags': len(set(f.name for f in all_flags)),
            'with_rollout': sum(1 for f in all_flags if f.rollout_percentage is not None)
        }
    
    def _summarize_security_headers(self, reports: List[IntelligenceReport]) -> Dict:
        """Summarize security header findings"""
        all_headers = {}
        for report in reports:
            all_headers.update(report.security_headers)
        
        return {
            'total_headers': len(all_headers),
            'headers_found': list(all_headers.keys()),
            'csp_present': 'Content-Security-Policy' in all_headers,
            'frame_options_present': 'X-Frame-Options' in all_headers
        }
    
    def _summarize_user_metadata(self, reports: List[IntelligenceReport]) -> Dict:
        """Summarize user metadata findings"""
        user_ids = set()
        guest_ids = set()
        countries = set()
        languages = set()
        
        for report in reports:
            metadata = report.user_metadata
            if metadata.user_id:
                user_ids.add(metadata.user_id)
            if metadata.guest_id:
                guest_ids.add(metadata.guest_id)
            if metadata.country:
                countries.add(metadata.country)
            if metadata.language:
                languages.add(metadata.language)
        
        return {
            'unique_user_ids': len(user_ids),
            'unique_guest_ids': len(guest_ids),
            'countries_detected': list(countries),
            'languages_detected': list(languages)
        }
    
    def cleanup(self):
        """Clean up resources"""
        if self.selenium_driver:
            self.selenium_driver.quit()
        if self.session:
            self.session.close()

def main():
    """Main execution function"""
    print("🕵️ X.COM INTELLIGENCE PARSER")
    print("=" * 50)
    
    parser = XComIntelligenceParser()
    
    # Sample X.com HTML source (from your screenshots/data)
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' *.twitter.com">
    </head>
    <body>
        <script>
            window.__INITIAL_STATE__ = {
                "user_id": "1929549409471041537",
                "guestId": "176335502388734729",
                "country": "US",
                "language": "en",
                "featureSwitch": {
                    "defaultConfig": {
                        "new_timeline": {"enabled": true, "percentage": 75.5},
                        "dark_mode": {"enabled": false},
                        "experimental_ui": {"enabled": true, "rollout": 25.0}
                    }
                }
            };
            
            var csrf_token = "abc123def456789";
            var auth_token = "bearer_xyz789abc123";
            
            // API endpoints
            var graphqlEndpoint = "https://api.twitter.com/graphql/UserByScreenName";
            var apiV2Endpoint = "https://api.twitter.com/2/users/by/username/";
            var internalApi = "https://api.twitter.com/i/api/1.1/statuses/home_timeline.json";
            var mediaEndpoint = "https://pbs.twimg.com/media/image.jpg";
        </script>
    </body>
    </html>
    """
    
    print("🔍 Analyzing Sample X.com Source...")
    report = parser.parse_html_source(sample_html, "https://x.com/sample")
    
    print(f"API Endpoints Found: {len(report.api_endpoints)}")
    for endpoint in report.api_endpoints:
        print(f"  • {endpoint.endpoint_type}: {endpoint.url}")
    
    print(f"\\nAuthentication Tokens: {len(report.auth_patterns)}")
    for auth in report.auth_patterns:
        print(f"  • {auth.token_type}: {auth.token_value}")
    
    print(f"\\nFeature Flags: {len(report.feature_flags)}")
    for flag in report.feature_flags:
        status = "ENABLED" if flag.enabled else "DISABLED"
        rollout = f" ({flag.rollout_percentage}%)" if flag.rollout_percentage else ""
        print(f"  • {flag.name}: {status}{rollout}")
    
    print(f"\\nUser Metadata:")
    metadata = report.user_metadata
    if metadata.user_id:
        print(f"  • User ID: {metadata.user_id}")
    if metadata.guest_id:
        print(f"  • Guest ID: {metadata.guest_id}")
    if metadata.country:
        print(f"  • Country: {metadata.country}")
    if metadata.language:
        print(f"  • Language: {metadata.language}")
    
    print(f"\\nSecurity Headers: {len(report.security_headers)}")
    for header, value in report.security_headers.items():
        print(f"  • {header}: {value[:50]}{'...' if len(value) > 50 else ''}")
    
    print(f"\\nPerformance Metrics:")
    for metric, value in report.performance_metrics.items():
        print(f"  • {metric}: {value}")
    
    # Test with multiple sources
    print("\\n🔬 Testing Multiple Source Analysis...")
    sources = [
        {'html': sample_html, 'source_url': 'https://x.com/sample1'},
        {'html': sample_html.replace('user_id": "1929549409471041537"', 'user_id": "9999999999999999999"'), 'source_url': 'https://x.com/sample2'}
    ]
    
    reports = parser.analyze_multiple_sources(sources)
    summary = parser.generate_intelligence_summary(reports)
    
    print(f"\\n📊 Intelligence Summary:")
    print(f"Total Reports: {summary['analysis_overview']['total_reports']}")
    print(f"Total API Endpoints: {summary['analysis_overview']['total_api_endpoints']}")
    print(f"Total Auth Tokens: {summary['analysis_overview']['total_auth_tokens']}")
    print(f"Total Feature Flags: {summary['analysis_overview']['total_feature_flags']}")
    
    # Save intelligence report
    timestamp = int(time.time())
    report_filename = f"xcom_intelligence_report_{timestamp}.json"
    
    # Convert reports to serializable format
    serializable_reports = []
    for r in reports:
        serializable_reports.append({
            'timestamp': r.timestamp.isoformat(),
            'target_url': r.target_url,
            'api_endpoints': [asdict(e) for e in r.api_endpoints],
            'auth_patterns': [asdict(a) for a in r.auth_patterns],
            'feature_flags': [asdict(f) for f in r.feature_flags],
            'user_metadata': asdict(r.user_metadata),
            'security_headers': r.security_headers,
            'performance_metrics': r.performance_metrics,
            'source_code_hash': r.source_code_hash
        })
    
    intelligence_data = {
        'reports': serializable_reports,
        'summary': summary,
        'generator': 'XComIntelligenceParser v1.0',
        'generated_at': datetime.now().isoformat()
    }
    
    with open(report_filename, 'w') as f:
        json.dump(intelligence_data, f, indent=2, default=str)
    
    print(f"\\n✅ Intelligence report saved to: {report_filename}")
    
    # Cleanup
    parser.cleanup()

if __name__ == "__main__":
    main()