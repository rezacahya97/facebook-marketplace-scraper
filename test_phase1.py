#!/usr/bin/env python3
# Simple Phase 1 Test Script
# Tests the enhanced app.py with cookies and proxies

import requests
import time

def test_phase1_scraper():
    """Test the Phase 1 enhanced scraper"""
    
    print("🚀 Testing Phase 1 Enhanced Scraper")
    print("=" * 50)
    
    # Test configurations
    tests = [
        {
            "name": "Baseline (No Enhancements)",
            "params": {
                "city": "New York",
                "query": "laptop", 
                "max_price": 1000,
                "use_cookies": False,
                "use_proxy": False
            }
        },
        {
            "name": "Cookies Only", 
            "params": {
                "city": "New York",
                "query": "laptop",
                "max_price": 1000,
                "use_cookies": True,
                "use_proxy": False
            }
        },
        {
            "name": "Proxies Only",
            "params": {
                "city": "New York", 
                "query": "laptop",
                "max_price": 1000,
                "use_cookies": False,
                "use_proxy": True
            }
        },
        {
            "name": "Full Phase 1 (Cookies + Proxies)",
            "params": {
                "city": "New York",
                "query": "laptop", 
                "max_price": 1000,
                "use_cookies": True,
                "use_proxy": True
            }
        }
    ]
    
    results = {}
    
    for test in tests:
        print(f"\n🔬 Testing: {test['name']}")
        print(f"🍪 Cookies: {test['params']['use_cookies']}")
        print(f"🌐 Proxy: {test['params']['use_proxy']}")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                "http://localhost:8000/scrape",
                params=test['params'],
                timeout=30
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                listings_found = data.get("listings_found", 0)
                phase1_info = data.get("phase1_info", {})
                
                results[test['name']] = {
                    "success": True,
                    "listings_found": listings_found,
                    "duration": duration,
                    "phase1_info": phase1_info
                }
                
                print(f"✅ SUCCESS: Found {listings_found} listings in {duration:.1f}s")
                if phase1_info:
                    print(f"   🍪 Cookies used: {phase1_info.get('cookies_used', False)}")
                    print(f"   🌐 Proxy used: {phase1_info.get('proxy_used', False)}")
                    if phase1_info.get('proxy_server'):
                        print(f"   🌐 Proxy server: {phase1_info['proxy_server']}")
                
            else:
                results[test['name']] = {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "duration": duration
                }
                print(f"❌ ERROR: HTTP {response.status_code}")
                
        except Exception as e:
            results[test['name']] = {
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time
            }
            print(f"💥 EXCEPTION: {e}")
        
        print("-" * 30)
    
    # Summary
    print("\n📊 PHASE 1 TEST SUMMARY")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "✅" if result.get("success") else "❌"
        listings = result.get("listings_found", 0)
        duration = result.get("duration", 0)
        
        print(f"{status} {test_name}")
        print(f"   Listings: {listings}, Duration: {duration:.1f}s")
        
        if result.get("success") and result.get("phase1_info"):
            phase1_info = result["phase1_info"]
            enhancements = []
            if phase1_info.get("cookies_used"):
                enhancements.append("🍪 Cookies")
            if phase1_info.get("proxy_used"):
                enhancements.append("🌐 Proxy")
            if enhancements:
                print(f"   Active: {', '.join(enhancements)}")
        
        if not result.get("success"):
            print(f"   Error: {result.get('error', 'Unknown')}")
        print()
    
    # Find best performing
    successful_tests = {k: v for k, v in results.items() if v.get("success")}
    if successful_tests:
        best = max(successful_tests.items(), key=lambda x: x[1].get("listings_found", 0))
        print(f"🏆 BEST PERFORMING: {best[0]}")
        print(f"   Found {best[1]['listings_found']} listings")
    
    print("\n✅ Phase 1 testing complete!")

if __name__ == "__main__":
    print("🧪 Phase 1 Enhanced Scraper Test")
    print("Make sure app.py is running on localhost:8000")
    print()
    
    input("Press Enter to start testing...")
    test_phase1_scraper()