// Supabase Edge Function for Strategy 1: Local Tunnel Architecture
// This function is triggered by Supabase Cron every 12 hours
// It calls the local scraper via Cloudflare Tunnel

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const TUNNEL_URL = Deno.env.get('TUNNEL_URL') // Your Cloudflare Tunnel URL
const SUPABASE_URL = Deno.env.get('SUPABASE_URL')
const SUPABASE_ANON_KEY = Deno.env.get('SUPABASE_ANON_KEY')

// Initialize Supabase client
const supabase = createClient(SUPABASE_URL!, SUPABASE_ANON_KEY!)

// Search configurations for different cities and items
const SEARCH_CONFIGS = [
  { city: 'New York', query: 'iphone', max_price: 800 },
  { city: 'Los Angeles', query: 'macbook', max_price: 1500 },
  { city: 'Chicago', query: 'ps5', max_price: 600 },
  { city: 'Miami', query: 'laptop', max_price: 1000 },
  // Add more search configurations as needed
]

interface ScrapingResult {
  name: string
  price: string
  location: string
  title: string
  image: string
  link: string
}

serve(async (req) => {
  // ULTRA-VERBOSE DEBUG LOGGING - IF YOU SEE THIS, CRON IS WORKING!
  console.log('🔥🔥🔥 EDGE FUNCTION CALLED! Method:', req.method, 'URL:', req.url)
  console.log('🔥🔥🔥 Headers:', Object.fromEntries(req.headers.entries()))
  console.log('🔥🔥🔥 Timestamp:', new Date().toISOString())
  
  try {
    console.log('🚀 Starting Strategy 1: Local Tunnel marketplace scraping...')
    
    // Verify tunnel connectivity first
    if (!TUNNEL_URL) {
      throw new Error('TUNNEL_URL environment variable not set')
    }
    
    // Health check tunnel
    console.log('🔍 Checking tunnel health...')
    const healthResponse = await fetch(`${TUNNEL_URL}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    if (!healthResponse.ok) {
      throw new Error(`Tunnel health check failed: ${healthResponse.status}`)
    }
    
    const healthData = await healthResponse.json()
    console.log('✅ Tunnel is healthy:', healthData)
    
    // Process each search configuration
    const allResults: ScrapingResult[] = []
    const errors: string[] = []
    
    for (const config of SEARCH_CONFIGS) {
      try {
        console.log(`📍 Scraping ${config.city} for "${config.query}" under $${config.max_price}`)
        
        // Call local scraper via tunnel
        const scrapeUrl = `${TUNNEL_URL}/crawl_facebook_marketplace?city=${encodeURIComponent(config.city)}&query=${encodeURIComponent(config.query)}&max_price=${config.max_price}`
        
        const response = await fetch(scrapeUrl, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'User-Agent': 'Supabase-Edge-Function/1.0',
          },
          // Timeout after 60 seconds
          signal: AbortSignal.timeout(60000)
        })
        
        if (!response.ok) {
          throw new Error(`Scraping failed for ${config.city}: ${response.status} ${response.statusText}`)
        }
        
        const results: ScrapingResult[] = await response.json()
        console.log(`✅ Found ${results.length} listings in ${config.city}`)
        
        allResults.push(...results)
        
        // Add small delay between requests to be respectful
        await new Promise(resolve => setTimeout(resolve, 2000))
        
      } catch (error) {
        const errorMsg = `Error scraping ${config.city}: ${error.message}`
        console.error('❌', errorMsg)
        errors.push(errorMsg)
      }
    }
    
    // Log final results
    console.log(`🎯 Scraping complete! Found ${allResults.length} total listings`)
    if (errors.length > 0) {
      console.log(`⚠️  ${errors.length} errors occurred:`, errors)
    }
    
    // Store cron execution log
    try {
      await supabase
        .from('cron_logs')
        .insert({
          execution_time: new Date().toISOString(),
          strategy: 'Local Tunnel Architecture',
          listings_found: allResults.length,
          searches_executed: SEARCH_CONFIGS.length,
          errors: errors.length > 0 ? errors : null,
          tunnel_url: TUNNEL_URL
        })
    } catch (logError) {
      console.error('Failed to log to database:', logError)
    }
    
    return new Response(
      JSON.stringify({
        success: true,
        strategy: 'Local Tunnel Architecture',
        timestamp: new Date().toISOString(),
        listings_found: allResults.length,
        searches_executed: SEARCH_CONFIGS.length,
        errors: errors.length,
        tunnel_healthy: true,
        message: 'Automated scraping completed successfully'
      }),
      {
        headers: { 'Content-Type': 'application/json' },
        status: 200
      }
    )
    
  } catch (error) {
    console.error('❌ Cron function failed:', error)
    
    // Log error to database
    try {
      await supabase
        .from('cron_logs')
        .insert({
          execution_time: new Date().toISOString(),
          strategy: 'Local Tunnel Architecture',
          listings_found: 0,
          searches_executed: 0,
          errors: [error.message],
          tunnel_url: TUNNEL_URL || 'not_set'
        })
    } catch (logError) {
      console.error('Failed to log error to database:', logError)
    }
    
    return new Response(
      JSON.stringify({
        success: false,
        strategy: 'Local Tunnel Architecture',
        timestamp: new Date().toISOString(),
        error: error.message,
        tunnel_url: TUNNEL_URL || 'not_set'
      }),
      {
        headers: { 'Content-Type': 'application/json' },
        status: 500
      }
    )
  }
}) 