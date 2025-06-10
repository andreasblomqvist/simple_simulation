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