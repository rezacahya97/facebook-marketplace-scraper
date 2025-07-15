from supabase.client import create_client, Client
import os
from datetime import datetime
from dotenv import load_dotenv
import uuid

# Load environment variables from .env file
load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")

if not url or not key:
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file")

supabase: Client = create_client(url, key)

def extract_price_number(price_string):
    """Extract numeric price from '$1,200' format"""
    import re
    if not price_string or price_string == "Price not found":
        return None
    match = re.search(r'[\d,]+(?:\.\d{2})?', price_string.replace('$', ''))
    return float(match.group().replace(',', '')) if match else None

def save_listing(listing_data):
    """Save single listing to marketplace_listings table"""
    try:
        print(f"DEBUG: Attempting to save listing: {listing_data.get('title', 'No title')}")
        
        data_to_insert = {
            'id': str(uuid.uuid4()),  # Generate unique UUID for each listing
            'title': listing_data.get('title', 'No title found'),
            'price_amount': extract_price_number(listing_data.get('price')),
            'price_formatted': listing_data.get('price', 'Price not found'),
            'location_display': listing_data.get('location', 'Location not found'),
            'city': listing_data.get('city'),
            'listing_url': listing_data.get('post_url'),
            'facebook_url': listing_data.get('post_url'),
            'primary_photo_url': listing_data.get('image'),
            'search_query': listing_data.get('search_query'),
            'search_location': listing_data.get('city'),
            'is_live': True,
            'is_pending': False,
            'is_sold': False,
            'scraped_at': datetime.now().isoformat(),
            'last_checked_at': datetime.now().isoformat()
        }
        
        print(f"DEBUG: Inserting data: {data_to_insert}")
        result = supabase.table('marketplace_listings').insert(data_to_insert).execute()
        print(f"DEBUG: Successfully saved listing to database")
        return result
    except Exception as e:
        print(f"ERROR: Failed to save listing to database: {e}")
        return None 