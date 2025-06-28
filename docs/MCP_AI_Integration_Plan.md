# MCP AI Integration Plan

## Overview
Build a Multi-Channel Platform (MCP) server that connects your simulation system to LLMs (e.g., ChatGPT, Claude), enabling users to ask questions and receive answers based on simulation data.

---

## 1. Architecture

```
User (Web UI/Chat) <-> MCP Server (API) <-> Simulation Engine
                                 |-> LLM API (OpenAI, Anthropic, etc.)
```

- **MCP Server**: Handles user queries, runs simulations, builds prompts, calls LLM APIs, returns answers.
- **Simulation Engine**: Your existing backend for running simulations and returning results.
- **LLM API**: External API for ChatGPT, Claude, etc.

---

## 2. Tech Stack
- **Backend**: Python (FastAPI recommended)
- **LLM Integration**: OpenAI API, Anthropic API, etc.
- **Frontend (optional)**: React/Next.js or simple chat UI
- **Auth (optional)**: JWT or OAuth for user management

---

## 3. API Design

### Endpoints
- `POST /ask` — Accepts user question and simulation params, returns LLM answer
- `POST /simulate` — (Optional) Direct simulation endpoint
- `GET /history` — (Optional) Get user Q&A history

### Example `/ask` Request
```json
{
  "question": "What is the projected EBITDA for Stockholm next year if churn is reduced by 2%?",
  "simulation_params": { ... }
}
```

### Example `/ask` Response
```json
{
  "answer": "If churn is reduced by 2%, the projected EBITDA for Stockholm next year is ..."
}
```

---

## 4. Workflow
1. **User submits a question** (and optionally simulation params)
2. **MCP server**:
   - Runs simulation (if needed)
   - Builds a prompt with the question and simulation results
   - Calls LLM API (ChatGPT, Claude, etc.)
   - Returns the LLM's answer to the user

---

## 5. Prompt Engineering
- Include user question and relevant simulation data in the prompt
- Example prompt:
  ```
  User asked: {question}
  Simulation results: {sim_results}
  Please answer the user's question using the data above.
  ```

---

## 6. Next Steps
1. Scaffold FastAPI backend with `/ask` endpoint
2. Add simulation engine integration (import/run simulation)
3. Add LLM API integration (OpenAI, Anthropic, etc.)
4. (Optional) Add user/session management
5. (Optional) Build simple frontend chat UI

---

## 7. Example FastAPI Scaffold
```python
from fastapi import FastAPI, Request
from pydantic import BaseModel
import openai  # or anthropic, etc.

app = FastAPI()

class AskRequest(BaseModel):
    question: str
    simulation_params: dict

@app.post("/ask")
async def ask(req: AskRequest):
    # 1. Run simulation (pseudo-code)
    sim_results = run_simulation(req.simulation_params)
    # 2. Build prompt
    prompt = f"User asked: {req.question}\nSimulation results: {sim_results}\nPlease answer the user's question using the data above."
    # 3. Call LLM API (pseudo-code)
    answer = call_llm_api(prompt)
    return {"answer": answer}
```

---

## 8. Security & Scaling
- Add API key or OAuth for user access
- Rate limiting for LLM API calls
- Logging and monitoring

---

## 9. Extensibility
- Add support for multiple LLMs (user can choose model)
- Add context/memory for multi-turn conversations
- Integrate with other data sources as needed

---

## 10. References
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [OpenAI API Docs](https://platform.openai.com/docs/api-reference)
- [Anthropic API Docs](https://docs.anthropic.com/claude/reference/) 