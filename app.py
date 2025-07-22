# Description: This file contains the code for Passivebot's Facebook Marketplace Scraper API.
# Date: 2024-01-24
# Author: Harminder Nijjar
# Version: 2.0.0 - VPS Deployment (Strategy A)
# Usage: python app.py

# Import the necessary libraries.
from playwright.sync_api import sync_playwright
import os
import time
import random
import json
import pickle
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from database import save_listing
from datetime import datetime

# Phase 1: Simple Cookie & Proxy Management
def save_cookies_simple(page, session_name="default"):
    """Save cookies for session persistence"""
    try:
        cookies_dir = Path("cookies")
        cookies_dir.mkdir(exist_ok=True)
        cookies = page.context.cookies()
        if cookies:
            with open(cookies_dir / f"{session_name}.pkl", 'wb') as f:
                pickle.dump(cookies, f)
            print(f"🍪 Saved {len(cookies)} cookies")
            return True
    except Exception as e:
        print(f"❌ Cookie save failed: {e}")
    return False

def load_cookies_simple(context, session_name="default"):
    """Load cookies for session persistence"""
    try:
        cookie_file = Path("cookies") / f"{session_name}.pkl"
        if cookie_file.exists():
            with open(cookie_file, 'rb') as f:
                cookies = pickle.load(f)
            context.add_cookies(cookies)
            print(f"🍪 Loaded {len(cookies)} cookies")
            return True
    except Exception as e:
        print(f"❌ Cookie load failed: {e}")
    return False

def get_free_proxy():
    """Get a free proxy for testing"""
    try:
        # Simple free proxy list (these change frequently)
        proxy_list = [
            "47.74.152.29:8888",
            "103.149.162.194:80", 
            "20.206.106.192:80"
        ]
        proxy = random.choice(proxy_list)
        print(f"🌐 Using proxy: {proxy}")
        return {"server": f"http://{proxy}"}
    except Exception as e:
        print(f"❌ Proxy failed: {e}")
    return None

def get_random_user_agent():
    """Get random user agent for better stealth"""
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    return random.choice(agents)

# Create an instance of the FastAPI class.
app = FastAPI(
    title="Facebook Marketplace Scraper API - Phase 1 Enhanced",
    description="VPS scraper with cookies, proxies, and randomization",
    version="2.1.0-phase1"
)

