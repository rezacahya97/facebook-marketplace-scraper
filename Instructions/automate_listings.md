# Facebook Marketplace Automation - Implementation Plan
## Option B: Railway Deployment + Supabase Edge Functions

### 🎯 Goal
Automate Facebook Marketplace scraping every 12 hours using:
- FastAPI deployed to Railway (stable public URL, supports browser dependencies)
- Supabase Edge Functions with built-in cron
- Zero local server dependencies

### 📊 **CURRENT STATUS**

**✅ PHASE 1 COMPLETED:**
- ✅ Removed Vercel configuration files
- ✅ Modified `app.py` for Railway deployment compatibility  
- ✅ Installed Railway CLI and deployed successfully
- ✅ Fixed browser dependencies (all Playwright libs installed)
- ✅ FastAPI app running on Railway: `https://flipping-software-production.up.railway.app`
- ✅ API endpoints responding with Status 200

**⚠️ ISSUE DISCOVERED:**
- ⚠️ Scraping returns empty array `[]` - Facebook redirecting to login page
- ⚠️ Selectors finding 0 elements - possible bot detection or outdated selectors

**🔧 IMMEDIATE DECISION REQUIRED:**
**Option A:** Debug Facebook scraping now (recommended - 15-30 min)  
**Option B:** Proceed to Supabase automation and debug later (risky)

**Recommendation: Option A** - Fix core scraping before building automation around it.

### 🛠️ **WHY RAILWAY IS BETTER**

#### **✅ Railway Advantages:**
- **Zero size limits** - supports full Playwright/Chromium
- **Zero code changes** - your proven app.py works as-is
- **Faster deployment** - 15 minutes vs hours of debugging
- **Container-based** - full Linux environment for browsers
- **Built-in domains** - automatic HTTPS
- **Cost-effective** - $5/month for automation workloads

### 📋 Implementation Steps

## Phase 1: Deploy FastAPI to Railway (15 minutes) - ✅ **COMPLETED**

### Step 1.1: Clean Up Vercel Files ✅ **READY**
**Remove Vercel-specific configuration:**
```bash
# Remove vercel.json (not needed for Railway)
rm vercel.json
```

### Step 1.2: Restore Original App Configuration ✅ **READY** 
**Edit:** `app.py` - Uncomment the uvicorn.run section for Railway

**Change back to:**
```python
if __name__ == "__main__":
    # Run the app.
    uvicorn.run(
        # Specify the app as the FastAPI app.
        'app:app',
        host='0.0.0.0',  # Railway needs 0.0.0.0
        port=8000
    )
```

### Step 1.3: Install Railway CLI & Deploy 🚀 **NEW APPROACH**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway 
railway login

# Initialize and deploy
railway link
railway up
```

**Expected Output:**
```
✅ Deployed to https://your-app-name.railway.app
```

### Step 1.4: Verify Deployment 🎯 **TEST PHASE**
Test the Railway URL in browser:
```
https://your-app-name.railway.app/
```
Should show: "Welcome to Passivebot's Facebook Marketplace API"

### Step 1.5: Test API Endpoint 🧪 **VALIDATION**
```
https://flipping-software-production.up.railway.app/crawl_facebook_marketplace?city=New York&query=iPhone&max_price=1000
```

**✅ Current Status:** Railway deployment successful, API returns Status 200, but empty results due to Facebook bot detection.

## Phase 1.5: Debug Facebook Scraping (15-30 minutes) - 🔧 **CURRENT PRIORITY**

### **Issue Analysis:**
From Railway logs, we can see:
- ✅ Browser launches successfully in headless mode
- ✅ Navigates to Facebook Marketplace URL  
- ❌ Facebook redirects to login page (`https://www.facebook.com/login/`)
- ❌ All selectors find 0 elements
- ❌ Returns empty array `[]`

### **Root Cause Options:**
1. **Facebook Login Required** - Marketplace might require authentication
2. **Bot Detection** - Facebook detecting automated browser  
3. **Outdated Selectors** - Page structure changed since local testing
4. **Rate Limiting** - IP being blocked/throttled
5. **Geo-restrictions** - Railway servers in different region

### **Debugging Approach:**

**Option A: Fix Now (Recommended)**
- ✅ **Pros:** Ensures core functionality before automation setup
- ✅ **Pros:** Validates that automation will actually work
- ⚠️ **Cons:** May require experimenting with anti-bot measures

