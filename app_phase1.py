# Phase 1 Enhanced App: Cookie + Free Proxy Integration
# Combines existing VPS scraper with cookie persistence and proxy rotation

from playwright.sync_api import sync_playwright
import os
import time
import random
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
import json
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from database import save_listing
from datetime import datetime

# Import Phase 1 components
from cookie_manager import CookieManager
from proxy_manager import ProxyManager, ManualProxyManager

# Create FastAPI instance
app = FastAPI(
    title="Facebook Marketplace Scraper API - PHASE 1 ENHANCED",
    description="VPS scraper with cookies + free proxy rotation",
    version="2.2.0-phase1"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Initialize Phase 1 managers
cookie_manager = CookieManager()
proxy_manager = ProxyManager()

# Health check endpoint
@app.get("/health")
def health_check():
    """Phase 1 health check with component status"""
    cookie_stats = cookie_manager.get_session_stats()
    proxy_stats = proxy_manager.get_proxy_stats()
    
    return {
        "status": "healthy",
        "service": "Facebook Marketplace Scraper - PHASE 1 ENHANCED",
        "strategy": "VPS + Cookies + Free Proxies",
        "version": "2.2.0-phase1",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "cookies": {
                "valid_sessions": cookie_stats["valid_sessions"],
                "total_sessions": cookie_stats["total_sessions"]
            },
            "proxies": {
                "working_proxies": proxy_stats["working_proxies"],
                "total_cached": proxy_stats["total_cached"]
            }
        }
    }

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Facebook Marketplace Scraper API - PHASE 1 ENHANCED",
        "strategy": "Strategy A + Cookie Management + Free Proxy Rotation",
        "version": "2.2.0-phase1",
        "features": [
            "Cookie persistence and rotation",
            "Free proxy integration", 
            "Enhanced randomization",
            "Detection pattern analysis"
        ],
        "endpoints": {
            "health": "/health",
            "scrape": "/scrape",
            "test-cookies": "/test-cookies",
            "test-proxies": "/test-proxies"
        }
    }

