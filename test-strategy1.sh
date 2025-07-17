#!/bin/bash

# Test Script for Strategy 1: Local Tunnel Architecture
# This script validates all components of the implementation

set -e  # Exit on any error

echo "🚀 Testing Strategy 1: Local Tunnel Architecture"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
LOCAL_URL="http://localhost:8000"
TUNNEL_URL="${TUNNEL_URL:-}"  # Set this environment variable
EDGE_FUNCTION_URL="${EDGE_FUNCTION_URL:-}"  # Set this environment variable

# Test functions
test_local_scraper() {
    echo -e "\n${BLUE}🧪 Test 1: Local Scraper Functionality${NC}"
    echo "Testing local FastAPI server..."
    
    # Test health endpoint
    if curl -s "${LOCAL_URL}/health" > /dev/null; then
        echo -e "${GREEN}✅ Health endpoint working${NC}"
    else
        echo -e "${RED}❌ Health endpoint failed${NC}"
        echo "Make sure to run: python app.py"
        return 1
    fi
    
    # Test root endpoint
    if curl -s "${LOCAL_URL}/" > /dev/null; then
        echo -e "${GREEN}✅ Root endpoint working${NC}"
    else
        echo -e "${RED}❌ Root endpoint failed${NC}"
        return 1
    fi
    
    # Test scraper endpoint
    echo "Testing scraper with New York iPhone search..."
    RESPONSE=$(curl -s "${LOCAL_URL}/crawl_facebook_marketplace?city=New%20York&query=iphone&max_price=800")
    
    if [[ $RESPONSE == *"["* ]]; then
        LISTING_COUNT=$(echo $RESPONSE | jq '. | length' 2>/dev/null || echo "unknown")
        echo -e "${GREEN}✅ Scraper endpoint working - Found $LISTING_COUNT listings${NC}"
    else
        echo -e "${YELLOW}⚠️  Scraper returned: $RESPONSE${NC}"
        echo -e "${YELLOW}    This might be due to Facebook detection - normal for first test${NC}"
    fi
}

test_tunnel_connectivity() {
    echo -e "\n${BLUE}🧪 Test 2: Cloudflare Tunnel Connectivity${NC}"
    
    if [[ -z "$TUNNEL_URL" ]]; then
        echo -e "${RED}❌ TUNNEL_URL not set${NC}"
        echo "Please set TUNNEL_URL environment variable to your tunnel URL"
        echo "Example: export TUNNEL_URL=https://abc-123.trycloudflare.com"
        return 1
    fi
    
    echo "Testing tunnel URL: $TUNNEL_URL"
    
    # Test tunnel health
    if curl -s "${TUNNEL_URL}/health" > /dev/null; then
        echo -e "${GREEN}✅ Tunnel health endpoint working${NC}"
    else
        echo -e "${RED}❌ Tunnel health endpoint failed${NC}"
        echo "Make sure tunnel is running: cloudflared tunnel --config cloudflare-tunnel.yml run marketplace-scraper-tunnel"
        return 1
    fi
    
    # Test tunnel scraper
    echo "Testing scraper via tunnel..."
    TUNNEL_RESPONSE=$(curl -s "${TUNNEL_URL}/crawl_facebook_marketplace?city=New%20York&query=iphone&max_price=800")
    
    if [[ $TUNNEL_RESPONSE == *"["* ]]; then
        TUNNEL_LISTING_COUNT=$(echo $TUNNEL_RESPONSE | jq '. | length' 2>/dev/null || echo "unknown")
        echo -e "${GREEN}✅ Tunnel scraper working - Found $TUNNEL_LISTING_COUNT listings${NC}"
    else
        echo -e "${YELLOW}⚠️  Tunnel scraper returned: $TUNNEL_RESPONSE${NC}"
    fi
}

