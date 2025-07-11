# Facebook Marketplace Scraper - Product Requirements Document (PRD)

## 📋 Project Overview

**Product Name:** Facebook Marketplace Scraper  
**Version:** 1.0.0  
**Architecture:** Two-tier web application with REST API backend and Streamlit frontend  
**Primary Function:** Automated scraping of Facebook Marketplace listings with filtering capabilities  

## 🎯 Core Functionality

### **What This Application Does:**
- **Scrapes Facebook Marketplace** for product listings based on user criteria
- **Filters results** by city, search query, and maximum price
- **Extracts structured data**: titles, prices, images, locations, and product URLs
- **Provides a user-friendly web interface** for input and result visualization
- **Returns data in JSON format** via REST API

### **Business Value:**
- Market research and price comparison
- Product availability tracking across different cities
- Automated data collection for resellers and buyers
- Real-time marketplace monitoring

## 🏗️ Technical Architecture

### **System Components:**

#### **1. Backend API Server (`app.py`)**
- **Framework:** FastAPI with Uvicorn ASGI server
- **Port:** 8000 (http://127.0.0.1:8000)
- **Core Dependencies:**
  - Playwright (browser automation)
  - BeautifulSoup4 (HTML parsing)
  - FastAPI (REST API framework)
  - Uvicorn (ASGI server)

#### **2. Frontend GUI (`gui.py`)**
- **Framework:** Streamlit web application
- **Port:** 8501 (http://localhost:8501)
- **Functionality:** User interface for input and result display

#### **3. Web Scraping Engine**
- **Browser:** Chromium (via Playwright)
- **Mode:** Headless browser automation
- **Parser:** BeautifulSoup for DOM manipulation

### **Data Flow Architecture:**
```
User Interface (Streamlit) 
    ↓ HTTP Request
REST API (FastAPI) 
    ↓ Browser Automation
Playwright → Facebook Marketplace 
    ↓ HTML Content
BeautifulSoup Parser 
    ↓ Structured Data
JSON Response → User Interface
```

## 🔄 Main Application Flow

### **Step-by-Step Process with File Mapping:**

| Step | Process | File Involved | Code Location |
|------|---------|---------------|---------------|
| **1** | User selects city + search term + max price in web interface | `gui.py` | Lines 12-16: Streamlit UI components |
| **2** | Streamlit sends HTTP request to FastAPI backend | `gui.py` | Lines 23-25: `requests.get()` call |
| **3** | FastAPI launches Chromium browser via Playwright | `app.py` | Lines 109-113: `sync_playwright()` context |
| **4** | Browser navigates to Facebook Marketplace with search parameters | `app.py` | Lines 106-107: URL construction + navigation |
| **5** | BeautifulSoup extracts: titles, prices, images, locations, URLs | `app.py` | Lines 128-152: HTML parsing and data extraction |
| **6** | Structured JSON data returns to frontend for display | `gui.py` | Lines 28-47: Results iteration and display |

### **Visual Flow Diagram:**

The complete application flow showing file interactions and data processing:

*(Mermaid diagram showing the complete flow from user input through web scraping to result display)*

### **Key File Responsibilities:**

#### **`gui.py` (Frontend - 50 lines)**
- **User Interface:** City dropdown, search input, price filter
- **HTTP Client:** Sends requests to FastAPI backend
- **Result Display:** Shows scraped listings with images and links

#### **`app.py` (Backend - 244 lines)**  
- **API Server:** FastAPI endpoints and request handling
- **Browser Automation:** Playwright Chromium launch and navigation
- **Data Extraction:** BeautifulSoup HTML parsing and JSON structuring
- **City Mapping:** 43 supported US cities with Facebook marketplace IDs

#### **Core Integration Points:**
- **Line 23-25 `gui.py`:** `requests.get()` call to FastAPI endpoint
- **Line 54+ `app.py`:** `/crawl_facebook_marketplace` endpoint handler  
- **Line 109-113 `app.py`:** Playwright browser launch and page automation
- **Line 130-152 `app.py`:** BeautifulSoup data extraction with CSS selectors

## 🔧 Implementation Details

### **API Endpoints:**

#### **1. Root Endpoint**
- **URL:** `GET /`
- **Purpose:** Health check and API information
- **Response:** Welcome message with planned features

#### **2. Main Scraping Endpoint**
- **URL:** `GET /crawl_facebook_marketplace`
- **Parameters:**
  - `city` (string): Target city for search
  - `query` (string): Search term (e.g., "MacBook Pro")
  - `max_price` (integer): Maximum price filter
- **Response:** Array of listing objects

#### **3. IP Information Endpoint**
- **URL:** `GET /return_ip_information`
- **Purpose:** Returns current IP address and location data
- **Use Case:** Network debugging and location verification

### **Supported Cities (43 total):**
New York, Los Angeles, Las Vegas, Chicago, Houston, San Antonio, Miami, Orlando, San Diego, Arlington, Baltimore, Cincinnati, Denver, Fort Worth, Jacksonville, Memphis, Nashville, Philadelphia, Portland, San Jose, Tucson, Atlanta, Boston, Columbus, Detroit, Honolulu, Kansas City, New Orleans, Phoenix, Seattle, Washington DC, Milwaukee, Sacramento, Austin, Charlotte, Dallas, El Paso, Indianapolis, Louisville, Minneapolis, Oklahoma City, Pittsburgh, San Francisco, Tampa

### **Data Extraction Points:**
- **Image URL:** Product thumbnail image
- **Title:** Listing title/product name
- **Price:** Listed price (formatted string)
- **Location:** Seller's general location
- **Product URL:** Direct link to Facebook listing

### **Browser Automation Workflow:**
1. **Launch Chromium browser** (headless=False for debugging)
2. **Navigate to Marketplace URL** with search parameters
3. **Wait for page load** (5-second delay for content to load)
4. **Detect and dismiss login popup** (critical step for accessing content)
   - Check for "See more on Facebook" popup overlay
   - Locate close button (X) in popup header
   - Click to dismiss popup and reveal marketplace listings
   - Wait for popup dismissal animation to complete
5. **Extract page HTML content** (now accessible without login wall)
6. **Parse with BeautifulSoup** using specific CSS selectors
7. **Structure data** into JSON format
8. **Close browser** and return results

## 🚫 Popup Dismissal Strategy

### **Problem Identified:**
Facebook shows a **"See more on Facebook"** login popup that blocks access to marketplace listings. However, the listings are already loaded in the background and become accessible once the popup is dismissed.

### **Solution Approach:**
**Auto-dismiss popup without login** - safer and faster than authentication.

### **Implementation Steps:**

#### **Phase 1: Popup Detection**
- **Wait for page load** (5 seconds to ensure listings load first)  
- **Check for popup presence** using multiple CSS selectors:
  - `div[role="dialog"]` (popup container)
  - Text content containing "See more on Facebook"
  - Close button with `aria-label="Close"`

#### **Phase 2: Popup Dismissal Methods** (Try in sequence)
1. **Primary:** Click X close button in popup header
2. **Secondary:** Press Escape key to dismiss modal
3. **Tertiary:** Click outside popup area (backdrop click)
4. **Fallback:** Wait and retry if popup persists

#### **Phase 3: Verification**
- **Confirm dismissal** by checking popup is no longer visible
- **Verify listings access** by counting visible marketplace items
- **Proceed with scraping** once content is accessible

#### **Code Location:** 
- **File:** `app.py` 
- **Function:** `crawl_facebook_marketplace()`
- **Position:** After page.goto() and before HTML extraction

#### **Error Handling:**
- **Timeout protection:** Max 10 seconds for popup dismissal
- **Retry mechanism:** Up to 3 attempts to dismiss popup
- **Graceful fallback:** Continue scraping even if popup remains (try to parse background content)

### **Expected Benefits:**
- ✅ **No login required** (avoids account risk)
- ✅ **Access to loaded content** (listings already present)
- ✅ **Faster execution** (no authentication delay)
- ✅ **Higher success rate** (proven manual method)

## 📝 Step-by-Step Execution Plan

### **Phase 1: Environment Setup**
1. **Install Python 3.x** (minimum version 3.7)
2. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```
3. **Install Playwright browsers:**
   ```bash
   python3 -m playwright install chromium
   ```

### **Phase 2: Backend Server Launch**
1. **Start FastAPI server:**
   ```bash
   python3 app.py
   ```
2. **Verify API availability** at http://127.0.0.1:8000
3. **Check API documentation** at http://127.0.0.1:8000/docs

### **Phase 3: Frontend Launch**
1. **Start Streamlit GUI:**
   ```bash
   python3 -m streamlit run gui.py
   ```
2. **Access web interface** at http://localhost:8501

### **Phase 4: Application Usage**
1. **Select target city** from dropdown menu
2. **Enter search query** (product name/keywords)
3. **Set maximum price** filter
4. **Click "Submit"** to initiate scraping
5. **Wait 30-60 seconds** for results
6. **Review extracted listings** with images, prices, and links

### **Phase 5: Alternative Execution Methods**
- **Individual processes:** Run API and GUI in separate terminals
- **Combined startup:** Use automation scripts if available
- **API-only mode:** Use curl/Postman for direct API testing

## ⚠️ Current Limitations & Considerations

### **Technical Limitations:**
- **CSS Selector Fragility:** Facebook frequently changes DOM structure
- **Rate Limiting:** No built-in protection against detection
- **Error Handling:** Limited exception handling for parsing failures
- **Performance:** Synchronous scraping (one request at a time)

### **Authentication Requirements:**
- **Facebook Login:** Currently optional but may be required for full access
- **Credentials:** Hardcoded placeholders need manual configuration
- **Account Risk:** Potential for account restrictions with heavy usage

### **Legal & Ethical Considerations:**
- **Terms of Service:** Usage subject to Facebook's ToS
- **Rate Limiting:** Respect website resources and implement delays
- **Data Usage:** Ensure compliance with local data protection laws

## 🔮 Future Enhancements (TODOs in Code)

### **Planned Features:**
- **ReactJS Frontend:** Modern web interface replacement
- **MongoDB Database:** Persistent data storage and history
- **Google Authentication:** Secure user management
- **API Documentation:** Comprehensive endpoint documentation

### **Technical Improvements:**
- **Dynamic City Discovery:** Auto-detect supported cities
- **Advanced Error Handling:** Robust exception management
- **Anti-Detection Measures:** Randomized delays and headers
- **Asynchronous Processing:** Multiple concurrent scraping sessions

## 🚀 Getting Started Checklist

**Prerequisites:**
- [ ] Python 3.7+ installed
- [ ] Git repository cloned
- [ ] Virtual environment activated (recommended)

**Setup Steps:**
- [ ] Install requirements: `pip3 install -r requirements.txt`
- [ ] Install browsers: `python3 -m playwright install chromium`
- [ ] Test API server: `python3 app.py`
- [ ] Test GUI: `python3 -m streamlit run gui.py`
- [ ] Verify both services communicate correctly

**First Scraping Test:**
- [ ] Open GUI at http://localhost:8501
- [ ] Select "New York" as city
- [ ] Search for "iPhone" with max price "500"
- [ ] Verify results display with images and prices

## 📊 Success Metrics

**Technical Success Indicators:**
- Both services start without errors
- API responds to requests within 60 seconds
- GUI displays structured results with images
- No critical exceptions in console logs

**Functional Success Indicators:**
- Successfully extracts 5+ listings per search
- All data fields populated (title, price, location)
- Images load correctly in GUI
- Facebook URLs are valid and clickable

This PRD serves as your complete guide to understanding, implementing, and running the Facebook Marketplace Scraper system.