# Phase 1 Enhanced scraping endpoint
@app.post("/scrape")
def scrape_marketplace_phase1(city: str, query: str, max_price: int, 
                              use_cookies: bool = True, use_proxy: bool = True):
    """Phase 1 enhanced scraping with cookies and proxies"""
    
    try:
        print(f"🚀 PHASE 1 Scraper: Starting enhanced scrape")
        print(f"📍 Target: {city}, Query: '{query}', Max Price: ${max_price}")
        print(f"🍪 Use Cookies: {use_cookies}")
        print(f"🌐 Use Proxy: {use_proxy}")
        
        # Get proxy if enabled
        proxy_config = None
        if use_proxy:
            proxy_config = proxy_manager.get_proxy_for_playwright()
            if proxy_config:
                print(f"🌐 Using proxy: {proxy_config['server']}")
            else:
                print("⚠️ No working proxy available, proceeding without proxy")
        
        # Enhanced browser configuration
        with sync_playwright() as p:
            # Launch browser with optional proxy
            browser_args = [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-blink-features=AutomationControlled',
                '--disable-features=VizDisplayCompositor',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-images',
                '--no-first-run',
                '--no-default-browser-check',
            ]
            
            browser = p.chromium.launch(
                headless=True,
                args=browser_args,
                proxy=proxy_config  # Apply proxy if available
            )
            
            # Enhanced context with randomization
            context = browser.new_context(
                viewport={"width": random.randint(1366, 1920), "height": random.randint(768, 1080)},
                user_agent=get_random_user_agent(),
                locale="en-US",
                timezone_id=random.choice(["America/New_York", "America/Chicago", "America/Los_Angeles"]),
                geolocation={"longitude": -74.0059, "latitude": 40.7128},
                permissions=["geolocation"]
            )
            
            # Load cookies if enabled
            cookies_loaded = False
            if use_cookies:
                available_sessions = cookie_manager.get_available_sessions()
                if available_sessions:
                    session_name = random.choice(available_sessions)
                    cookies_loaded = cookie_manager.load_cookies(context, session_name)
                    print(f"🍪 Cookies loaded: {cookies_loaded} (session: {session_name})")
                else:
                    print("⚠️ No valid cookie sessions available")
            
            page = context.new_page()
            
            # Enhanced anti-detection script injection
            page.add_init_script("""
                // Remove webdriver detection
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                // Mock chrome runtime
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                };
                
                // Mock plugins with randomization
                Object.defineProperty(navigator, 'plugins', {
                    get: () => Array.from({length: Math.floor(Math.random() * 5) + 3}, (_, i) => i),
                });
                
                // Random screen resolution
                Object.defineProperty(screen, 'width', {
                    get: () => window.outerWidth
                });
                Object.defineProperty(screen, 'height', {
                    get: () => window.outerHeight
                });
            """)
            
            # Call enhanced scraping logic
            results = scrape_facebook_marketplace_enhanced(page, city, query, max_price, use_cookies)
            
            # Save cookies if we successfully accessed Facebook
            if use_cookies and not cookies_loaded and len(results) > 0:
                cookie_manager.save_cookies(page, f"auto_{datetime.now().strftime('%Y%m%d_%H%M')}")
                print("🍪 Saved new cookie session for future use")
            
            browser.close()
            
        print(f"✅ PHASE 1 Scraper: Found {len(results)} listings")
        
        # Enhanced response with Phase 1 details
        return {
            "success": True, 
            "listings_found": len(results), 
            "data": results,
            "phase1_info": {
                "cookies_used": use_cookies and cookies_loaded,
                "proxy_used": use_proxy and proxy_config is not None,
                "proxy_server": proxy_config['server'] if proxy_config else None,
                "enhancement_active": True
            }
        }
        
    except Exception as e:
        print(f"❌ PHASE 1 Scraper failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_random_user_agent():
    """Get randomized user agent"""
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    return random.choice(agents)

def scrape_facebook_marketplace_enhanced(page, city, query, max_price, cookies_enabled=True):
    """Enhanced scraping logic with randomization"""
    
    # Build marketplace URL
    cities = {
        'New York': 'nyc', 'Los Angeles': 'la', 'Las Vegas': 'vegas',
        'Chicago': 'chicago', 'Houston': 'houston', 'Miami': 'miami',
        'Orlando': 'orlando', 'San Diego': 'sandiego', 'Boston': 'boston'
    }
    
    city_slug = cities.get(city, city.lower().replace(' ', ''))
    marketplace_url = f'https://www.facebook.com/marketplace/{city_slug}/search/?query={query}&maxPrice={max_price}'
    
    print(f"🌐 Enhanced Navigation to: {marketplace_url}")
    page.goto(marketplace_url)
    
    # Enhanced randomized wait
    wait_time = random.uniform(3, 7)  # Random 3-7 seconds instead of static 5
    print(f"⏱️ Randomized wait: {wait_time:.1f}s")
    time.sleep(wait_time)
    
    # Enhanced popup dismissal with randomization
    dismiss_popups_enhanced(page)
    
    # Analyze page content for debugging
    page_analysis = analyze_page_content_enhanced(page, city, query)
    
    # Parse listings
    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')
    results = parse_marketplace_listings_enhanced(soup, city, query)
    
    return results

def dismiss_popups_enhanced(page):
    """Enhanced popup dismissal with randomization"""
    max_attempts = random.randint(2, 4)  # Randomize attempts
    
    for attempt in range(max_attempts):
        try:
            # Random small delay before each attempt
            time.sleep(random.uniform(0.5, 1.5))
            
            close_selectors = [
                'div[role="dialog"] button[aria-label="Close"]',
                'div[role="dialog"] svg[aria-label="Close"]', 
                'button[aria-label="Close"]',
                'div[role="dialog"] button:has-text("×")',
                'div[role="dialog"] div[data-testid="close-button"]'
            ]
            
            popup_found = False
            for selector in close_selectors:
                if page.locator(selector).count() > 0:
                    # Random small delay before clicking
                    time.sleep(random.uniform(0.1, 0.3))
                    page.locator(selector).first.click()
                    popup_found = True
                    time.sleep(random.uniform(1, 2))
                    break
            
            if not popup_found:
                if page.locator('div[role="dialog"]').count() > 0:
                    page.keyboard.press('Escape')
                    time.sleep(random.uniform(1, 2))
                else:
                    break
                    
        except Exception as e:
            print(f"Enhanced popup dismissal error: {e}")
            time.sleep(random.uniform(0.5, 1))

def analyze_page_content_enhanced(page, city, query):
    """Enhanced page content analysis"""
    
    print("🔍 === PHASE 1 PAGE ANALYSIS ===")
    
    page_title = page.title()
    current_url = page.url
    html_content = page.content()
    
    print(f"📄 Title: {page_title}")
    print(f"🌐 URL: {current_url}")
    print(f"📊 HTML Length: {len(html_content):,} chars")
    
    # Enhanced detection indicators
    detection_indicators = [
        "login", "log in", "sign in", "checkpoint", "security", 
        "unusual activity", "verify", "captcha", "robot", "automated",
        "suspicious", "blocked", "restricted"
    ]
    
    html_lower = html_content.lower()
    found_indicators = [indicator for indicator in detection_indicators if indicator in html_lower]
    
    if found_indicators:
        print(f"🚨 DETECTION INDICATORS: {found_indicators}")
    else:
        print("✅ No detection indicators found")
    
    # Check for successful marketplace access
    marketplace_indicators = ["marketplace", "listing", "item", "price", "$"]
    found_marketplace = [indicator for indicator in marketplace_indicators if indicator in html_lower]
    
    print(f"🏪 Marketplace indicators: {len(found_marketplace)}/5")
    print("🔍 === ANALYSIS END ===")
    
    return {
        "title": page_title,
        "url": current_url,
        "html_length": len(html_content),
        "detection_indicators": found_indicators,
        "marketplace_indicators": found_marketplace
    }

def parse_marketplace_listings_enhanced(soup, city, query):
    """Enhanced listing parsing with better error handling"""
    parsed = []
    
    listing_selectors = [
        'div[data-testid="marketplace-item"]',
        'div.x9f619.x78zum5.x1r8uery.xdt5ytf.x1iyjqo2.xs83m0k.x1e558r4.x150jy0e.x1iorvi4.xjkvuk6.xnpuxes.x291uyu.x1uepa24',
        'div[role="article"]',
        'a[href*="/marketplace/item/"]'
    ]
    
    listings = []
    for selector in listing_selectors:
        listings = soup.select(selector)
        print(f"🎯 Selector '{selector}': {len(listings)} elements")
        if listings:
            break
    
    for i, listing in enumerate(listings[:20]):  # Limit to first 20 for testing
        try:
            post_url = extract_post_url_enhanced(listing)
            if not post_url:
                continue
                
            image = extract_image_enhanced(listing)
            title = extract_title_enhanced(listing)
            price = extract_price_enhanced(listing)
            location = extract_location_enhanced(listing)
            
            # Enhanced data validation
            if title != "No title found" and price != "Price not found":
                listing_data = {
                    "title": title,
                    "price": price,
                    "location": location,
                    "image": image,
                    "post_url": post_url,
                    "city": city,
                    "search_query": query
                }
                
                # Save to database
                save_listing(listing_data)
                
                # Add to results
                parsed.append({
                    "name": title,
                    "price": price,
                    "location": location,
                    "title": title,
                    "image": image,
                    "link": post_url.replace('https://www.facebook.com', '')
                })
                
                print(f"✅ Parsed listing {i+1}: {title[:50]}...")
            
        except Exception as e:
            print(f"⚠️ Error parsing listing {i+1}: {e}")
            continue
    
    return parsed

# Enhanced extraction functions (same logic, better error handling)
def extract_post_url_enhanced(listing):
    """Enhanced post URL extraction"""
    try:
        if listing.name == 'a' and listing.get('href') and '/marketplace/item/' in str(listing.get('href')):
            href_val = listing.get('href')
            if isinstance(href_val, str):
                return 'https://www.facebook.com' + href_val
        
        link_elements = listing.find_all('a')
        for link in link_elements:
            href_val = link.get('href')
            if href_val and isinstance(href_val, str) and '/marketplace/item/' in href_val:
                return 'https://www.facebook.com' + href_val
    except Exception as e:
        print(f"URL extraction error: {e}")
    return None

def extract_image_enhanced(listing):
    """Enhanced image extraction"""
    try:
        img_element = listing.find('img')
        if img_element and hasattr(img_element, 'get'):
            src_val = img_element.get('src')
            if src_val and isinstance(src_val, str) and 'http' in src_val:
                return src_val
    except Exception as e:
        print(f"Image extraction error: {e}")
    return "No image found"

def extract_title_enhanced(listing):
    """Enhanced title extraction"""
    try:
        all_spans = listing.find_all('span')
        for span in all_spans:
            if span.get_text(strip=True):
                span_text = span.get_text(strip=True)
                if (len(span_text) > 5 and 
                    not span_text.startswith('$') and 
                    len(span_text) < 200 and
                    not any(keyword in span_text.lower() for keyword in ['miles', 'away', 'km'])):
                    return span_text
    except Exception as e:
        print(f"Title extraction error: {e}")
    return "No title found"

def extract_price_enhanced(listing):
    """Enhanced price extraction"""
    try:
        all_text_elements = listing.find_all(string=True)
        for text_elem in all_text_elements:
            if text_elem and hasattr(text_elem, 'strip'):
                text_clean = text_elem.strip()
                if text_clean.startswith('$') and len(text_clean) > 1 and len(text_clean) < 20:
                    return text_clean
    except Exception as e:
        print(f"Price extraction error: {e}")
    return "Price not found"

def extract_location_enhanced(listing):
    """Enhanced location extraction"""
    try:
        all_text_elements = listing.find_all(string=True)
        location_keywords = ['miles away', 'mi away', 'km away', 'miles', 'mi']
        
        for text_elem in all_text_elements:
            if text_elem and hasattr(text_elem, 'strip'):
                text_clean = text_elem.strip()
                if any(keyword in text_clean.lower() for keyword in location_keywords):
                    return text_clean
    except Exception as e:
        print(f"Location extraction error: {e}")
    return "Location not found"

# Test endpoints
@app.get("/test-cookies")
def test_cookies():
    """Test cookie manager status"""
    stats = cookie_manager.get_session_stats()
    return {
        "cookie_manager": "active",
        "stats": stats
    }

@app.get("/test-proxies")
def test_proxies():
    """Test proxy manager status"""
    stats = proxy_manager.get_proxy_stats()
    return {
        "proxy_manager": "active", 
        "stats": stats
    }

if __name__ == "__main__":
    print("🚀 Starting Phase 1 Enhanced Server...")
    print("🍪 Cookie management: ENABLED")
    print("🌐 Free proxy rotation: ENABLED")
    print("🎲 Enhanced randomization: ENABLED")
    
    uvicorn.run(
        'app_phase1:app',
        host='0.0.0.0',
        port=8001,  # Different port to avoid conflicts
        reload=False,
        access_log=True,
        log_level="info"
    )