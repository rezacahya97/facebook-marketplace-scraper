# Description: This file contains the code for Passivebot's Facebook Marketplace Scraper API.
# Date: 2024-01-24
# Author: Harminder Nijjar
# Version: 1.0.0.
# Usage: python app.py


# Import the necessary libraries.
# Playwright is used to crawl the Facebook Marketplace.
from playwright.sync_api import sync_playwright
# The os library is used to get the environment variables.
import os
# The time library is used to add a delay to the script.
import time
# The BeautifulSoup library is used to parse the HTML.
from bs4 import BeautifulSoup
# The FastAPI library is used to create the API.
from fastapi import HTTPException, FastAPI
# The JSON library is used to convert the data to JSON.
import json
# The uvicorn library is used to run the API.
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
# Import database functions for storing listings
from database import save_listing
                 
# Create an instance of the FastAPI class.
app = FastAPI()
# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# Create a route to the root endpoint.
@app.get("/")
# Define a function to be executed when the endpoint is called.
def root():
    # Return a message.
    return {"message": "Welcome to Passivebot's Facebook Marketplace API. Documentation is currently being worked on along with the API. Some planned features currently in the pipeline are a ReactJS frontend, MongoDB database, and Google Authentication."}

    # TODO - Add documentation to the API.
    # TODO - Add a React frontend to the API.
    # TODO - Add a MongoDB database to the API.
    # TODO - Add Google Authentication to the React frontend.

