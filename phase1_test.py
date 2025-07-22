# Phase 1 Enhanced Testing Script
# Tests Phase 1 improvements (cookies + proxies) vs baseline

import requests
import time
import json
from datetime import datetime

# Test configuration for Phase 1
TEST_CONFIG = {
    "endpoint": "http://localhost:8001/scrape",  # Phase 1 app runs on 8001
    "test_cases": [
        {"city": "New York", "query": "laptop", "max_price": 1000},
        {"city": "Los Angeles", "query": "iphone", "max_price": 800},
        {"city": "Chicago", "query": "macbook", "max_price": 1500},
    ],
    "timeout": 45  # Longer timeout for proxy connections
}

def run_phase1_tests():
    """Run Phase 1 tests to measure improvements"""
    
    print("🚀 === PHASE 1 ENHANCED TESTING ===")
    print(f"⏰ Test started at: {datetime.now().isoformat()}")
    print(f"🎯 Testing {len(TEST_CONFIG['test_cases'])} scenarios with Phase 1 enhancements")
    print()
    
    # Test different configurations
    configurations = [
        {"name": "Baseline (No Enhancements)", "use_cookies": False, "use_proxy": False},
        {"name": "Cookies Only", "use_cookies": True, "use_proxy": False},
        {"name": "Proxies Only", "use_cookies": False, "use_proxy": True},
        {"name": "Full Phase 1 (Cookies + Proxies)", "use_cookies": True, "use_proxy": True},
    ]
    
    all_results = {}
    
    for config in configurations:
        print(f"🔬 Testing Configuration: {config['name']}")
        print(f"🍪 Cookies: {config['use_cookies']}, 🌐 Proxies: {config['use_proxy']}")
        print()
        
        config_results = []
        
        for i, test_case in enumerate(TEST_CONFIG['test_cases'], 1):
            print(f"📍 Test {i}/{len(TEST_CONFIG['test_cases'])}: {test_case['city']} - '{test_case['query']}'")
            
            start_time = time.time()
            
            try:
                # Build request params
                params = {
                    **test_case,
                    "use_cookies": config["use_cookies"],
                    "use_proxy": config["use_proxy"]
                }
                
                # Make request to Phase 1 scraping endpoint
                response = requests.post(
                    TEST_CONFIG["endpoint"],
                    params=params,
                    timeout=TEST_CONFIG["timeout"]
                )
                
                end_time = time.time()
                duration = end_time - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    listings_found = data.get("listings_found", 0)
                    phase1_info = data.get("phase1_info", {})
                    
                    result = {
                        "success": True,
                        "city": test_case["city"],
                        "query": test_case["query"],
                        "listings_found": listings_found,
                        "duration": round(duration, 2),
                        "cookies_used": phase1_info.get("cookies_used", False),
                        "proxy_used": phase1_info.get("proxy_used", False),
                        "proxy_server": phase1_info.get("proxy_server"),
                        "enhancement_active": phase1_info.get("enhancement_active", False)
                    }
                    
                    status_icons = []
                    if phase1_info.get("cookies_used"):
                        status_icons.append("🍪")
                    if phase1_info.get("proxy_used"):
                        status_icons.append("🌐")
                    
                    if listings_found > 0:
                        print(f"✅ SUCCESS: Found {listings_found} listings in {duration:.1f}s {' '.join(status_icons)}")
                    else:
                        print(f"⚠️ NO LISTINGS: Access successful but no items found {' '.join(status_icons)}")
                        
                else:
                    result = {
                        "success": False,
                        "city": test_case["city"],
                        "query": test_case["query"],
                        "error": f"HTTP {response.status_code}",
                        "duration": round(duration, 2)
                    }
                    print(f"❌ ERROR: HTTP {response.status_code}")
                    
            except requests.exceptions.Timeout:
                result = {
                    "success": False,
                    "city": test_case["city"],
                    "query": test_case["query"],
                    "error": "Timeout",
                    "duration": TEST_CONFIG["timeout"]
                }
                print(f"⏱️ TIMEOUT: After {TEST_CONFIG['timeout']}s")
                
            except Exception as e:
                result = {
                    "success": False,
                    "city": test_case["city"],
                    "query": test_case["query"],
                    "error": str(e),
                    "duration": 0
                }
                print(f"💥 EXCEPTION: {str(e)}")
            
            config_results.append(result)
            print()
            
            # Small delay between tests
            time.sleep(3)
        
        all_results[config["name"]] = config_results
        print(f"✅ Configuration '{config['name']}' testing complete")
        print("=" * 60)
        print()
    
    # Analyze and compare results
    analyze_phase1_results(all_results)
    
    # Save results for analysis
    save_phase1_results(all_results)
    
    return all_results