**Option B: Fix During Edge Function Development**  
- ⚠️ **Cons:** Risk of discovering fundamental issues after automation setup
- ⚠️ **Cons:** May require changes to Railway deployment

### **Recommended Fix Strategy:**
1. **Test with different user agents** - Make browser look more human-like
2. **Add random delays** - Mimic human browsing behavior  
3. **Update selectors** - Check if Facebook changed their HTML structure
4. **Add cookies/session handling** - Maintain persistent session
5. **Test from different regions** - Verify it's not geo-blocking

### **Decision Point:**
**SHOULD WE FIX SCRAPING NOW OR PROCEED TO AUTOMATION?**

**Recommendation: Fix now** - because there's no point automating broken scraping.

## Phase 2: Create Supabase Edge Function (10 minutes) - ⏳ **READY AFTER PHASE 1.5**

### Step 2.1: Access Supabase Dashboard
1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Select your project
3. Navigate to **Edge Functions** in left sidebar

### Step 2.2: Create New Edge Function
**Function Name:** `marketplace-scraper`

**Function Code:**
```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req) => {
  try {
    console.log('Starting marketplace automation...')
    
    // Replace with your Railway URL from Step 1.4
    const API_BASE_URL = 'https://your-app-name.railway.app'
    
    // Define search parameters
    const searchParams = {
      city: 'New York',        // Change as needed
      query: 'iPhone',         // Change as needed  
      max_price: 1000         // Change as needed
    }
    
    // Build API URL
    const apiUrl = `${API_BASE_URL}/crawl_facebook_marketplace?` + 
                   `city=${encodeURIComponent(searchParams.city)}&` +
                   `query=${encodeURIComponent(searchParams.query)}&` +
                   `max_price=${searchParams.max_price}`
    
    console.log('Calling API:', apiUrl)
    
    // Make request to your FastAPI endpoint
    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    if (!response.ok) {
      throw new Error(`API responded with status: ${response.status}`)
    }
    
    const data = await response.json()
    
    console.log(`Automation completed successfully. Found ${data.length} listings.`)
    
    return new Response(
      JSON.stringify({ 
        success: true, 
        listings_found: data.length,
        timestamp: new Date().toISOString(),
        search_params: searchParams 
      }),
      { 
        headers: { "Content-Type": "application/json" },
        status: 200 
      }
    )
    
  } catch (error) {
    console.error('Automation error:', error)
    
    return new Response(
      JSON.stringify({ 
        success: false, 
        error: error.message,
        timestamp: new Date().toISOString() 
      }),
      { 
        headers: { "Content-Type": "application/json" },
        status: 500 
      }
    )
  }
})
```

### Step 2.3: Update Edge Function Configuration
**Important:** Replace `your-app-name` in the API_BASE_URL with your actual Railway deployment URL from Step 1.4

## Phase 3: Set Up Supabase Cron (5 minutes) - ⏳ **READY AFTER PHASE 2**

### Step 3.1: Navigate to Database
1. In Supabase Dashboard, go to **Database** → **Extensions**
2. Enable **pg_cron** extension if not already enabled

### Step 3.2: Create Cron Job
Go to **SQL Editor** and run:

```sql
-- Schedule edge function to run every 12 hours
SELECT cron.schedule(
  'marketplace-automation',           -- job name
  '0 */12 * * *',                    -- every 12 hours (at 00:00 and 12:00)
  $$
  SELECT
    net.http_post(
      url:='https://YOUR_PROJECT_REF.supabase.co/functions/v1/marketplace-scraper',
      headers:='{"Content-Type": "application/json", "Authorization": "Bearer YOUR_ANON_KEY"}'::jsonb
    ) as request_id;
  $$
);
```

**Replace:**
- `YOUR_PROJECT_REF` with your Supabase project reference
- `YOUR_ANON_KEY` with your Supabase anon key

### Step 3.3: Verify Cron Job
```sql
-- Check if cron job was created
SELECT * FROM cron.job;
```

## Phase 4: Testing & Verification (10 minutes) - ⏳ **FINAL PHASE**

### Step 4.1: Manual Test Edge Function
In Supabase Dashboard → Edge Functions → `marketplace-scraper`:
Click **"Invoke Function"** button