# Create a route to the return_data endpoint.
@app.get("/crawl_facebook_marketplace")
# Define a function to be executed when the endpoint is called.
# Add a description to the function.
def crawl_facebook_marketplace(city: str, query: str, max_price: int):
    # Define dictionary of cities from the facebook marketplace directory for United States.
    # https://m.facebook.com/marketplace/directory/US/?_se_imp=0oey5sMRMSl7wluQZ
    # TODO - Add more cities to the dictionary.
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
    # If the city is in the cities dictionary...
    if city in cities:
        # Get the city location id from the cities dictionary.
        city = cities[city]
    # If the city is not in the cities dictionary...
    else:
        # Exit the script if the city is not in the cities dictionary.
        # Capitalize only the first letter of the city.
        city = city.capitalize()
        # Raise an HTTPException.
        raise HTTPException (404, f'{city} is not a city we are currently supporting on the Facebook Marketplace. Please reach out to us to add this city in our directory.')
        # TODO - Try and find a way to get city location ids from Facebook if the city is not in the cities dictionary.
        
    # Define the URL to scrape.
    marketplace_url = f'https://www.facebook.com/marketplace/{city}/search/?query={query}&maxPrice={max_price}'
    initial_url = "https://www.facebook.com/login/device-based/regular/login/"
    # Get listings of particular item in a particular city for a particular price.
    # Initialize the session using Playwright.
    with sync_playwright() as p:
        # Open a new browser page.
        # Configure browser for Railway production environment
        is_production = os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('PORT')
        
        # Strategy 1.1: Realistic Browser Configuration
        # Set realistic Chrome User-Agent (current version)
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        # =================================================================
        # STRATEGY 1.3: SESSION & COOKIE MANAGEMENT  
        # =================================================================
        # Create persistent browser context to simulate real user session
        
        print("DEBUG: Strategy 1.3 - Creating persistent browser context")
        
        if is_production:
            # Railway/containerized environment configuration
            browser = p.chromium.launch(
                headless=True,
                args=[
                    # Security flags (required for Railway)
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    
                    # Anti-detection flags (make browser look real)
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-field-trial-config',
                    '--disable-ipc-flooding-protection',
                    '--no-first-run',
                    '--no-default-browser-check',
                    '--no-pings',
                    '--password-store=basic',
                    '--use-mock-keychain',
                    
                    # Window and display settings
                    '--window-size=1920,1080',
                    '--start-maximized',
                    
                    # User agent
                    f'--user-agent={user_agent}'
                ]
            )
        else:
            # Local development configuration  
            browser = p.chromium.launch(headless=False)
            
        # Strategy 1.3: Create browser context with persistent session
        print("DEBUG: Creating browser context with session persistence")
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=user_agent,
            # Accept language and timezone for realism
            locale="en-US",
            timezone_id="America/New_York",
            # Geolocation (optional - makes it more realistic)
            permissions=["geolocation"],
            geolocation={"latitude": 40.7128, "longitude": -74.0060},  # NYC coordinates
            # Extra HTTP headers for realism
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
            }
        )
        
        # Create page from context (inherits all settings)
        page = context.new_page()
        
        print("DEBUG: Strategy 1.3 context created with realistic settings")
        
        # Remove webdriver property (anti-detection)
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Add realistic navigator properties
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5], // Fake some plugins
            });
            
            // Hide automation indicators
            Object.defineProperty(navigator, 'permissions', {
                get: () => ({
                    query: () => Promise.resolve({ state: 'granted' })
                }),
            });
        """)
        
        # =================================================================
        # STRATEGY 1.3: SESSION SIMULATION & BROWSING HISTORY
        # =================================================================
        # Simulate real user browsing session before accessing marketplace
        
        import random  # Import random for human-like delays
        print("DEBUG: Strategy 1.3 - Starting session simulation")
        
        # Step 1: Build browsing history by visiting related sites first
        print("DEBUG: Step 1 - Building realistic browsing history")
        
        # Visit a news site first (common user behavior)
        print("DEBUG: Visiting news site to build session history")
        page.goto("https://www.cnn.com")
        time.sleep(random.uniform(2.0, 4.0))
        
        # Add some scrolling and interaction
        page.mouse.move(500, 300)
        page.mouse.wheel(0, 200)
        time.sleep(random.uniform(1.0, 2.0))
        
        # Step 2: Visit Facebook homepage (normal user flow)
        print("DEBUG: Step 2 - Navigating to Facebook homepage")
        page.goto("https://www.facebook.com")
        time.sleep(random.uniform(3.0, 5.0))
        
        # Check and save cookies after Facebook homepage
        cookies = context.cookies()
        print(f"DEBUG: Collected {len(cookies)} cookies from Facebook homepage")
        
        # Simulate some browsing on Facebook homepage
        print("DEBUG: Simulating Facebook homepage interaction")
        page.mouse.move(400, 200)
        time.sleep(random.uniform(1.0, 2.0))
        page.mouse.wheel(0, 300)
        time.sleep(random.uniform(2.0, 3.0))
        
        # Step 3: Add local storage and session storage (realistic browser state)
        page.evaluate("""
            // Add realistic localStorage data
            localStorage.setItem('fb_last_visit', Date.now().toString());
            localStorage.setItem('fb_user_preferences', '{"theme":"default","locale":"en_US"}');
            
            // Add realistic sessionStorage  
            sessionStorage.setItem('fb_session_id', Math.random().toString(36));
            sessionStorage.setItem('fb_page_loads', '3');
        """)
        
        print("DEBUG: Added realistic localStorage and sessionStorage data")
        
        # Step 4: Check current page state before marketplace navigation
        current_url = page.url
        current_title = page.title()
        
        print(f"DEBUG: Pre-marketplace session state:")
        print(f"DEBUG: Current URL: {current_url}")
        print(f"DEBUG: Current title: {current_title}")
        print(f"DEBUG: Cookies count: {len(context.cookies())}")
        
        print(f"DEBUG: Strategy 1.3 session setup complete")
        print(f"DEBUG: User-Agent: {user_agent}")
        print(f"DEBUG: Viewport: 1920x1080")
        print(f"DEBUG: Geolocation: NYC coordinates")
        print(f"DEBUG: Locale: en-US, Timezone: America/New_York")
        
        # =================================================================
        # STRATEGY 1.2: HUMAN-LIKE BEHAVIOR PATTERNS
        # =================================================================
        # Instead of going directly to marketplace (bot-like), simulate real human browsing
        
        print("DEBUG: Strategy 1.2 - Starting human-like navigation pattern")
        
        # Step 1: Visit Facebook homepage first (like a real user)
        print("DEBUG: Step 1 - Visiting Facebook homepage first")
        page.goto("https://www.facebook.com")
        
        # Human-like delay after homepage load  
        delay = random.uniform(2.0, 4.0)
        print(f"DEBUG: Human-like delay: {delay:.2f} seconds")
        time.sleep(delay)
        
        # Step 2: Simulate human cursor movement on homepage
        print("DEBUG: Step 2 - Simulating human mouse movements")
        # Move mouse to different areas of the page (like reading/browsing)
        page.mouse.move(300, 200)  # Move to top area
        time.sleep(random.uniform(0.5, 1.0))
        page.mouse.move(600, 400)  # Move to center
        time.sleep(random.uniform(0.5, 1.0))
        page.mouse.move(900, 600)  # Move to different area
        time.sleep(random.uniform(0.5, 1.0))
        
        # Step 3: Scroll down like a human browsing the page
        print("DEBUG: Step 3 - Human-like scrolling behavior")
        page.mouse.wheel(0, 300)  # Scroll down a bit
        time.sleep(random.uniform(1.0, 2.0))
        page.mouse.wheel(0, -150)  # Scroll back up (human-like)
        time.sleep(random.uniform(1.0, 2.0))
        
        # Step 4: Now navigate to marketplace (more natural progression)
        print(f"DEBUG: Step 4 - Now navigating to marketplace: {marketplace_url}")
        page.goto(marketplace_url)
        
        # Step 5: Human-like wait and interaction on marketplace page
        print("DEBUG: Step 5 - Human-like behavior on marketplace page")
        # Longer initial wait (humans need time to read/process)
        initial_delay = random.uniform(3.0, 6.0)
        print(f"DEBUG: Initial marketplace load delay: {initial_delay:.2f} seconds")
        time.sleep(initial_delay)
        
        # Simulate human reading/browsing the marketplace page
        print("DEBUG: Simulating human browsing patterns on marketplace")
        page.mouse.move(400, 300)  # Look at search area
        time.sleep(random.uniform(1.0, 2.0))
        
        # Scroll down to see listings (like a human would)
        print("DEBUG: Scrolling to view listings (human-like)")
        page.mouse.wheel(0, 400)  # Scroll to see more listings
        time.sleep(random.uniform(2.0, 3.0))
        
        # Additional small movements (humans rarely stay perfectly still)
        page.mouse.move(600, 500)
        time.sleep(random.uniform(1.0, 2.0))
        
        print("DEBUG: Strategy 1.2 complete - human-like behavior simulation finished")
        
        # =================================================================
        # STRATEGY 1.2: RESULTS TRACKING & VALIDATION
        # =================================================================
        # Check if human-like behavior bypassed Facebook's bot detection
        
        print("DEBUG: Checking Strategy 1.2 results...")
        current_url = page.url
        current_title = page.title()
        
        print(f"DEBUG: Final page URL: {current_url}")
        print(f"DEBUG: Final page title: {current_title}")
        
        # Check if we successfully reached marketplace vs login redirect
        if "login" in current_url.lower():
            print("❌ STRATEGY 1.2 FAILED: Still redirected to login page")
            print("DEBUG: Facebook still detecting automation despite human-like behavior")
        elif "marketplace" in current_url.lower():
            print("✅ STRATEGY 1.2 SUCCESS: Reached marketplace page!")
            print("DEBUG: Human-like behavior bypassed bot detection")
        else:
            print("⚠️ STRATEGY 1.2 UNKNOWN: Unexpected page reached")
            print(f"DEBUG: Investigating unexpected URL: {current_url}")
        
        # Additional marketplace validation
        html_sample = page.content()[:500]  # First 500 chars for debugging
        if "marketplace" in html_sample.lower():
            print("✅ HTML VALIDATION: Marketplace content detected in page source")
        elif "login" in html_sample.lower():
            print("❌ HTML VALIDATION: Login content detected in page source")
        else:
            print("⚠️ HTML VALIDATION: Unknown content type")
        
        print("DEBUG: Strategy 1.2 validation complete, proceeding with popup dismissal...")
        
        # POPUP DISMISSAL STRATEGY - Auto-dismiss "See more on Facebook" popup
        popup_dismissed = False
        max_attempts = 3
        
        for attempt in range(max_attempts):
            print(f"DEBUG: Popup dismissal attempt {attempt + 1}/{max_attempts}")
            
            try:
                # Method 1: Look for close button with various selectors
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
                        print(f"DEBUG: Found close button with selector: {selector}")
                        page.locator(selector).first.click()
                        popup_found = True
                        popup_dismissed = True
                        print("DEBUG: Successfully clicked close button")
                        time.sleep(2)  # Wait for popup animation
                        break
                
                if not popup_found:
                    # Method 2: Check for popup dialog and try ESC key
                    if page.locator('div[role="dialog"]').count() > 0:
                        print("DEBUG: Found dialog, trying ESC key")
                        page.keyboard.press('Escape')
                        popup_dismissed = True
                        time.sleep(2)
                    else:
                        # Method 3: Look for "See more on Facebook" text and dismiss
                        if page.locator('text="See more on Facebook"').count() > 0:
                            print("DEBUG: Found 'See more on Facebook' text")
                            # Try clicking outside the popup (backdrop click)
                            page.mouse.click(100, 100)  # Click top-left corner
                            popup_dismissed = True
                            time.sleep(2)
                        else:
                            print("DEBUG: No popup detected")
                            popup_dismissed = True  # Assume no popup present
                            break
                
                # Verify popup dismissal
                if page.locator('div[role="dialog"]').count() == 0:
                    print("DEBUG: Popup successfully dismissed")
                    break
                else:
                    print("DEBUG: Popup still present, retrying...")
                    time.sleep(1)
                    
            except Exception as e:
                print(f"DEBUG: Popup dismissal error: {e}")
                time.sleep(1)
        
        if not popup_dismissed:
            print("DEBUG: WARNING - Could not dismiss popup, proceeding anyway...")
        
        # Additional wait after popup dismissal
        time.sleep(2)
        
        # DEBUG: Save page content to see what we're getting
        html = page.content()
        print(f"DEBUG: Page title: {page.title()}")
        print(f"DEBUG: Page URL: {page.url}")
        print(f"DEBUG: HTML length: {len(html)}")
        
        soup = BeautifulSoup(html, 'html.parser')
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
            print(f"DEBUG: Selector '{selector}' found {len(listings)} elements")
            if listings:
                break
        
        if not listings:
            print("DEBUG: No listings found with any selector, trying generic approach")
            # Try to find any marketplace-related elements
            all_divs = soup.find_all('div')
            marketplace_divs = [div for div in all_divs if 'marketplace' in str(div).lower()]
            print(f"DEBUG: Found {len(marketplace_divs)} divs mentioning 'marketplace'")
        
        for listing in listings:
            try:
                # Get the item URL (this is our listing element)
                post_url = None
                listing_container = None
                
                if listing.name == 'a' and listing.get('href') and '/marketplace/item/' in str(listing.get('href')):
                    href_val = listing.get('href')
                    if isinstance(href_val, str):
                        post_url = 'https://www.facebook.com' + href_val
                        listing_container = listing.parent
                else:
                    # If listing is not the link itself, find the link within it
                    link_elements = listing.find_all('a')
                    for link in link_elements:
                        href_val = link.get('href')
                        if href_val and isinstance(href_val, str) and '/marketplace/item/' in href_val:
                            post_url = 'https://www.facebook.com' + href_val
                            listing_container = listing
                            break
                
                if not post_url or not listing_container:
                    continue

                # Get the item image - try multiple strategies
                image = "No image found"
                img_element = listing_container.find('img')
                if img_element:
                    try:
                        src_val = img_element.get('src')
                        if src_val and isinstance(src_val, str):
                            image = src_val
                    except (AttributeError, TypeError):
                        pass

                # Get the item title - look for text in various span elements
                title = "No title found"
                
                # Find all text-containing elements
                all_spans = listing_container.find_all('span')
                for span in all_spans:
                    if span.get_text(strip=True):
                        span_text = span.get_text(strip=True)
                        # Check if this could be a title (not a price, reasonable length)
                        if (len(span_text) > 5 and 
                            not span_text.startswith('$') and 
                            len(span_text) < 200):
                            title = span_text
                            break

                # Get the item price - look for text starting with $
                price = "Price not found"
                
                # Look through all text for price patterns
                all_text_elements = listing_container.find_all(string=True)
                for text_elem in all_text_elements:
                    if text_elem and hasattr(text_elem, 'strip'):
                        text_clean = text_elem.strip()
                        if text_clean.startswith('$') and len(text_clean) > 1:
                            price = text_clean
                            break

                # Get the item location - usually appears near the bottom
                location = "Location not found"
                
                # Look for location-like text in spans
                for span in all_spans:
                    if span.get_text(strip=True):
                        span_text = span.get_text(strip=True)
                        # Skip if it's the title or price we already found
                        if span_text == title or span_text == price:
                            continue
                        # Look for location indicators or reasonable length text
                        if (any(indicator in span_text.lower() for indicator in ['mi', 'km', 'miles', 'away']) or 
                            (len(span_text) > 3 and len(span_text) < 50 and 
                             not span_text.startswith('$') and 
                             span_text != title)):
                            location = span_text
                            break

                print(f"DEBUG: Successfully parsed item:")
                print(f"  Title: {title}")
                print(f"  Price: {price}")
                print(f"  Location: {location}")
                print(f"  URL: {post_url}")
                print(f"  Image: {image[:50]}..." if len(str(image)) > 50 else f"  Image: {image}")

                # Append the parsed data to the list.
                parsed.append({
                    'image': image,
                    'title': title,
                    'price': price,
                    'post_url': post_url,
                    'location': location
                })
                
            except Exception as e:
                print(f"DEBUG: Failed to parse listing: {e}")
                import traceback
                print(f"DEBUG: Full error traceback: {traceback.format_exc()}")
                pass
        
        print(f"DEBUG: Total parsed items: {len(parsed)}")
        
        # Close the browser.
        browser.close()
        # Return the parsed data as a JSON.
        result = []
        for item in parsed:
            # Prepare data for database
            listing_data = {
                'title': item['title'],
                'price': item['price'],
                'location': item['location'],
                'post_url': item['post_url'],
                'image': item['image'],
                'city': city,
                'search_query': query
            }
            
            # Save to database
            save_listing(listing_data)
            
            # Keep existing response format
            result.append({
                'name': item['title'],
                'price': item['price'],
                'location': item['location'],
                'title': item['title'],
                'image': item['image'],
                'link': item['post_url']
            })
        return result

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
    # Run the app.
    # Use Railway's PORT environment variable if available, otherwise default to 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        # Specify the app as the FastAPI app.
        'app:app',
        host='0.0.0.0',  # Railway needs 0.0.0.0
        port=port
    )
