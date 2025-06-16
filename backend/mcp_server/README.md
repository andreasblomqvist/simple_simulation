# MCP Server - AI Simulation Q&A System

## How to Run

### 1. Install Dependencies
```sh
pip install fastapi httpx uvicorn
```

### 2. Set Your Anthropic API Key
Get your Anthropic Claude API key from [Anthropic Console](https://console.anthropic.com/) and set it as an environment variable:
```sh
export ANTHROPIC_API_KEY=sk-ant-...   # (Linux/macOS)
# or
set ANTHROPIC_API_KEY=sk-ant-...      # (Windows CMD)
# or
$env:ANTHROPIC_API_KEY="sk-ant-..."   # (Windows PowerShell)
```

### 3. Start the MCP Server
From the `mcp_server` directory (or project root), run:
```sh
uvicorn mcp_server.main:app --reload --port 8100
```
- The server will be available at [http://localhost:8100](http://localhost:8100).

### 4. Stopping the Server
- Press `Ctrl+C` in the terminal where the server is running.

### 5. Example: Test the `/ask` Endpoint
You can use `curl` or Postman to test:
```sh
curl -X POST http://localhost:8100/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the projected EBITDA for Stockholm next year if churn is reduced by 2%?",
    "simulation_params": {
      "start_year": 2024,
      "start_half": "H1",
      "end_year": 2025,
      "end_half": "H2",
      "price_increase": 0.03,
      "salary_increase": 0.03,
      "office_overrides": {"Stockholm": {"roles": {"Consultant": {"A": {"churn_h1": 0.01}}}}}
    }
  }'
```

**Note:**
- Make sure your simulation backend (FastAPI) is running and accessible at `http://localhost:8000/simulate` before starting the MCP server.

---

## Overview
This MCP server lets users ask natural language questions about simulation scenarios and get answers powered by Anthropic Claude (or other LLMs). It connects your simulation backend with an LLM API, so users can prompt questions and receive context-aware answers.

---

## Architecture
```
User (Web UI/Chat/HTTP) <-> MCP Server (FastAPI) <-> Simulation Backend (FastAPI)
                                         |
                                         |-> Anthropic Claude API (LLM)
```
- **MCP Server**: Handles user questions, runs simulations, builds prompts, calls LLM, returns answers.
- **Simulation Backend**: Your existing simulation engine, exposes `/simulate` endpoint.
- **LLM API**: Anthropic Claude (can be extended to OpenAI, etc.)

---

## Environment & Requirements
- Python 3.8+
- [FastAPI](https://fastapi.tiangolo.com/)
- [httpx](https://www.python-httpx.org/)
- [uvicorn](https://www.uvicorn.org/) (for running FastAPI)
- Anthropic API key (get from https://console.anthropic.com/)

### Install dependencies
```sh
pip install fastapi httpx uvicorn
```

### Environment Variables
- `ANTHROPIC_API_KEY` — Your Anthropic Claude API key

Set it in your shell:
```sh
export ANTHROPIC_API_KEY=sk-ant-...
```

---

## Setup & Running

### 1. Start the Simulation Backend
- Make sure your simulation backend (FastAPI) is running and exposes `/simulate` on `http://localhost:8000` (default).
- Example:
  ```sh
  uvicorn backend.main:app --reload --port 8000
  ```

### 2. Start the MCP Server
- From the `mcp_server` directory (or project root):
  ```sh
  uvicorn mcp_server.main:app --reload --port 8100
  ```
- The MCP server will listen on `http://localhost:8100` by default.

### 3. Stopping
- Press `Ctrl+C` in the terminal where each server is running.

---

## Usage

### Example: Ask a Question via HTTP (curl)
```sh
curl -X POST http://localhost:8100/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the projected EBITDA for Stockholm next year if churn is reduced by 2%?",
    "simulation_params": {
      "start_year": 2024,
      "start_half": "H1",
      "end_year": 2025,
      "end_half": "H2",
      "price_increase": 0.03,
      "salary_increase": 0.03,
      "office_overrides": {"Stockholm": {"roles": {"Consultant": {"A": {"churn_h1": 0.01}}}}}
    }
  }'
```
- The response will be a JSON object with an `answer` field containing Claude's reply.

---

## Customization & Extensibility
- You can extend the MCP server to support other LLMs (OpenAI, etc.)
- Add authentication, logging, or a web UI as needed.
- See `MCP_AI_Integration_Plan.md` for more details and roadmap.

---

## Troubleshooting
- Make sure both the simulation backend and MCP server are running.
- Ensure your Anthropic API key is set and valid.
- Check ports (default: 8000 for simulation, 8100 for MCP server).
- For errors, see logs in the terminal where each server is running.

---

## References
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Anthropic Claude API Docs](https://docs.anthropic.com/claude/reference/)
- [httpx Docs](https://www.python-httpx.org/) 