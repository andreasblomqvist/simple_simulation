# Simple Workforce Simulation

A lightweight workforce simulation engine for modeling organizational growth and development.

## Features

- Simple employee progression modeling
- Office growth simulation
- Career path tracking
- Workforce analytics

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run tests:
```bash
pytest tests/
```

## Project Structure

```
simple_simulation/
├── src/
│   ├── models/      # Data models
│   ├── services/    # Business logic
│   └── utils/       # Helper functions
├── tests/
│   ├── unit/        # Unit tests
│   └── integration/ # Integration tests
└── config/          # Configuration files
```

## Development

This project uses:
- Python 3.8+
- pytest for testing
- SQLAlchemy for data modeling 

## Running the Backend

1. **Create a virtual environment (if not already created):**
   ```powershell
   python -m venv .venv
   ```
2. **Activate the virtual environment:**
   ```powershell
   .venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```
4. **Run the backend server (from the project root):**
   ```powershell
   uvicorn backend.main:app --reload
   ```

> **Note:**
> - Always run the backend from the project root directory (where the `backend` folder is located).
> - If you encounter import errors, double-check your working directory and that your virtual environment is activated. 