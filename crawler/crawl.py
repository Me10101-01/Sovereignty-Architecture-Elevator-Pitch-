#!/usr/bin/env python3
"""
Web Crawler for STRATEGICKHAOS Empire
Specialized crawling for .gov, .edu, .org, and Google Scholar
"""

import os
import time
import json
import requests
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
import redis

# === REDIS CONNECTION ===

redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

def log_event(message: str):
    """Log crawler events"""
    timestamp = datetime.now(timezone.utc).isoformat()
    print(f"[{timestamp}] CRAWLER: {message}")

class StrategicCrawler:
    """Strategic crawler for sovereignty intelligence"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'STRATEGICKHAOS-Research-Bot/1.0 (Academic Research)'
        })
        
    def crawl_government_sites(self):
        """Crawl .gov sites for policy and regulatory information"""
        gov_sites = [
            "https://www.gsa.gov/technology/technology-purchasing-and-acquisition",
            "https://www.cisa.gov/cybersecurity-best-practices",
            "https://www.nist.gov/cyberframework",
            "https://www.sec.gov/investment/investment-adviser-marketing-rule",
            "https://www.ftc.gov/business-guidance/privacy-security"
        ]
        
        results = []
        for url in gov_sites:
            try:
                log_event(f"Crawling government site: {url}")
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    result = {
                        "url": url,
                        "title": self.extract_title(response.text),
                        "content_length": len(response.text),
                        "crawled_at": datetime.now(timezone.utc).isoformat(),
                        "domain": "government",
                        "status": "success"
                    }
                    results.append(result)
                    
                time.sleep(2)  # Respectful crawling
                
            except Exception as e:
                log_event(f"Failed to crawl {url}: {e}")
                results.append({
                    "url": url,
                    "status": "failed",
                    "error": str(e),
                    "crawled_at": datetime.now(timezone.utc).isoformat()
                })
        
        return results
    
    def crawl_educational_sites(self):
        """Crawl .edu sites for academic research"""
        edu_sites = [
            "https://cyber.harvard.edu/research",
            "https://www.law.stanford.edu/publications/",
            "https://www.berkeley.edu/research/",
            "https://www.mit.edu/research/",
            "https://www.cmu.edu/research/"
        ]
        
        results = []
        for url in edu_sites:
            try:
                log_event(f"Crawling educational site: {url}")
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    result = {
                        "url": url,
                        "title": self.extract_title(response.text),
                        "content_length": len(response.text),
                        "crawled_at": datetime.now(timezone.utc).isoformat(),
                        "domain": "education",
                        "status": "success"
                    }
                    results.append(result)
                    
                time.sleep(3)  # Extra respectful for .edu
                
            except Exception as e:
                log_event(f"Failed to crawl {url}: {e}")
                results.append({
                    "url": url,
                    "status": "failed",
                    "error": str(e),
                    "crawled_at": datetime.now(timezone.utc).isoformat()
                })
        
        return results
    
    def crawl_org_sites(self):
        """Crawl .org sites for standards and best practices"""
        org_sites = [
            "https://www.iso.org/standard/",
            "https://www.w3.org/standards/",
            "https://www.ietf.org/standards/",
            "https://opensource.org/licenses/",
            "https://creativecommons.org/licenses/"
        ]
        
        results = []
        for url in org_sites:
            try:
                log_event(f"Crawling organization site: {url}")
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    result = {
                        "url": url,
                        "title": self.extract_title(response.text),
                        "content_length": len(response.text),
                        "crawled_at": datetime.now(timezone.utc).isoformat(),
                        "domain": "organization",
                        "status": "success"
                    }
                    results.append(result)
                    
                time.sleep(2)
                
            except Exception as e:
                log_event(f"Failed to crawl {url}: {e}")
                results.append({
                    "url": url,
                    "status": "failed",
                    "error": str(e),
                    "crawled_at": datetime.now(timezone.utc).isoformat()
                })
        
        return results
    
    def extract_title(self, html_content: str) -> str:
        """Extract title from HTML content"""
        try:
            # Simple title extraction
            start = html_content.find('<title>') + 7
            end = html_content.find('</title>')
            if start > 6 and end > start:
                return html_content[start:end].strip()
        except:
            pass
        return "Unknown Title"
    
    def store_results(self, results: list, domain: str):
        """Store crawl results in Redis"""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        for result in results:
            result_key = f"crawl_result:{domain}:{timestamp}:{result['url']}"
            redis_client.setex(result_key, 86400, json.dumps(result))  # 24 hour expiry
        
        # Store summary
        summary = {
            "domain": domain,
            "total_sites": len(results),
            "successful": len([r for r in results if r.get('status') == 'success']),
            "failed": len([r for r in results if r.get('status') == 'failed']),
            "crawled_at": timestamp
        }
        
        summary_key = f"crawl_summary:{domain}:{timestamp}"
        redis_client.setex(summary_key, 86400, json.dumps(summary))
        
        log_event(f"Stored {len(results)} {domain} crawl results")

def main_crawler_loop():
    """Main crawler execution loop"""
    log_event("STRATEGIC CRAWLER STARTING")
    
    crawler = StrategicCrawler()
    
    while True:
        try:
            # Crawl government sites
            log_event("Starting government sites crawl")
            gov_results = crawler.crawl_government_sites()
            crawler.store_results(gov_results, "government")
            
            # Crawl educational sites
            log_event("Starting educational sites crawl")
            edu_results = crawler.crawl_educational_sites()
            crawler.store_results(edu_results, "education")
            
            # Crawl organization sites
            log_event("Starting organization sites crawl")
            org_results = crawler.crawl_org_sites()
            crawler.store_results(org_results, "organization")
            
            log_event("Crawl cycle complete - sleeping for 1 hour")
            time.sleep(3600)  # Sleep for 1 hour
            
        except Exception as e:
            log_event(f"Crawler loop error: {e}")
            time.sleep(300)  # Sleep 5 minutes on error

if __name__ == "__main__":
    main_crawler_loop()