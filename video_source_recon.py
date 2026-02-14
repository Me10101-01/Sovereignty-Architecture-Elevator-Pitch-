#!/usr/bin/env python3
"""
LEGION Video Source Intelligence Analysis
Reconnaissance framework for media forensics and source tracing
"""

import re
import json
import subprocess
from urllib.parse import urlparse, parse_qs
from dataclasses import dataclass
from typing import List, Dict, Optional
import base64

@dataclass
class VideoIntelligence:
    url: str
    domain: str
    protocol: str
    path: str
    parameters: Dict
    source_type: str
    confidence: float
    metadata: Dict

class VideoSourceRecon:
    """Advanced video source reconnaissance and forensics"""
    
    def __init__(self):
        self.patterns = {
            'youtube': [
                r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
                r'youtu\.be/([a-zA-Z0-9_-]+)',
                r'youtube\.com/embed/([a-zA-Z0-9_-]+)'
            ],
            'vimeo': [
                r'vimeo\.com/(\d+)',
                r'player\.vimeo\.com/video/(\d+)'
            ],
            'twitter': [
                r'twitter\.com/.+/status/(\d+)',
                r'x\.com/.+/status/(\d+)'
            ],
            'instagram': [
                r'instagram\.com/p/([a-zA-Z0-9_-]+)',
                r'instagram\.com/reel/([a-zA-Z0-9_-]+)'
            ],
            'tiktok': [
                r'tiktok\.com/@[^/]+/video/(\d+)',
                r'vm\.tiktok\.com/([a-zA-Z0-9]+)'
            ],
            'gitkraken': [
                r'gitkraken\.com.*',
                r'glo\.gitkraken\.com.*',
                r'app\.gitkraken\.com.*'
            ],
            'jetbrains': [
                r'jetbrains\.com.*',
                r'resources\.jetbrains\.com.*',
                r'plugins\.jetbrains\.com.*'
            ],
            'generic_video': [
                r'.*\.(mp4|webm|ogg|avi|mov|wmv|flv|mkv)(\?.*)?$',
                r'.*video.*',
                r'.*media.*'
            ]
        }
        
        self.dom_selectors = [
            'video',
            'iframe[src*="youtube"]',
            'iframe[src*="vimeo"]', 
            'iframe[src*="twitter"]',
            'iframe[src*="instagram"]',
            'embed[src*="video"]',
            'object[data*="video"]',
            '[data-video-src]',
            '[data-src*="video"]',
            '.video-container',
            '.media-player',
            'audio',
            'source'
        ]

    def analyze_url_patterns(self, url: str) -> VideoIntelligence:
        """Analyze URL for video source patterns"""
        parsed = urlparse(url)
        
        # Determine source type
        source_type = "unknown"
        confidence = 0.0
        
        for platform, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    source_type = platform
                    confidence = 0.9
                    break
            if confidence > 0:
                break
        
        return VideoIntelligence(
            url=url,
            domain=parsed.netloc,
            protocol=parsed.scheme,
            path=parsed.path,
            parameters=parse_qs(parsed.query),
            source_type=source_type,
            confidence=confidence,
            metadata={
                'fragment': parsed.fragment,
                'port': parsed.port,
                'username': parsed.username,
                'password': parsed.password if parsed.password else None
            }
        )

    def extract_video_metadata(self, html_content: str) -> List[Dict]:
        """Extract video metadata from HTML content"""
        metadata = []
        
        # Look for Open Graph video tags
        og_patterns = [
            r'<meta\s+property=["\']og:video["\'][^>]*content=["\']([^"\']+)["\'][^>]*>',
            r'<meta\s+property=["\']og:video:url["\'][^>]*content=["\']([^"\']+)["\'][^>]*>',
            r'<meta\s+property=["\']og:video:secure_url["\'][^>]*content=["\']([^"\']+)["\'][^>]*>'
        ]
        
        for pattern in og_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                metadata.append({
                    'type': 'open_graph_video',
                    'url': match,
                    'source': 'meta_tag'
                })
        
        # Look for JSON-LD structured data
        json_ld_pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
        json_matches = re.findall(json_ld_pattern, html_content, re.DOTALL | re.IGNORECASE)
        
        for json_content in json_matches:
            try:
                data = json.loads(json_content)
                if isinstance(data, dict):
                    if data.get('@type') in ['VideoObject', 'Video']:
                        metadata.append({
                            'type': 'json_ld_video',
                            'data': data,
                            'source': 'structured_data'
                        })
            except json.JSONDecodeError:
                continue
        
        # Look for video/iframe sources
        video_patterns = [
            r'<video[^>]*src=["\']([^"\']+)["\'][^>]*>',
            r'<iframe[^>]*src=["\']([^"\']+)["\'][^>]*>',
            r'<source[^>]*src=["\']([^"\']+)["\'][^>]*>'
        ]
        
        for pattern in video_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                intel = self.analyze_url_patterns(match)
                metadata.append({
                    'type': 'direct_video_source',
                    'url': match,
                    'intelligence': intel.__dict__,
                    'source': 'html_element'
                })
        
        return metadata

    def generate_curl_reconnaissance(self, url: str) -> List[str]:
        """Generate curl commands for deep reconnaissance"""
        commands = []
        
        # Basic reconnaissance
        commands.append(f'curl -s -I "{url}" | grep -E "(content-type|location|server|x-)"')
        
        # Full page content analysis
        commands.append(f'curl -s -L "{url}" | grep -E "(video|iframe|embed|source)" | head -10')
        
        # Check for video API endpoints
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        api_endpoints = [
            f"{base_url}/api/video",
            f"{base_url}/api/media", 
            f"{base_url}/video/manifest",
            f"{base_url}/media/playlist.m3u8",
            f"{base_url}/.well-known/media"
        ]
        
        for endpoint in api_endpoints:
            commands.append(f'curl -s -I "{endpoint}" 2>/dev/null | grep -E "(200|302|content-type)"')
        
        # Network timing analysis
        commands.append(f'curl -w "DNS:%{{time_namelookup}} Connect:%{{time_connect}} Total:%{{time_total}}" -o /dev/null -s "{url}"')
        
        return commands

    def analyze_gitkraken_context(self) -> Dict:
        """Analyze GitKraken specific video contexts"""
        return {
            'possible_sources': [
                'GitKraken Glo board embedded videos',
                'GitKraken tutorial/onboarding videos',
                'GitKraken commit timeline animations',
                'GitKraken diff visualization videos',
                'Embedded YouTube tutorials',
                'GitKraken marketing/promotional content'
            ],
            'common_video_types': [
                'Tutorial demonstrations',
                'Feature walkthroughs', 
                'Git workflow explanations',
                'Diff/merge visualizations',
                'Onboarding sequences'
            ],
            'potential_domains': [
                'gitkraken.com',
                'glo.gitkraken.com',
                'app.gitkraken.com',
                'youtube.com/c/GitKraken',
                'vimeo.com/gitkraken',
                'resources.gitkraken.com'
            ]
        }

    def generate_recon_report(self, target_context: str = "gitkraken") -> Dict:
        """Generate comprehensive reconnaissance report"""
        report = {
            'timestamp': '2025-11-17T00:00:00Z',
            'target_context': target_context,
            'reconnaissance_phase': 'video_source_intelligence',
            'analysis': self.analyze_gitkraken_context(),
            'curl_patterns': [],
            'dom_analysis_commands': [
                "document.querySelectorAll('video, iframe, embed, object')",
                "Array.from(document.querySelectorAll('[src*=\"video\"], [data-src*=\"video\"]')).map(el => el.src || el.dataset.src)",
                "window.getComputedStyle && Array.from(document.all).filter(el => getComputedStyle(el).backgroundImage.includes('video'))",
                "[...document.scripts].filter(s => s.src && (s.src.includes('video') || s.src.includes('media'))).map(s => s.src)"
            ],
            'network_analysis': [
                "Check DevTools Network tab for video/media requests",
                "Monitor WebRTC connections",
                "Analyze WebSocket traffic for streaming data",
                "Inspect Service Worker cache for video assets"
            ],
            'forensic_techniques': [
                "Browser history analysis for video URLs",
                "Local storage inspection for video metadata",
                "Cookie analysis for video platform sessions", 
                "Memory dump analysis for buffered video data"
            ]
        }
        
        # Add specific curl patterns based on context
        if target_context == "gitkraken":
            base_urls = [
                "https://www.gitkraken.com",
                "https://glo.gitkraken.com", 
                "https://app.gitkraken.com",
                "https://resources.gitkraken.com"
            ]
            
            for base_url in base_urls:
                report['curl_patterns'].extend(self.generate_curl_reconnaissance(base_url))
        
        return report

