# SimpleSim - Simulation Platform

## Overview
SimpleSim is a simulation platform with:
- **Frontend**: Modern React/Ant Design dashboard for simulation control and results visualization
- **Backend**: FastAPI simulation engine
- **MCP Server**: AI Q&A server that lets users ask questions about simulation scenarios and get answers from LLMs (e.g., Claude)
- **Tests**: Unit and integration tests for backend and core logic

---

## Architecture
```
[Frontend (React)] <-> [Backend (FastAPI)] <-> [MCP Server (FastAPI)]
                                         |
                                         |-> [LLM API (Claude, etc.)]
```

---

## 1. Frontend (React)
- Located in `frontend/`
- Modern UI with Ant Design, KPI cards, lever controls, and results tables

### Setup & Run
```sh
cd frontend
npm install
npm run dev
```
- Runs on [http://localhost:3000](http://localhost:3000) by default

---

## 2. Backend (Simulation Engine)
- Located in `backend/` and `simple_simulation/`
- FastAPI app exposing `/simulate` and other endpoints

### Setup & Run
```sh
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
- Runs on [http://localhost:8000](http://localhost:8000) by default

---

## 3. MCP Server (AI Q&A)
- Located in `mcp_server/`
- FastAPI app exposing `/ask` endpoint
- Integrates with Anthropic Claude (or other LLMs)

### How to Run the MCP Server
1. **Install dependencies**
   ```sh
   pip install fastapi httpx uvicorn
   ```
2. **Set your Anthropic API key**
   ```sh
   export ANTHROPIC_API_KEY=sk-ant-...   # (Linux/macOS)
   # or
   set ANTHROPIC_API_KEY=sk-ant-...      # (Windows CMD)
   # or
   $env:ANTHROPIC_API_KEY="sk-ant-..."   # (Windows PowerShell)
   ```
3. **Start the MCP server**
   ```sh
   uvicorn mcp_server.main:app --reload --port 8100
   ```
   - The server will be available at [http://localhost:8100](http://localhost:8100).
4. **Test the /ask endpoint** (see `mcp_server/README.md` for a curl example)

> **See `mcp_server/README.md` for full details and troubleshooting.**

---

## 4. Tests
- Unit tests in `simple_simulation/tests/unit/`
- (Add integration tests as needed)

### Run Tests
```sh
cd simple_simulation
test/unit
pytest
```

---

## Usage
- Use the frontend to configure and run simulations, view KPIs, and analyze results
- Use the MCP server to ask natural language questions about simulation scenarios and get LLM-powered answers

---

## References
- See `MCP_AI_Integration_Plan.md` and `mcp_server/README.md` for more details on the MCP server and AI integration
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [Ant Design](https://ant.design/)
- [Anthropic Claude API Docs](https://docs.anthropic.com/claude/reference/) 