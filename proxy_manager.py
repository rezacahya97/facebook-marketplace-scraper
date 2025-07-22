# Phase 1: Free Proxy Management System
# Implements free proxy fetching and rotation for IP-based detection bypass

import requests
import time
import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from fake_useragent import UserAgent

class ProxyManager:
    """Manages free proxy fetching and rotation"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.proxies_cache = []
        self.working_proxies = []
        self.failed_proxies = set()
        self.last_fetch_time = None
        
        # Proxy sources (free proxy APIs)
        self.proxy_sources = [
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        ]
        
        # Test URLs for proxy validation
        self.test_urls = [
            "http://httpbin.org/ip",
            "https://api.ipify.org?format=json",
            "http://ip-api.com/json"
        ]
        
        self.proxy_timeout = 10  # seconds
        self.cache_duration_minutes = 30
    
    def fetch_fresh_proxies(self) -> List[str]:
        """Fetch fresh proxies from multiple sources"""
        print("🔄 Fetching fresh proxies from sources...")
        
        all_proxies = set()
        
        for source_url in self.proxy_sources:
            try:
                print(f"📡 Fetching from: {source_url}")
                
                headers = {'User-Agent': self.ua.random}
                response = requests.get(source_url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    # Parse proxy list (usually one proxy per line)
                    proxies = response.text.strip().split('\n')
                    valid_proxies = []
                    
                    for proxy in proxies:
                        proxy = proxy.strip()
                        # Basic format validation (IP:PORT)
                        if ':' in proxy and len(proxy.split('.')) == 4:
                            parts = proxy.split(':')
                            if len(parts) == 2 and parts[1].isdigit():
                                valid_proxies.append(proxy)
                    
                    all_proxies.update(valid_proxies)
                    print(f"✅ Found {len(valid_proxies)} proxies from source")
                else:
                    print(f"❌ Failed to fetch from {source_url}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error fetching from {source_url}: {e}")
        
        proxy_list = list(all_proxies)
        random.shuffle(proxy_list)  # Randomize order
        
        print(f"🎯 Total unique proxies collected: {len(proxy_list)}")
        
        self.proxies_cache = proxy_list
        self.last_fetch_time = datetime.now()
        
        return proxy_list
    
    def test_proxy(self, proxy: str) -> bool:
        """Test if a proxy is working"""
        proxy_dict = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
        
        for test_url in self.test_urls:
            try:
                headers = {'User-Agent': self.ua.random}
                response = requests.get(
                    test_url, 
                    proxies=proxy_dict, 
                    headers=headers,
                    timeout=self.proxy_timeout
                )
                
                if response.status_code == 200:
                    # Additional validation - check if we get a different IP
                    try:
                        data = response.json()
                        if 'ip' in data or 'origin' in data:
                            return True
                    except:
                        # If it's not JSON, but status is 200, it might still work
                        if len(response.text) > 0:
                            return True
                        
            except Exception:
                continue
        
        return False
    
    def find_working_proxies(self, max_proxies: int = 10, max_test_time: int = 60) -> List[str]:
        """Find working proxies from the cache"""
        print(f"🧪 Testing proxies to find {max_proxies} working ones...")
        
        if not self.proxies_cache:
            self.fetch_fresh_proxies()
        
        working_proxies = []
        tested_count = 0
        start_time = time.time()
        
        # Test proxies in batches
        for proxy in self.proxies_cache:
            if proxy in self.failed_proxies:
                continue
                
            if len(working_proxies) >= max_proxies:
                break
                
            if time.time() - start_time > max_test_time:
                print(f"⏰ Testing timeout reached ({max_test_time}s)")
                break
            
            tested_count += 1
            print(f"🔍 Testing proxy {tested_count}: {proxy}")
            
            if self.test_proxy(proxy):
                working_proxies.append(proxy)
                print(f"✅ Working proxy found: {proxy}")
            else:
                self.failed_proxies.add(proxy)
                print(f"❌ Proxy failed: {proxy}")
        
        self.working_proxies = working_proxies
        print(f"🎯 Found {len(working_proxies)} working proxies out of {tested_count} tested")
        
        return working_proxies
    
    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """Get a random working proxy"""
        if not self.working_proxies:
            print("⚠️ No working proxies available, finding new ones...")
            self.find_working_proxies()
        
        if not self.working_proxies:
            print("❌ No working proxies found!")
            return None
        
        proxy = random.choice(self.working_proxies)
        
        return {
            'server': f'http://{proxy}',
            'proxy': proxy,
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
    
    def get_proxy_for_playwright(self) -> Optional[Dict[str, str]]:
        """Get proxy configuration for Playwright"""
        proxy_info = self.get_random_proxy()
        
        if not proxy_info:
            return None
        
        # Parse proxy for Playwright format
        proxy_parts = proxy_info['proxy'].split(':')
        
        return {
            'server': f'http://{proxy_info["proxy"]}',
            'username': None,  # Free proxies usually don't have auth
            'password': None
        }
    
    def validate_proxy_cache(self) -> bool:
        """Check if proxy cache is still valid"""
        if not self.last_fetch_time:
            return False
        
        cache_age = datetime.now() - self.last_fetch_time
        return cache_age.total_seconds() < (self.cache_duration_minutes * 60)
    
    def get_proxy_stats(self) -> Dict:
        """Get statistics about proxy status"""
        cache_valid = self.validate_proxy_cache()
        cache_age_minutes = 0
        
        if self.last_fetch_time:
            cache_age_minutes = (datetime.now() - self.last_fetch_time).total_seconds() / 60
        
        return {
            'total_cached': len(self.proxies_cache),
            'working_proxies': len(self.working_proxies),
            'failed_proxies': len(self.failed_proxies),
            'cache_valid': cache_valid,
            'cache_age_minutes': round(cache_age_minutes, 1),
            'sources_count': len(self.proxy_sources)
        }
    
    def refresh_working_proxies(self):
        """Refresh the list of working proxies"""
        print("🔄 Refreshing working proxy list...")
        self.working_proxies = []
        self.failed_proxies.clear()
        
        # Re-fetch if cache is old
        if not self.validate_proxy_cache():
            self.fetch_fresh_proxies()
        
        self.find_working_proxies()

# Alternative: Manual proxy list for testing
class ManualProxyManager:
    """Simple proxy manager with manually configured proxies"""
    
    def __init__(self, proxy_list: List[str] = None):
        # Example free proxies (these change frequently, for testing only)
        self.proxy_list = proxy_list or [
            "47.74.152.29:8888",
            "103.149.162.194:80", 
            "20.206.106.192:80",
            "128.199.202.122:3128"
        ]
        
        self.current_index = 0
    
    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Get next proxy in rotation"""
        if not self.proxy_list:
            return None
        
        proxy = self.proxy_list[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxy_list)
        
        return {
            'server': f'http://{proxy}',
            'proxy': proxy,
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
    
    def get_proxy_for_playwright(self) -> Optional[Dict[str, str]]:
        """Get proxy configuration for Playwright"""
        proxy_info = self.get_next_proxy()
        
        if not proxy_info:
            return None
        
        return {
            'server': proxy_info['server'],
            'username': None,
            'password': None
        }

# Helper functions
def create_proxy_manager(use_manual: bool = False, manual_proxies: List[str] = None):
    """Factory function to create proxy manager"""
    if use_manual:
        return ManualProxyManager(manual_proxies)
    else:
        return ProxyManager()

def test_proxy_manager():
    """Test the proxy manager functionality"""
    print("🔍 === TESTING PROXY MANAGER ===")
    
    manager = ProxyManager()
    
    # Get stats
    stats = manager.get_proxy_stats()
    print(f"📊 Initial stats: {stats}")
    
    # Fetch proxies
    proxies = manager.fetch_fresh_proxies()
    print(f"📡 Fetched {len(proxies)} proxies")
    
    # Find working ones
    working = manager.find_working_proxies(max_proxies=3, max_test_time=30)
    print(f"✅ Found {len(working)} working proxies")
    
    # Test getting random proxy
    proxy = manager.get_random_proxy()
    if proxy:
        print(f"🎲 Random proxy: {proxy['proxy']}")
    
    # Test Playwright format
    pw_proxy = manager.get_proxy_for_playwright()
    if pw_proxy:
        print(f"🎭 Playwright proxy: {pw_proxy}")

if __name__ == "__main__":
    test_proxy_manager()