def analyze_phase1_results(all_results):
    """Analyze Phase 1 test results and compare configurations"""
    
    print("📊 === PHASE 1 RESULTS ANALYSIS ===")
    print()
    
    config_stats = {}
    
    for config_name, results in all_results.items():
        total_tests = len(results)
        successful_requests = len([r for r in results if r.get("success", False)])
        listings_found_count = len([r for r in results if r.get("listings_found", 0) > 0])
        total_listings = sum(r.get("listings_found", 0) for r in results)
        avg_duration = sum(r.get("duration", 0) for r in results) / total_tests if total_tests > 0 else 0
        
        # Calculate success rates
        request_success_rate = (successful_requests / total_tests) * 100 if total_tests > 0 else 0
        listing_success_rate = (listings_found_count / total_tests) * 100 if total_tests > 0 else 0
        
        config_stats[config_name] = {
            "request_success_rate": request_success_rate,
            "listing_success_rate": listing_success_rate,
            "total_listings": total_listings,
            "avg_duration": avg_duration,
            "successful_requests": successful_requests,
            "total_tests": total_tests
        }
        
        print(f"🔬 {config_name}:")
        print(f"   📡 Request Success: {request_success_rate:.1f}% ({successful_requests}/{total_tests})")
        print(f"   📋 Listing Success: {listing_success_rate:.1f}%")
        print(f"   📊 Total Listings: {total_listings}")
        print(f"   ⏱️ Avg Duration: {avg_duration:.1f}s")
        print()
    
    # Calculate improvements
    print("📈 === IMPROVEMENT ANALYSIS ===")
    baseline_stats = config_stats.get("Baseline (No Enhancements)", {})
    baseline_listing_rate = baseline_stats.get("listing_success_rate", 0)
    
    for config_name, stats in config_stats.items():
        if config_name == "Baseline (No Enhancements)":
            continue
        
        listing_improvement = stats["listing_success_rate"] - baseline_listing_rate
        listing_multiplier = stats["listing_success_rate"] / baseline_listing_rate if baseline_listing_rate > 0 else float('inf')
        
        improvement_icon = "📈" if listing_improvement > 0 else "📉" if listing_improvement < 0 else "➡️"
        
        print(f"{improvement_icon} {config_name}:")
        print(f"   Listing Success Rate: {stats['listing_success_rate']:.1f}% ({listing_improvement:+.1f} pp)")
        if listing_multiplier != float('inf'):
            print(f"   Improvement Factor: {listing_multiplier:.1f}x")
        print(f"   Additional Listings: +{stats['total_listings'] - baseline_stats.get('total_listings', 0)}")
        print()
    
    # Best performing configuration
    best_config = max(config_stats.items(), key=lambda x: x[1]["listing_success_rate"])
    print(f"🏆 BEST PERFORMING: {best_config[0]}")
    print(f"   Success Rate: {best_config[1]['listing_success_rate']:.1f}%")
    print(f"   Total Listings: {best_config[1]['total_listings']}")
    print()
    
    # Phase 1 target analysis
    target_rate = 25  # Phase 1 target: 20-30%
    full_phase1_stats = config_stats.get("Full Phase 1 (Cookies + Proxies)", {})
    full_rate = full_phase1_stats.get("listing_success_rate", 0)
    
    print("🎯 === PHASE 1 TARGET ANALYSIS ===")
    print(f"Target Success Rate: {target_rate}%")
    print(f"Full Phase 1 Rate: {full_rate:.1f}%")
    
    if full_rate >= target_rate:
        print("✅ PHASE 1 TARGET ACHIEVED!")
    else:
        gap = target_rate - full_rate
        print(f"⚠️ Gap to target: {gap:.1f} percentage points")
        
        if full_rate > baseline_listing_rate:
            print("✅ Improvement over baseline achieved")
        else:
            print("❌ No improvement over baseline")

def save_phase1_results(all_results):
    """Save Phase 1 results for comparison"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"phase1_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "phase": "Phase 1 Enhanced (Cookies + Proxies)",
            "configurations": all_results
        }, f, indent=2)
    
    print(f"💾 Phase 1 results saved to: {filename}")

if __name__ == "__main__":
    print("🚀 Starting Phase 1 Enhanced Testing...")
    print("📋 Make sure app_phase1.py is running on localhost:8001")
    print("⚠️ This will test multiple configurations - may take 10-15 minutes")
    print()
    
    input("Press Enter to continue...")
    
    try:
        results = run_phase1_tests()
        print("✅ Phase 1 testing completed!")
        print("📁 Check the generated JSON file for detailed results")
    except Exception as e:
        print(f"💥 Phase 1 testing failed: {e}")