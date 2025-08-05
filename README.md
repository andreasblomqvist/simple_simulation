# Simple Workforce Simulation

A lightweight workforce simulation engine for modeling organizational growth and development.

## Features

- Simple employee progression modeling
- Office growth simulation
- Career path tracking
- Workforce analytics
- **Year-by-year simulation navigation and KPI tracking** (new)
- **Enhanced UI with simplified controls and year-over-year comparisons** (v2)

## Setup

### Backend Setup

1. Create a virtual environment (Python 3.9+ recommended):
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

2. Install dependencies (from the backend directory):
```bash
cd backend
pip install -r requirements.txt
```

3. Run tests (from the project root):
```bash
python3 -m pytest backend/tests/unit/
```

   - To run a specific test file:
     ```bash
     python3 -m pytest backend/tests/unit/test_engine_basic.py
     ```

### Frontend Setup

1. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the frontend development server:**
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:3000`

3. **Build for production:**
   ```bash
   npm run build
   ```

## Project Structure

```
simple_simulation/
├── backend/
│   ├── src/            # Business logic and services
│   ├── config/         # Configuration files
│   ├── routers/        # API endpoints
│   ├── tests/
│   │   └── unit/       # Unit tests (year-based and monthly simulation)
│   └── requirements.txt
├── frontend/           # React frontend application
│   ├── src/
│   │   ├── components/ # UI components
│   │   │   └── v2/     # Enhanced v2 components with year navigation
│   │   ├── pages/      # Page components
│   │   └── types.ts    # TypeScript type definitions
│   ├── package.json
│   └── tsconfig.json
└── README.md
```

## Development

This project uses:
- **Backend:** Python 3.9+, pytest, FastAPI
- **Frontend:** React 18, TypeScript, Ant Design, Vite

## Running the Application

### Full Development Environment

1. **Start the backend server (from project root):**
   ```bash
   # Terminal 1 - Backend
   source .venv/bin/activate
   uvicorn backend.main:app --reload
   ```
   Backend will be available at `http://localhost:8000`

2. **Start the frontend server (from project root):**
   ```bash
   # Terminal 2 - Frontend  
   cd frontend
   npm run dev
   ```
   Frontend will be available at `http://localhost:3000`

### Testing the Year Navigation Features

1. **Access the Year Navigation Demo:**
   - Navigate to `http://localhost:3000/year-demo`
   - Test year-by-year navigation and enhanced KPI cards
   - Explore year-over-year change indicators and trend visualizations

2. **Run backend tests for year-based features:**
   ```bash
   python3 -m pytest backend/tests/unit/test_year_based_simulation.py
   ```

## Running the Backend (Legacy Instructions)

1. **Create a virtual environment (if not already created):**
   ```bash
   python3 -m venv .venv
   ```
2. **Activate the virtual environment:**
   ```bash
   source .venv/bin/activate  # On Unix/macOS
   .venv\Scripts\activate    # On Windows
   ```
3. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
4. **Run the backend server (from the project root):**
   ```bash
   uvicorn backend.main:app --reload
   ```

> **Notes:**
> - Always run the backend from the project root directory (where the `backend` folder is located).
> - If you encounter import errors, double-check your working directory and that your virtual environment is activated.
> - For year-based simulation features, see the new test suite in `backend/tests/unit/test_year_based_simulation.py`.
> - For Python 3.11 support, ensure you have Python 3.11 installed and create your virtual environment with `python3.11 -m venv .venv`.
> - The frontend uses Vite for fast development and hot module replacement.
> - New v2 components showcase enhanced UX with year navigation capabilities.