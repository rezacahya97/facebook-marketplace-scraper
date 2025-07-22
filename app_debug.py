from playwright.sync_api import sync_playwright
import os
import time
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
import json
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from database import save_listing
from datetime import datetime

# Create FastAPI instance
app = FastAPI(
    title="Facebook Marketplace Scraper API - DEBUG VERSION",
    description="VPS-optimized scraper with HTML content analysis",
    version="2.1.0-debug"
)

# Configure CORS for VPS deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
def health_check():
    """VPS health check endpoint"""
    return {
        "status": "healthy",
        "service": "Facebook Marketplace Scraper - DEBUG VERSION",
        "strategy": "VPS + Cron (Strategy A)",
        "version": "2.1.0-debug",
        "timestamp": datetime.utcnow().isoformat()
    }

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Facebook Marketplace Scraper API - DEBUG VERSION",
        "strategy": "Strategy A: VPS + Cron",
        "version": "2.1.0-debug",
        "debug": "HTML content analysis enabled",
        "endpoints": {
            "health": "/health",
            "scrape": "/scrape",
            "crawl": "/crawl_facebook_marketplace"
        }
    }

# Enhanced debugging function
def analyze_page_content(page, city, query):
    """Analyze what Facebook actually serves to VPS"""
    
    print("🔍 === PAGE CONTENT ANALYSIS START ===")
    
    # Get basic page info
    page_title = page.title()
    current_url = page.url
    
    print(f"📄 Page Title: {page_title}")
    print(f"🌐 Current URL: {current_url}")
    
    # Check for redirects
    expected_url_part = f"facebook.com/marketplace/{city.lower()}"
    if expected_url_part not in current_url.lower():
        print(f"⚠️ REDIRECT DETECTED! Expected: {expected_url_part}, Got: {current_url}")
    
    # Get HTML content
    html_content = page.content()
    html_length = len(html_content)
    
    print(f"📊 HTML Content Length: {html_length:,} characters")
    
    # Check for specific Facebook detection indicators
    detection_indicators = [
        "login", "log in", "sign in", "checkpoint", "security", 
        "unusual activity", "verify", "captcha", "robot", "automated"
    ]
    
    html_lower = html_content.lower()
    found_indicators = [indicator for indicator in detection_indicators if indicator in html_lower]
    
    if found_indicators:
        print(f"🚨 DETECTION INDICATORS FOUND: {found_indicators}")
    else:
        print("✅ No obvious detection indicators found")
    
    # Check for marketplace-specific elements
    marketplace_indicators = [
        "marketplace", "listing", "item", "price", "$", "seller", "buy", "shop"
    ]
    
    found_marketplace = [indicator for indicator in marketplace_indicators if indicator in html_lower]
    print(f"🏪 Marketplace indicators found: {found_marketplace}")
    
    # Save HTML snippet for manual inspection
    html_snippet = html_content[:2000] if len(html_content) > 2000 else html_content
    print(f"📝 HTML SNIPPET (first 2000 chars):")
    print("=" * 50)
    print(html_snippet)
    print("=" * 50)
    
    # Check for empty body or minimal content
    soup = BeautifulSoup(html_content, 'html.parser')
    body = soup.find('body')
    if body:
        body_text = body.get_text(strip=True)
        print(f"📄 Body text length: {len(body_text)} characters")
        if len(body_text) < 100:
            print("⚠️ WARNING: Very minimal body content!")
            print(f"Body text: {body_text[:200]}...")
    else:
        print("❌ ERROR: No body tag found!")
    
    # Check for specific Facebook marketplace selectors
    marketplace_selectors = [
        'div[data-testid="marketplace-item"]',
        'a[href*="/marketplace/item/"]',
        'div[role="article"]'
    ]
    
    for selector in marketplace_selectors:
        elements = soup.select(selector)
        print(f"🎯 Selector '{selector}': {len(elements)} elements found")
    
    print("🔍 === PAGE CONTENT ANALYSIS END ===")
    
    return {
        "title": page_title,
        "url": current_url,
        "html_length": html_length,
        "detection_indicators": found_indicators,
        "marketplace_indicators": found_marketplace,
        "body_text_length": len(body_text) if body else 0
    }

