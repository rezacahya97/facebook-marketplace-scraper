# Description: This file contains the code for Passivebot's Facebook Marketplace Scraper API.
# Date: 2024-01-24
# Author: Harminder Nijjar
# Version: 2.0.0 - VPS Deployment (Strategy A)
# Usage: python app.py

# Import the necessary libraries.
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

# Create an instance of the FastAPI class.
app = FastAPI(
    title="Facebook Marketplace Scraper API",
    description="VPS-optimized scraper with enhanced anti-detection",
    version="2.0.0"
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
def scrape_marketplace(city: str, query: str, max_price: int):
    """VPS scraping endpoint triggered by Supabase"""
    
    try:
        print(f"🚀 VPS Scraper: Starting scrape for {city}, query: '{query}', max_price: ${max_price}")
        
        # Enhanced anti-detection (VPS-optimized)
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
                    '--disable-images',  # Faster loading on VPS
                    '--no-first-run',
                    '--no-default-browser-check',
                ]
            )
            
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="en-US",
                timezone_id="America/New_York",
                geolocation={"longitude": -74.0059, "latitude": 40.7128},  # NYC coordinates
                permissions=["geolocation"]
            )
            
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
            
            # Call existing scraping logic
            results = scrape_facebook_marketplace_logic(page, city, query, max_price)
            
            browser.close()
            
        print(f"✅ VPS Scraper: Found {len(results)} listings")
        return {"success": True, "listings_found": len(results), "data": results}
        
    except Exception as e:
        print(f"❌ VPS Scraper failed: {str(e)}")
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
    
    print(f"🌐 Navigating to: {marketplace_url}")
    page.goto(marketplace_url)
    
    # Wait for page load
    time.sleep(5)
    
    # Enhanced popup dismissal strategy
    dismiss_popups(page)
    
    # Get page content
    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')
    
    # Parse listings using existing logic
    return parse_marketplace_listings(soup, city, query)

def dismiss_popups(page):
    """Enhanced popup dismissal for VPS"""
    max_attempts = 3
    
    for attempt in range(max_attempts):
        try:
            # Multiple close button selectors
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
                # Try ESC key
                if page.locator('div[role="dialog"]').count() > 0:
                    page.keyboard.press('Escape')
                    time.sleep(2)
                else:
                    break  # No popup detected
                    
        except Exception as e:
            print(f"Popup dismissal error: {e}")
            time.sleep(1)

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