**Expected Response:**
```json
{
  "success": true,
  "listings_found": 15,
  "timestamp": "2024-01-24T10:30:00.000Z",
  "search_params": {
    "city": "New York",
    "query": "iPhone", 
    "max_price": 1000
  }
}
```

### Step 4.2: Verify Database Storage
Check your `marketplace_listings` table in Supabase:
```sql
SELECT * FROM marketplace_listings 
ORDER BY scraped_at DESC 
LIMIT 10;
```

### Step 4.3: Monitor Logs
- **Edge Function Logs:** Supabase Dashboard → Edge Functions → Logs
- **Railway Logs:** Railway Dashboard → Your Project → Deployments → Logs

## 🔧 Configuration & Customization

### Change Search Parameters
Edit the Edge Function code and update:
```typescript
const searchParams = {
  city: 'Los Angeles',     // Different city
  query: 'MacBook Pro',    // Different item
  max_price: 2000         // Different price
}
```

### Change Schedule
Modify the cron expression in Phase 3.2:
- `'0 */6 * * *'` = Every 6 hours
- `'0 0 * * *'` = Daily at midnight
- `'0 0 */2 * *'` = Every 2 days

### Add Multiple Searches (Future)
Create additional Edge Functions:
- `marketplace-scraper-iphones`
- `marketplace-scraper-laptops`
- `marketplace-scraper-furniture`

Each with its own cron schedule and search parameters.

## 🚨 Important Notes

### Railway Deployment Benefits
- **No size limits**: Full support for Playwright/Chromium dependencies
- **Container-based**: Complete Linux environment for browser automation
- **Stable URL**: Your Railway URL never changes once deployed
- **Automatic HTTPS**: SSL certificate included automatically
- **Always-on**: No cold starts affecting scraping performance
- **Built-in monitoring**: Logs, metrics, and alerts included

### Environment Variables
Add environment variables in Railway Dashboard:
1. Go to Railway Dashboard → Your Project → Variables
2. Add `SUPABASE_URL` and `SUPABASE_ANON_KEY`
3. Railway automatically redeploys with new variables

### Security
- Your API is publicly accessible (same as before)
- Railway provides DDoS protection automatically
- Built-in request monitoring and alerts
- No additional security configuration needed

## 📊 Monitoring Success

### Daily Checks
1. **Supabase Edge Function Logs** - Check for errors
2. **Database Records** - Verify new listings added
3. **Railway Application Logs** - Monitor API performance and browser automation

### Success Metrics
- Edge function executes without errors
- New listings appear in database every 12 hours
- Search parameters working as expected
- Railway deployment stays responsive
- Browser automation works reliably

## 🚀 Next Steps After Testing

Once confirmed working:
1. **Add multiple automated searches** with different parameters
2. **Set up monitoring alerts** for failed runs
3. **Implement data analysis** on collected listings
4. **Configure custom domain** (optional)
5. **Scale to additional cities/search terms**

---

## 📊 **Updated Timeline**

**✅ Phase 1 (Railway Deployment):** 15 minutes - **COMPLETED**  
**🔧 Phase 1.5 (Debug Scraping):** 15-30 minutes - **CURRENT PRIORITY**  
**⏳ Phase 2 (Supabase Edge Function):** 10 minutes - **PENDING**  
**⏳ Phase 3 (Supabase Cron):** 5 minutes - **PENDING**  
**⏳ Phase 4 (Testing):** 10 minutes - **PENDING**  

**Total Estimated Time:** ~30-45 minutes (including debugging)  
**Ongoing Maintenance:** Zero (fully automated)  
**Scalability:** Easy to add more searches by creating new Edge Functions  
**Code Changes:** Minimal (just scraping improvements + host configuration)

## ✅ Railway vs Vercel Comparison

| Factor | Railway | Vercel |
|--------|---------|--------|
| **Browser Support** | ✅ Full Playwright support | ❌ 250MB size limit |
| **Code Changes** | ✅ Minimal (host only) | ❌ Major refactoring needed |
| **Setup Time** | ✅ 15 minutes | ❌ 30+ minutes + debugging |
| **Reliability** | ✅ Proven for automation | ❌ Serverless limitations |
| **Cost** | ✅ $5/month | ✅ Similar pricing |
| **Maintenance** | ✅ Zero | ❌ Function size monitoring |

**Railway is clearly the better choice for your browser automation needs!** 🎯