# Enhanced scraping endpoint with debugging
@app.post("/scrape")
def scrape_marketplace(city: str, query: str, max_price: int):
    """VPS scraping endpoint with HTML content analysis"""
    
    try:
        print(f"🚀 DEBUG VPS Scraper: Starting scrape for {city}, query: '{query}', max_price: ${max_price}")
        
        # Enhanced anti-detection
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
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
            )
            
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="en-US",
                timezone_id="America/New_York",
                geolocation={"longitude": -74.0059, "latitude": 40.7128},
                permissions=["geolocation"]
            )
            
            page = context.new_page()
            
            # Enhanced anti-detection script injection
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                };
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
            """)
            
            # Get city slug for URL
            cities = {
                'New York': 'nyc', 'Los Angeles': 'la', 'Las Vegas': 'vegas',
                'Chicago': 'chicago', 'Houston': 'houston', 'Boston': 'boston',
                'Miami': 'miami', 'Orlando': 'orlando', 'San Diego': 'sandiego'
            }
            
            city_slug = cities.get(city, city.lower().replace(' ', ''))
            marketplace_url = f'https://www.facebook.com/marketplace/{city_slug}/search/?query={query}&maxPrice={max_price}'
            
            print(f"🌐 DEBUG: Navigating to: {marketplace_url}")
            page.goto(marketplace_url)
            
            # Wait for page load
            print("⏱️ DEBUG: Waiting for page load...")
            time.sleep(5)
            
            # Enhanced popup dismissal
            dismiss_popups(page)
            
            # ANALYZE PAGE CONTENT - This is the key debugging addition
            page_analysis = analyze_page_content(page, city, query)
            
            # Try to parse listings with debug info
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            results = parse_marketplace_listings_debug(soup, city, query)
            
            browser.close()
            
        print(f"✅ DEBUG VPS Scraper: Found {len(results)} listings")
        
        return {
            "success": True, 
            "listings_found": len(results), 
            "data": results,
            "debug_info": page_analysis  # Include debug analysis in response
        }
        
    except Exception as e:
        print(f"❌ DEBUG VPS Scraper failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def dismiss_popups(page):
    """Enhanced popup dismissal for VPS"""
    max_attempts = 3
    
    for attempt in range(max_attempts):
        try:
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
                    page.locator(selector).first.click()
                    popup_found = True
                    time.sleep(2)
                    break
            
            if not popup_found:
                if page.locator('div[role="dialog"]').count() > 0:
                    page.keyboard.press('Escape')
                    time.sleep(2)
                else:
                    break
                    
        except Exception as e:
            print(f"Popup dismissal error: {e}")
            time.sleep(1)

def parse_marketplace_listings_debug(soup, city, query):
    """Parse listings with enhanced debugging"""
    
    print("🔍 === LISTING PARSING DEBUG START ===")
    
    # Try multiple CSS selectors with debug output
    listing_selectors = [
        'div[data-testid="marketplace-item"]',
        'div.x9f619.x78zum5.x1r8uery.xdt5ytf.x1iyjqo2.xs83m0k.x1e558r4.x150jy0e.x1iorvi4.xjkvuk6.xnpuxes.x291uyu.x1uepa24',
        'div[role="article"]',
        'a[href*="/marketplace/item/"]'
    ]
    
    listings = []
    for selector in listing_selectors:
        elements = soup.select(selector)
        print(f"🎯 DEBUG: Selector '{selector}' found {len(elements)} elements")
        if elements:
            listings = elements
            print(f"✅ Using selector: {selector}")
            break
    
    if not listings:
        print("❌ No listings found with any selector")
        
        # Try generic marketplace search
        all_divs = soup.find_all('div')
        marketplace_divs = [div for div in all_divs if 'marketplace' in str(div).lower()]
        print(f"🔍 Found {len(marketplace_divs)} divs mentioning 'marketplace'")
        
        # Check for common Facebook elements
        common_selectors = ['div', 'span', 'a', 'article']
        for sel in common_selectors:
            count = len(soup.select(sel))
            print(f"📊 Total {sel} elements: {count}")
    
    parsed = []
    for i, listing in enumerate(listings[:3]):  # Only process first 3 for debugging
        print(f"🔍 Processing listing {i+1}/{min(3, len(listings))}")
        try:
            # Debug listing content
            listing_text = listing.get_text(strip=True)[:100]
            print(f"📄 Listing {i+1} text snippet: {listing_text}...")
            
            # Try to extract data with debug output
            post_url = extract_post_url(listing)
            print(f"🔗 URL: {post_url}")
            
            if post_url:
                title = extract_title(listing)
                price = extract_price(listing)
                location = extract_location(listing)
                image = extract_image(listing)
                
                print(f"📝 Title: {title}")
                print(f"💰 Price: {price}")
                print(f"📍 Location: {location}")
                print(f"🖼️ Image: {image[:50]}...")
                
                listing_data = {
                    "title": title,
                    "price": price, 
                    "location": location,
                    "image": image,
                    "post_url": post_url,
                    "city": city,
                    "search_query": query
                }
                
                save_listing(listing_data)
                
                parsed.append({
                    "name": title,
                    "price": price,
                    "location": location,
                    "title": title,
                    "image": image,
                    "link": post_url.replace('https://www.facebook.com', '')
                })
                
        except Exception as e:
            print(f"❌ Error parsing listing {i+1}: {e}")
    
    print(f"✅ Successfully parsed {len(parsed)} listings")
    print("🔍 === LISTING PARSING DEBUG END ===")
    
    return parsed

# Extract functions (same as original)
def extract_post_url(listing):
    if listing.name == 'a' and listing.get('href') and '/marketplace/item/' in str(listing.get('href')):
        href_val = listing.get('href')
        if isinstance(href_val, str):
            return 'https://www.facebook.com' + href_val
    
    link_elements = listing.find_all('a')
    for link in link_elements:
        href_val = link.get('href')
        if href_val and isinstance(href_val, str) and '/marketplace/item/' in href_val:
            return 'https://www.facebook.com' + href_val
    return None

def extract_image(listing):
    img_element = listing.find('img')
    if img_element and hasattr(img_element, 'get'):
        src_val = img_element.get('src')
        if src_val and isinstance(src_val, str):
            return src_val
    return "No image found"

def extract_title(listing):
    all_spans = listing.find_all('span')
    for span in all_spans:
        if span.get_text(strip=True):
            span_text = span.get_text(strip=True)
            if (len(span_text) > 5 and 
                not span_text.startswith('$') and 
                len(span_text) < 200):
                return span_text
    return "No title found"

def extract_price(listing):
    all_text_elements = listing.find_all(string=True)
    for text_elem in all_text_elements:
        if text_elem and hasattr(text_elem, 'strip'):
            text_clean = text_elem.strip()
            if text_clean.startswith('$') and len(text_clean) > 1:
                return text_clean
    return "Price not found"

def extract_location(listing):
    all_text_elements = listing.find_all(string=True)
    location_keywords = ['miles away', 'mi away', 'km away']
    
    for text_elem in all_text_elements:
        if text_elem and hasattr(text_elem, 'strip'):
            text_clean = text_elem.strip()
            if any(keyword in text_clean.lower() for keyword in location_keywords):
                return text_clean
    return "Location not found"

# Legacy endpoint for backward compatibility
@app.get("/crawl_facebook_marketplace")
def crawl_facebook_marketplace(city: str, query: str, max_price: int):
    """Legacy endpoint - calls new debug scrape function"""
    try:
        result = scrape_marketplace(city, query, max_price)
        return result["data"]  # Return just the listings array for compatibility
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # VPS-optimized server configuration
    uvicorn.run(
        'app_debug:app',
        host='0.0.0.0',
        port=8000,
        reload=False,
        access_log=True,
        log_level="info"
    ) 
