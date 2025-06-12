from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
import os
import httpx

app = FastAPI()

class AskRequest(BaseModel):
    question: str
    simulation_params: Dict[str, Any]

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-3-opus-20240229"  # You can change to another Claude model if needed
SIMULATION_API_URL = "http://localhost:8000/simulate"  # Adjust if needed

@app.post("/ask")
async def ask(req: AskRequest):
    # Call simulation engine via HTTP
    sim_results = await run_simulation(req.simulation_params)
    # Build prompt for Claude
    prompt = f"User asked: {req.question}\nSimulation results: {sim_results}\nPlease answer the user's question using the data above."
    # Call Claude API
    answer = await call_claude_api(prompt)
    return {"answer": answer}

# --- Simulation engine integration via HTTP ---
async def run_simulation(params):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(SIMULATION_API_URL, json=params, timeout=60)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": f"Simulation engine error: {e}"}

# --- Claude API integration ---
async def call_claude_api(prompt: str) -> str:
    if not ANTHROPIC_API_KEY:
        return "Claude API key not set. Set ANTHROPIC_API_KEY environment variable."
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
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(CLAUDE_API_URL, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            # Claude's response is in result['content'][0]['text']
            if "content" in result and isinstance(result["content"], list) and result["content"]:
                return result["content"][0].get("text", "[No answer returned]")
            return "[No answer returned]"
    except Exception as e:
        return f"[Claude API error: {e}]"

# Note: Install httpx with `pip install httpx` and get your Anthropic API key from https://console.anthropic.com/ 