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
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Navigate directly to marketplace
        print(f"DEBUG: Navigating to {marketplace_url}")
        page.goto(marketplace_url)
        
        # Wait for the page to load completely (listings load first)
        print("DEBUG: Waiting for page to load...")
        time.sleep(5)
        
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
                if img_element and hasattr(img_element, 'get'):
                    src_val = img_element.get('src')
                    if src_val and isinstance(src_val, str):
                        image = src_val

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
    uvicorn.run(
        # Specify the app as the FastAPI app.
        'app:app',
        host='127.0.0.1',
        port=8000
    )