# Configure CORS for VPS deployment
origins = [
    "https://*",  # Allow all HTTPS origins for VPS
    "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # More permissive for VPS
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Health check endpoint for VPS monitoring
@app.get("/health")
def health_check():
    """VPS health check endpoint"""
    return {
        "status": "healthy",
        "service": "Facebook Marketplace Scraper",
        "strategy": "VPS + Cron (Strategy A)",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Facebook Marketplace Scraper API - VPS Deployment",
        "strategy": "Strategy A: VPS + Cron",
        "version": "2.0.0",
        "endpoints": {
            "health": "/health",
            "scrape": "/scrape",
            "crawl": "/crawl_facebook_marketplace",
            "ip": "/return_ip_information"
        }
    }

# New VPS-optimized scraping endpoint
@app.post("/scrape")
def scrape_marketplace(city: str, query: str, max_price: int, 
                      use_cookies: bool = True, use_proxy: bool = True):
    """Phase 1 enhanced scraping with cookies and proxies"""
    
    try:
        print(f"🚀 PHASE 1 Scraper: Starting enhanced scrape")
        print(f"📍 {city}, '{query}', ${max_price}")
        print(f"🍪 Cookies: {use_cookies}, 🌐 Proxy: {use_proxy}")
        
        # Phase 1: Get proxy if enabled
        proxy_config = None
        if use_proxy:
            proxy_config = get_free_proxy()
        
        # Enhanced anti-detection with Phase 1 features
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                proxy=proxy_config,  # Phase 1: Proxy support
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
            
            # Phase 1: Enhanced context with randomization
            context = browser.new_context(
                viewport={
                    "width": random.randint(1366, 1920), 
                    "height": random.randint(768, 1080)
                },
                user_agent=get_random_user_agent(),  # Phase 1: Random user agent
                locale="en-US",
                timezone_id=random.choice([
                    "America/New_York", "America/Chicago", "America/Los_Angeles"
                ]),
                geolocation={"longitude": -74.0059, "latitude": 40.7128},
                permissions=["geolocation"]
            )
            
            # Phase 1: Load cookies if enabled
            cookies_loaded = False
            if use_cookies:
                cookies_loaded = load_cookies_simple(context)
            
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
                
                // Mock plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                // Mock permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                    Promise.resolve({ state: Deno.PermissionState.granted }) :
                    originalQuery(parameters)
                );
            """)
            
            # Call enhanced scraping logic
            results = scrape_facebook_marketplace_logic(page, city, query, max_price)
            
            # Phase 1: Save cookies if we successfully scraped and cookies are enabled
            if use_cookies and not cookies_loaded and len(results) > 0:
                save_cookies_simple(page, f"auto_{datetime.now().strftime('%Y%m%d_%H%M')}")
            
            browser.close()
            
        print(f"✅ PHASE 1 Scraper: Found {len(results)} listings")
        phase1_info = {
            "cookies_used": use_cookies and cookies_loaded,
            "proxy_used": use_proxy and proxy_config is not None,
            "proxy_server": proxy_config.get('server') if proxy_config else None,
            "enhancements_active": True
        }
        return {"success": True, "listings_found": len(results), "data": results, "phase1_info": phase1_info}
        
    except Exception as e:
        print(f"❌ PHASE 1 Scraper failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def scrape_facebook_marketplace_logic(page, city, query, max_price):
    """Extracted scraping logic for reuse"""
    
    # Define dictionary of cities
    cities = {
        'New York': 'nyc',
        'Los Angeles': 'la',
        'Las Vegas': 'vegas',
        'Chicago': 'chicago',
        'Houston': 'houston',
        'San Antonio': 'sanantonio',
        'Miami': 'miami',
        'Orlando': 'orlando',
        'San Diego': 'sandiego',
        'Arlington': 'arlington',
        'Balitmore': 'baltimore',
        'Cincinnati': 'cincinnati',
        'Denver': 'denver',
        'Fort Worth': 'fortworth',
        'Jacksonville': 'jacksonville',
        'Memphis': 'memphis',
        'Nashville': 'nashville',
        'Philadelphia': 'philly',
        'Portland': 'portland',
        'San Jose': 'sanjose',
        'Tucson': 'tucson',
        'Atlanta': 'atlanta',
        'Boston': 'boston',
        'Columnbus': 'columbus',
        'Detroit': 'detroit',
        'Honolulu': 'honolulu',
        'Kansas City': 'kansascity',
        'New Orleans': 'neworleans',
        'Phoenix': 'phoenix',
        'Seattle': 'seattle',
        'Washington DC': 'dc',
        'Milwaukee': 'milwaukee',
        'Sacremento': 'sac',
        'Austin': 'austin',
        'Charlotte': 'charlotte',
        'Dallas': 'dallas',
        'El Paso': 'elpaso',
        'Indianapolis': 'indianapolis',
        'Louisville': 'louisville',
        'Minneapolis': 'minneapolis',
        'Oaklahoma City' : 'oklahoma',
        'Pittsburgh': 'pittsburgh',
        'San Francisco': 'sanfrancisco',
        'Tampa': 'tampa'
    }
    
    # Convert city name to URL slug
    if city in cities:
        city_slug = cities[city]
    else:
        city_slug = city.lower().replace(' ', '')
    
    # Build marketplace URL
    marketplace_url = f'https://www.facebook.com/marketplace/{city_slug}/search/?query={query}&maxPrice={max_price}'
    
    print(f"🌐 Enhanced Navigation to: {marketplace_url}")
    page.goto(marketplace_url)
    
    # Phase 1: Randomized wait instead of static 5 seconds
    wait_time = random.uniform(3, 7)
    print(f"⏱️ Random wait: {wait_time:.1f}s")
    time.sleep(wait_time)
    
    # Enhanced popup dismissal strategy
    dismiss_popups(page)
    
    # Get page content
    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')
    
    # Parse listings using existing logic
    return parse_marketplace_listings(soup, city, query)

def dismiss_popups(page):
    """Phase 1 enhanced popup dismissal with randomization"""
    max_attempts = random.randint(2, 4)  # Phase 1: Randomize attempts
    
    for attempt in range(max_attempts):
        try:
            # Phase 1: Random small delay before each attempt
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
                    page.locator(selector).first.click()
                    popup_found = True
                    time.sleep(random.uniform(1, 2.5))  # Phase 1: Random timing
                    break
            
            if not popup_found:
                if page.locator('div[role="dialog"]').count() > 0:
                    page.keyboard.press('Escape')
                    time.sleep(random.uniform(1, 2))  # Phase 1: Random timing
                else:
                    break
                    
        except Exception as e:
            print(f"Popup dismissal error: {e}")
            time.sleep(random.uniform(0.5, 1))  # Phase 1: Random error delay

def parse_marketplace_listings(soup, city, query):
    """Parse listings from HTML using existing selectors"""
    parsed = []
    
    # Try multiple CSS selectors for marketplace listings
    listing_selectors = [
        'div[data-testid="marketplace-item"]',
        'div.x9f619.x78zum5.x1r8uery.xdt5ytf.x1iyjqo2.xs83m0k.x1e558r4.x150jy0e.x1iorvi4.xjkvuk6.xnpuxes.x291uyu.x1uepa24',
        'div[role="article"]',
        'a[href*="/marketplace/item/"]'
    ]
    
    listings = []
    for selector in listing_selectors:
        listings = soup.select(selector)
        if listings:
            break
    
    for listing in listings:
        try:
            # Extract listing data
            post_url = extract_post_url(listing)
            if not post_url:
                continue
                
            image = extract_image(listing)
            title = extract_title(listing)
            price = extract_price(listing)
            location = extract_location(listing)
            
            # Create listing object
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
            
        except Exception as e:
            print(f"Error parsing listing: {e}")
            continue
    
    return parsed

def extract_post_url(listing):
    """Extract post URL from listing"""
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
    """Extract image URL from listing"""
    img_element = listing.find('img')
    if img_element and hasattr(img_element, 'get'):
        src_val = img_element.get('src')
        if src_val and isinstance(src_val, str):
            return src_val
    return "No image found"

def extract_title(listing):
    """Extract title from listing"""
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
    """Extract price from listing"""
    all_text_elements = listing.find_all(string=True)
    for text_elem in all_text_elements:
        if text_elem and hasattr(text_elem, 'strip'):
            text_clean = text_elem.strip()
            if text_clean.startswith('$') and len(text_clean) > 1:
                return text_clean
    return "Price not found"

def extract_location(listing):
    """Extract location from listing"""
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
    """Legacy endpoint - calls new scrape function"""
    try:
        result = scrape_marketplace(city, query, max_price)
        return result["data"]  # Return just the listings array for compatibility
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create a route to the return_html endpoint.
@app.get("/return_ip_information")
# Define a function to be executed when the endpoint is called.
def return_ip_information():
    # Initialize the session using Playwright.
    with sync_playwright() as p:
        # Open a new browser page.
        browser = p.chromium.launch()
        page = browser.new_page()
        # Navigate to the URL.
        page.goto('https://www.ipburger.com/')
        # Wait for the page to load.
        time.sleep(5)
        # Get the HTML content of the page.
        html = page.content()
        # Beautify the HTML content.
        soup = BeautifulSoup(html, 'html.parser')
        # Find the IP address.
        ip_elem = soup.find('span', id='ipaddress1')
        ip_address = ip_elem.text if ip_elem else "Unknown"
        # Find the country.
        country_elem = soup.find('strong', id='country_fullname')
        country = country_elem.text if country_elem else "Unknown"
        # Find the location.
        location_elem = soup.find('strong', id='location')
        location = location_elem.text if location_elem else "Unknown"
        # Find the ISP.
        isp_elem = soup.find('strong', id='isp')
        isp = isp_elem.text if isp_elem else "Unknown"
        # Find the Hostname.
        hostname_elem = soup.find('strong', id='hostname')
        hostname = hostname_elem.text if hostname_elem else "Unknown"
        # Find the Type.
        ip_type_elem = soup.find('strong', id='ip_type')
        ip_type = ip_type_elem.text if ip_type_elem else "Unknown"
        # Find the version.
        version_elem = soup.find('strong', id='version')
        version = version_elem.text if version_elem else "Unknown"
        # Close the browser.
        browser.close()
        # Return the IP information as JSON.
        return {
            'ip_address': ip_address,
            'country': country,
            'location': location,
            'isp': isp,
            'hostname': hostname,
            'type': ip_type,
            'version': version
        }

if __name__ == "__main__":
    # VPS-optimized server configuration
    uvicorn.run(
        'app:app',
        host='0.0.0.0',  # VPS needs 0.0.0.0 for external access
        port=8000,
        reload=False,  # Disable reload for production
        access_log=True,
        log_level="info"
    )
