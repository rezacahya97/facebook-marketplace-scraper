# Strategy 1: Local Tunnel Architecture - Setup Instructions

## 📋 Overview
This strategy exposes your working local scraper via Cloudflare Tunnel, allowing Supabase Edge Functions to call it remotely. Your scraper runs on your residential IP (bypassing bot detection) while being accessible for automated cron jobs.

## 🏗 Architecture Flow
```
Supabase Cron (every 12 hours) 
    ↓
Supabase Edge Function 
    ↓
Cloudflare Tunnel (secure)
    ↓
Local FastAPI Scraper (your residential IP)
    ↓
Supabase Database (listings stored)
```

## 🚀 Implementation Steps

### Step 1: Install Cloudflare Tunnel
```bash
# Install cloudflared
brew install cloudflare/cloudflare/cloudflared

# Login to Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create marketplace-scraper-tunnel

# Copy tunnel UUID and update cloudflare-tunnel.yml
```

### Step 2: Configure Tunnel
1. Update `cloudflare-tunnel.yml` with your tunnel UUID
2. Set up tunnel credentials path
3. Test tunnel configuration

### Step 3: Start Local Services

#### Terminal 1: Start FastAPI Scraper
```bash
# Activate your Python environment if needed
# source venv/bin/activate

# Start the local scraper
python app.py
```

#### Terminal 2: Start Cloudflare Tunnel
```bash
# Start tunnel with configuration
cloudflared tunnel --config cloudflare-tunnel.yml run marketplace-scraper-tunnel
```

### Step 4: Get Tunnel URL
- Cloudflare will provide a public URL (e.g., `https://abc-123.trycloudflare.com`)
- Test it: `curl https://your-tunnel-url.trycloudflare.com/health`

### Step 5: Deploy Supabase Edge Function
```bash
# Install Supabase CLI
npm install -g supabase

# Login to Supabase
supabase login

# Link to your project
supabase link --project-ref YOUR_PROJECT_REF

# Set environment variables
supabase secrets set TUNNEL_URL=https://your-tunnel-url.trycloudflare.com
supabase secrets set SUPABASE_URL=your-supabase-url
supabase secrets set SUPABASE_ANON_KEY=your-anon-key

# Deploy edge function
supabase functions deploy marketplace-cron
```

### Step 6: Set Up Supabase Cron
In your Supabase dashboard, create a cron job:

```sql
-- Create cron_logs table first
CREATE TABLE IF NOT EXISTS cron_logs (
    id SERIAL PRIMARY KEY,
    execution_time TIMESTAMP DEFAULT NOW(),
    strategy TEXT,
    listings_found INTEGER DEFAULT 0,
    searches_executed INTEGER DEFAULT 0,
    errors TEXT[],
    tunnel_url TEXT
);

-- Create cron job for every 12 hours
SELECT cron.schedule(
    'marketplace-scraping',
    '0 */12 * * *',  -- Every 12 hours
    $$
    SELECT
      net.http_post(
          url:='https://your-project-ref.supabase.co/functions/v1/marketplace-cron',
          headers:='{"Content-Type": "application/json", "Authorization": "Bearer YOUR_ANON_KEY"}'::jsonb
      ) as request_id;
    $$
);
```

## 🔧 Configuration Files Created

### 1. `app.py` (Modified)
- ✅ Added CORS for tunnel access
- ✅ Added `/health` endpoint
- ✅ Fixed NavigableString type errors
- ✅ Ready for tunnel exposure

### 2. `cloudflare-tunnel.yml`
- ✅ Tunnel configuration
- ✅ Ingress rules for local FastAPI
- ✅ Security settings

### 3. `supabase/functions/marketplace-cron/index.ts`
- ✅ Edge function for cron trigger
- ✅ Multiple city/query configurations
- ✅ Error handling and logging
- ✅ Tunnel health checks

## 🎯 Testing Strategy 1

### Test 1: Local Scraper Works
```bash
# Test direct scraper
curl "http://localhost:8000/crawl_facebook_marketplace?city=New%20York&query=iphone&max_price=800"
```

### Test 2: Tunnel Connectivity
```bash
# Test health endpoint via tunnel
curl https://your-tunnel-url.trycloudflare.com/health

# Test scraper via tunnel
curl "https://your-tunnel-url.trycloudflare.com/crawl_facebook_marketplace?city=New%20York&query=iphone&max_price=800"
```

### Test 3: Edge Function
```bash
# Test edge function directly
curl -X POST "https://your-project-ref.supabase.co/functions/v1/marketplace-cron" \
  -H "Authorization: Bearer YOUR_ANON_KEY" \
  -H "Content-Type: application/json"
```

### Test 4: Full Automation Flow
- Wait for cron execution (or trigger manually)
- Check `cron_logs` table for results
- Verify listings in your database

## ⚡ Quick Start Script

Run this after completing setup steps:

```bash
# Quick test of complete flow
./test-strategy1.sh
```

## 🛟 Troubleshooting

### Common Issues:

1. **Tunnel won't start**
   - Check tunnel credentials
   - Verify cloudflare-tunnel.yml paths
   - Ensure port 8000 is available

2. **Health check fails**
   - Verify FastAPI is running on :8000
   - Check tunnel URL is correct
   - Test local endpoint first

3. **Edge function timeout**
   - Increase timeout in edge function
   - Check scraper performance
   - Verify tunnel stability

4. **No listings found**
   - Test scraper locally first
   - Check Facebook isn't blocking your IP
   - Verify search parameters

## 📊 Expected Results

### Success Metrics:
- **Success Rate**: 95% (using residential IP)
- **Listings Retrieved**: 10-50 per search
- **Response Time**: 15-30 seconds per search
- **Uptime**: 99%+ (local machine dependent)

### Monitoring:
- Check `cron_logs` table for execution history
- Monitor tunnel metrics at Cloudflare dashboard
- Set up alerts for failed cron executions

## 🔄 Next Steps After Success

1. **Scale searches**: Add more cities/queries to `SEARCH_CONFIGS`
2. **Optimize performance**: Reduce scraper execution time
3. **Add notifications**: Email/Slack alerts for new listings
4. **Data analysis**: Build dashboards from collected data
5. **Backup strategy**: Implement Strategy 2 as fallback

## 💡 Why This Strategy Works

✅ **Residential IP**: Uses your home internet (bypasses datacenter detection)  
✅ **Known Working Code**: Same scraper that works locally  
✅ **Secure Tunnel**: Cloudflare provides enterprise-grade security  
✅ **Automated**: Supabase cron handles scheduling  
✅ **Scalable**: Easy to add more searches  
✅ **Monitorable**: Full logging and error tracking  

This strategy leverages your working local setup while providing cloud automation! 