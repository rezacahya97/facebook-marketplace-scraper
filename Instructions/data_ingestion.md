# Facebook Marketplace Data Ingestion - PRD

## Outcome
**Connect existing scraper to marketplace_listings table** so every search automatically feeds data into the database for future analytics.

**Success Metric**: Every scrape request stores listings in Supabase, enabling status tracking and trend analysis.

## Current State vs. Target State

**Current**: `Scraper → Parse → Return JSON → Data disappears`
**Target**: `Scraper → Parse → Store in Supabase → Return JSON + Database populated`

## Flow Diagram

```
User Request (Streamlit)
    ↓
FastAPI /crawl_facebook_marketplace
    ↓
Playwright scrapes Facebook
    ↓
Parse listings (existing logic)
    ↓
FOR EACH LISTING:
    ↓
Store in marketplace_listings table
    ↓
Return same JSON response to user
```

## Files Modified

### Primary Changes
- `app.py` - Add database storage after parsing
- `database.py` - Create Supabase connection functions
- `requirements.txt` - Add supabase-py

### No Changes Needed
- `streamlit_app.py` - Keep existing interface
- Existing scraping logic - Keep as-is
- User experience - Identical to current

## Implementation Plan

### Step 1: Database Connection (15 minutes)
**Create `database.py`**
```python
from supabase import create_client, Client
import os
from datetime import datetime

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY") 
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
        result = supabase.table('marketplace_listings').insert({
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
        }).execute()
        return result
    except Exception as e:
        print(f"Error saving listing: {e}")
        return None
```

### Step 2: Modify Scraper (30 minutes)
**Update `app.py` - Add database storage**

Add imports:
```python
from database import save_listing
```

Replace the return statement in `crawl_facebook_marketplace()`:
```python
# BEFORE: At the end of the function
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

# AFTER: Add database storage
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
```

### Step 3: Environment Setup (5 minutes)
**Add to `.env` file**:
```
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
```

**Update `requirements.txt`**:
```
supabase==1.0.3
```

### Step 4: Testing (10 minutes)
1. Run a search from Streamlit
2. Check Supabase marketplace_listings table
3. Verify data appears correctly
4. Confirm user experience unchanged

## Risk Mitigation

**What if database save fails?**
- Scraper still returns results to user
- Error logged but doesn't break user experience
- User sees no difference in functionality

**What if Supabase is down?**
- Scraper continues working normally
- Database writes fail silently
- No impact on user experience

## Success Criteria

- [ ] Each scrape stores listings in marketplace_listings table
- [ ] User experience remains identical
- [ ] Data populates with correct format for existing status checker
- [ ] No performance degradation
- [ ] Error handling prevents crashes

## Deployment Steps

1. Add environment variables to hosting platform
2. Install supabase dependency 
3. Deploy updated code
4. Run test search
5. Verify database population

**Total Implementation Time**: ~1 hour
**User-Facing Changes**: None (invisible data collection)