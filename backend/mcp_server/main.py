from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
import os
import httpx
import asyncio
import time

app = FastAPI()

class AskRequest(BaseModel):
    question: str
    simulation_params: Dict[str, Any]

# Get API key from environment variable
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"  # Latest Claude 3.5 Sonnet model
SIMULATION_API_URL = "http://localhost:8000/simulation/run"  # Updated to current API endpoint

# Rate limiting variables
last_request_time = 0
min_request_interval = 2.0  # Minimum 2 seconds between requests

# Simple cache to avoid repeated API calls for similar questions
response_cache = {}
cache_ttl = 300  # Cache responses for 5 minutes

# Configuration options
ENABLE_RATE_LIMITING = True  # Set to False to disable rate limiting
ENABLE_CACHING = True        # Set to False to disable caching
MAX_RETRIES = 3             # Number of retry attempts
BASE_DELAY = 1.0            # Base delay for exponential backoff

@app.post("/ask")
async def ask(req: AskRequest):
    # Call simulation engine via HTTP
    sim_results = await run_simulation(req.simulation_params)
    # Build prompt for Claude
    prompt = f"User asked: {req.question}\nSimulation results: {sim_results}\nPlease answer the user's question using the data above."
    # Call Claude API
    answer = await call_claude_api(prompt)
    return {"answer": answer}

@app.get("/status")
async def get_status():
    """Get MCP server status and configuration"""
    global last_request_time, response_cache
    current_time = time.time()
    time_since_last = current_time - last_request_time if last_request_time > 0 else None
    
    return {
        "status": "running",
        "configuration": {
            "rate_limiting_enabled": ENABLE_RATE_LIMITING,
            "caching_enabled": ENABLE_CACHING,
            "min_request_interval": min_request_interval,
            "max_retries": MAX_RETRIES,
            "cache_ttl": cache_ttl
        },
        "current_state": {
            "time_since_last_request": time_since_last,
            "cached_responses": len(response_cache),
            "ready_for_request": time_since_last is None or time_since_last >= min_request_interval
        }
    }

# --- Simulation engine integration via HTTP ---
async def run_simulation(params):
    try:
        # Convert MCP parameters to current simulation engine format
        duration_months = params.get("duration_months", 12)
        
        # Calculate end year/month from duration
        start_year = params.get("start_year", 2025)
        start_month = params.get("start_month", 1)
        
        total_months = start_month + duration_months - 1
        end_year = start_year + (total_months - 1) // 12
        end_month = ((total_months - 1) % 12) + 1
        
        # Build simulation request matching current API
        sim_params = {
            "start_year": start_year,
            "start_month": start_month,
            "end_year": end_year,
            "end_month": end_month,
            "price_increase": params.get("price_increase", 0.03),
            "salary_increase": params.get("salary_increase", 0.03),
            "unplanned_absence": params.get("unplanned_absence", 0.05),
            "hy_working_hours": params.get("hy_working_hours", 166.4),
            "other_expense": params.get("other_expense", 19000000.0)
        }
        
        # Add office overrides if provided
        if "office_overrides" in params:
            sim_params["office_overrides"] = params["office_overrides"]
            
        print(f"[DEBUG] MCP calling simulation with: {sim_params}")
            
        async with httpx.AsyncClient() as client:
            response = await client.post(SIMULATION_API_URL, json=sim_params, timeout=60)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": f"Simulation engine error: {e}"}

# --- Claude API integration ---
async def call_claude_api(prompt: str) -> str:
    global last_request_time, response_cache
    
    if not ANTHROPIC_API_KEY:
        return "Claude API key not set. Set ANTHROPIC_API_KEY environment variable."
    
    # Check cache first (if enabled)
    if ENABLE_CACHING:
        cache_key = hash(prompt)
        current_time = time.time()
        if cache_key in response_cache:
            cached_response, timestamp = response_cache[cache_key]
            if current_time - timestamp < cache_ttl:
                return f"{cached_response}\n\n[Cached response - no API call made]"
    
    # Rate limiting: ensure minimum time between requests (if enabled)
    if ENABLE_RATE_LIMITING:
        current_time = time.time()
        time_since_last = current_time - last_request_time
        if time_since_last < min_request_interval:
            wait_time = min_request_interval - time_since_last
            await asyncio.sleep(wait_time)
    
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": CLAUDE_MODEL,
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    # Retry logic with exponential backoff
    for attempt in range(MAX_RETRIES):
        try:
            if ENABLE_RATE_LIMITING:
                last_request_time = time.time()
            async with httpx.AsyncClient() as client:
                response = await client.post(CLAUDE_API_URL, headers=headers, json=data, timeout=60)
                
                # Debug the response
                print(f"[DEBUG] Claude API response status: {response.status_code}")
                if response.status_code != 200:
                    print(f"[DEBUG] Claude API error response: {response.text}")
                
                response.raise_for_status()
                result = response.json()
                # Claude's response is in result['content'][0]['text']
                if "content" in result and isinstance(result["content"], list) and result["content"]:
                    answer = result["content"][0].get("text", "[No answer returned]")
                    
                    # Cache the response (if enabled)
                    if ENABLE_CACHING:
                        response_cache[cache_key] = (answer, time.time())
                    
                    return answer
                return "[No answer returned]"
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                if attempt < MAX_RETRIES - 1:
                    # Exponential backoff: wait longer each time
                    delay = BASE_DELAY * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    return "Rate limit exceeded. Please wait a few minutes before making another request. The system is working correctly but needs time between requests."
            return f"[Claude API error: {e}]"
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                delay = BASE_DELAY * (2 ** attempt)
                await asyncio.sleep(delay)
                continue
            return f"[Claude API error: {e}]"
    
    return "[Max retries exceeded]"

# Note: Install httpx with `pip install httpx` and get your Anthropic API key from https://console.anthropic.com/ 