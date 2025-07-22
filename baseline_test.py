# Phase 1 Baseline Testing Script
# Tests current VPS performance to establish baseline metrics

import requests
import time
import json
from datetime import datetime

# Test configuration
TEST_CONFIG = {
    "endpoint": "http://localhost:8000/scrape",
    "test_cases": [
        {"city": "New York", "query": "laptop", "max_price": 1000},
        {"city": "Los Angeles", "query": "iphone", "max_price": 800},
        {"city": "Chicago", "query": "macbook", "max_price": 1500},
    ],
    "timeout": 30
}

def run_baseline_test():
    """Run baseline tests to measure current VPS performance"""
    
    print("🔬 === PHASE 1 BASELINE TESTING ===")
    print(f"⏰ Test started at: {datetime.now().isoformat()}")
    print(f"🎯 Testing {len(TEST_CONFIG['test_cases'])} scenarios")
    print()
    
    results = []
    
    for i, test_case in enumerate(TEST_CONFIG['test_cases'], 1):
        print(f"📍 Test {i}/{len(TEST_CONFIG['test_cases'])}: {test_case['city']} - '{test_case['query']}'")
        
        start_time = time.time()
        
        try:
            # Make request to scraping endpoint
            response = requests.post(
                TEST_CONFIG["endpoint"],
                params=test_case,
                timeout=TEST_CONFIG["timeout"]
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                listings_found = data.get("listings_found", 0)
                debug_info = data.get("debug_info", {})
                
                # Analyze detection indicators
                detection_indicators = debug_info.get("detection_indicators", [])
                is_detected = len(detection_indicators) > 0
                has_login_redirect = "login" in debug_info.get("url", "").lower()
                
                result = {
                    "success": True,
                    "city": test_case["city"],
                    "query": test_case["query"],
                    "listings_found": listings_found,
                    "duration": round(duration, 2),
                    "detected": is_detected,
                    "login_redirect": has_login_redirect,
                    "detection_indicators": detection_indicators,
                    "url": debug_info.get("url", ""),
                    "html_length": debug_info.get("html_length", 0)
                }
                
                if listings_found > 0:
                    print(f"✅ SUCCESS: Found {listings_found} listings in {duration:.1f}s")
                elif is_detected or has_login_redirect:
                    print(f"🚨 DETECTED: {detection_indicators} - {debug_info.get('url', '')}")
                else:
                    print(f"⚠️  NO LISTINGS: Page loaded but no items found")
                    
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
        
        results.append(result)
        print()
        
        # Small delay between tests
        time.sleep(2)
    
    # Calculate baseline metrics
    analyze_baseline_results(results)
    
    # Save results for comparison
    save_baseline_results(results)
    
    return results

def analyze_baseline_results(results):
    """Analyze baseline test results and calculate metrics"""
    
    print("📊 === BASELINE RESULTS ANALYSIS ===")
    
    total_tests = len(results)
    successful_requests = len([r for r in results if r.get("success", False)])
    listings_found_count = len([r for r in results if r.get("listings_found", 0) > 0])
    detected_count = len([r for r in results if r.get("detected", False)])
    login_redirects = len([r for r in results if r.get("login_redirect", False)])
    
    total_listings = sum(r.get("listings_found", 0) for r in results)
    avg_duration = sum(r.get("duration", 0) for r in results) / total_tests if total_tests > 0 else 0
    
    # Calculate success rates
    request_success_rate = (successful_requests / total_tests) * 100 if total_tests > 0 else 0
    listing_success_rate = (listings_found_count / total_tests) * 100 if total_tests > 0 else 0
    detection_rate = (detected_count / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"🎯 Total Tests: {total_tests}")
    print(f"📡 Request Success Rate: {request_success_rate:.1f}% ({successful_requests}/{total_tests})")
    print(f"📋 Listing Success Rate: {listing_success_rate:.1f}% ({listings_found_count}/{total_tests})")
    print(f"🚨 Detection Rate: {detection_rate:.1f}% ({detected_count}/{total_tests})")
    print(f"🔑 Login Redirects: {login_redirects}/{total_tests}")
    print(f"📊 Total Listings Found: {total_listings}")
    print(f"⏱️ Average Duration: {avg_duration:.1f}s")
    print()
    
    # Phase 1 targets
    print("🎯 PHASE 1 TARGETS:")
    print(f"📈 Target Listing Success Rate: 20-30% (Currently: {listing_success_rate:.1f}%)")
    print(f"📉 Target Detection Rate: <50% (Currently: {detection_rate:.1f}%)")
    print(f"🎪 Improvement Needed: {max(20 - listing_success_rate, 0):.1f} percentage points")
    print()

def save_baseline_results(results):
    """Save baseline results for later comparison"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"baseline_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "phase": "Baseline (Pre-Phase 1)",
            "results": results
        }, f, indent=2)
    
    print(f"💾 Baseline results saved to: {filename}")

if __name__ == "__main__":
    print("🚀 Starting Phase 1 Baseline Testing...")
    print("📋 Make sure app_debug.py is running on localhost:8000")
    print()
    
    try:
        results = run_baseline_test()
        print("✅ Baseline testing completed!")
    except Exception as e:
        print(f"💥 Baseline testing failed: {e}")