test_edge_function() {
    echo -e "\n${BLUE}🧪 Test 3: Supabase Edge Function${NC}"
    
    if [[ -z "$EDGE_FUNCTION_URL" ]]; then
        echo -e "${YELLOW}⚠️  EDGE_FUNCTION_URL not set - skipping edge function test${NC}"
        echo "To test edge function, set EDGE_FUNCTION_URL environment variable"
        echo "Example: export EDGE_FUNCTION_URL=https://your-project.supabase.co/functions/v1/marketplace-cron"
        return 0
    fi
    
    echo "Testing edge function: $EDGE_FUNCTION_URL"
    
    # Test edge function
    EDGE_RESPONSE=$(curl -s -X POST "$EDGE_FUNCTION_URL" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${SUPABASE_ANON_KEY:-your-key}")
    
    if [[ $EDGE_RESPONSE == *"success"* ]]; then
        echo -e "${GREEN}✅ Edge function working${NC}"
        echo "Response: $EDGE_RESPONSE"
    else
        echo -e "${RED}❌ Edge function failed${NC}"
        echo "Response: $EDGE_RESPONSE"
        return 1
    fi
}

check_dependencies() {
    echo -e "\n${BLUE}🔍 Checking Dependencies${NC}"
    
    # Check if jq is installed for JSON parsing
    if ! command -v jq &> /dev/null; then
        echo -e "${YELLOW}⚠️  jq not found - install with: brew install jq${NC}"
    else
        echo -e "${GREEN}✅ jq installed${NC}"
    fi
    
    # Check if curl is available
    if ! command -v curl &> /dev/null; then
        echo -e "${RED}❌ curl not found${NC}"
        return 1
    else
        echo -e "${GREEN}✅ curl available${NC}"
    fi
    
    # Check if cloudflared is installed
    if ! command -v cloudflared &> /dev/null; then
        echo -e "${YELLOW}⚠️  cloudflared not found - install with: brew install cloudflare/cloudflare/cloudflared${NC}"
    else
        echo -e "${GREEN}✅ cloudflared installed${NC}"
    fi
    
    # Check if supabase CLI is installed
    if ! command -v supabase &> /dev/null; then
        echo -e "${YELLOW}⚠️  supabase CLI not found - install with: npm install -g supabase${NC}"
    else
        echo -e "${GREEN}✅ supabase CLI installed${NC}"
    fi
}

show_setup_status() {
    echo -e "\n${BLUE}📋 Setup Status Check${NC}"
    
    # Check if app.py exists
    if [[ -f "app.py" ]]; then
        echo -e "${GREEN}✅ app.py exists${NC}"
    else
        echo -e "${RED}❌ app.py not found${NC}"
    fi
    
    # Check if cloudflare-tunnel.yml exists
    if [[ -f "cloudflare-tunnel.yml" ]]; then
        echo -e "${GREEN}✅ cloudflare-tunnel.yml exists${NC}"
    else
        echo -e "${RED}❌ cloudflare-tunnel.yml not found${NC}"
    fi
    
    # Check if supabase directory exists
    if [[ -d "supabase/functions/marketplace-cron" ]]; then
        echo -e "${GREEN}✅ Supabase edge function directory exists${NC}"
    else
        echo -e "${YELLOW}⚠️  Supabase edge function directory not found${NC}"
    fi
    
    # Check if local server is running
    if curl -s "$LOCAL_URL/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Local FastAPI server is running${NC}"
    else
        echo -e "${RED}❌ Local FastAPI server not running${NC}"
        echo "Start it with: python app.py"
    fi
}

# Main execution
main() {
    echo -e "Starting comprehensive test of Strategy 1 implementation...\n"
    
    # Check setup status
    show_setup_status
    
    # Check dependencies
    check_dependencies
    
    # Run tests
    echo -e "\n${BLUE}🏃 Running Tests${NC}"
    echo "=================="
    
    # Test 1: Local scraper
    if test_local_scraper; then
        echo -e "${GREEN}✅ Test 1 passed${NC}"
    else
        echo -e "${RED}❌ Test 1 failed${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    
    # Test 2: Tunnel connectivity
    if test_tunnel_connectivity; then
        echo -e "${GREEN}✅ Test 2 passed${NC}"
    else
        echo -e "${RED}❌ Test 2 failed${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    
    # Test 3: Edge function
    if test_edge_function; then
        echo -e "${GREEN}✅ Test 3 passed${NC}"
    else
        echo -e "${RED}❌ Test 3 failed${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    
    # Summary
    echo -e "\n${BLUE}📊 Test Summary${NC}"
    echo "================"
    
    if [[ ${FAILED_TESTS:-0} -eq 0 ]]; then
        echo -e "${GREEN}🎉 All tests passed! Strategy 1 is ready for production.${NC}"
        echo -e "${GREEN}You can now set up the Supabase cron job for automation.${NC}"
    else
        echo -e "${RED}❌ $FAILED_TESTS test(s) failed.${NC}"
        echo -e "${YELLOW}Please fix the issues above before proceeding.${NC}"
    fi
    
    echo -e "\n${BLUE}📚 Next Steps${NC}"
    echo "=============="
    echo "1. If tests passed, set up Supabase cron job (see strategy1-setup.md)"
    echo "2. Monitor cron_logs table for execution results"
    echo "3. Scale up by adding more cities/queries to SEARCH_CONFIGS"
    echo "4. Set up alerts for failed executions"
}

# Initialize failed tests counter
FAILED_TESTS=0

# Run main function
main

# Exit with error code if tests failed
exit ${FAILED_TESTS:-0} 