def main():
    """Execute video source reconnaissance"""
    recon = VideoSourceRecon()
    
    print("🎯 LEGION VIDEO SOURCE INTELLIGENCE ANALYSIS")
    print("=" * 60)
    
    # Generate reconnaissance report
    report = recon.generate_recon_report("gitkraken")
    
    print(f"\n📊 Analysis Context: {report['target_context'].upper()}")
    print(f"🕐 Timestamp: {report['timestamp']}")
    
    print(f"\n🔍 GitKraken Video Source Analysis:")
    for source in report['analysis']['possible_sources']:
        print(f"  • {source}")
    
    print(f"\n🎬 Common Video Types:")
    for vtype in report['analysis']['common_video_types']:
        print(f"  • {vtype}")
    
    print(f"\n🌐 Potential Domains:")
    for domain in report['analysis']['potential_domains']:
        print(f"  • {domain}")
    
    print(f"\n🔧 DOM Analysis Commands:")
    for i, cmd in enumerate(report['dom_analysis_commands'], 1):
        print(f"  {i}. {cmd}")
    
    print(f"\n🔍 Network Analysis Techniques:")
    for technique in report['network_analysis']:
        print(f"  • {technique}")
    
    print(f"\n🕵️ Forensic Techniques:")
    for technique in report['forensic_techniques']:
        print(f"  • {technique}")
    
    print(f"\n💻 Sample Curl Reconnaissance Commands:")
    for i, cmd in enumerate(report['curl_patterns'][:5], 1):
        print(f"  {i}. {cmd}")
    
    print(f"\n🎯 DEPLOYMENT READY - Execute reconnaissance commands above")
    
    return report

if __name__ == "__main__":
    main()