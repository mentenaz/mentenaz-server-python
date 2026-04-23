# AGENTS.md - Guidance for Agentic Coding Agents

This file provides guidance for agents operating in this repository.

## Project Overview

Flask backend for a portfolio chatbot that answers questions about Francois Huyzers's professional profile. It fetches data from Supabase and uses the Groq API (LLaMA 3.1 8B Instant) to generate responses.

## Environment

- Python 3.x
- Required environment variables in `.env`:
  - `GROQ_API_KEY` — Groq API key
  - `SUPABASE_URL` — Supabase project URL
  - `SUPABASE_KEY` — Supabase publishable key
  - `ALLOWED_ORIGIN` — CORS origin (defaults to `*`)

## Build / Run Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server (debug mode, port 5000)
python app.py

# Run with gunicorn (production)
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

## Testing

**No test framework is currently configured.** To add tests:

```bash
# Install pytest
pip install pytest pytest-cov

# Run all tests
pytest

# Run a single test file
pytest tests/test_app.py

# Run a single test function
pytest tests/test_app.py::test_function_name

# Run with coverage
pytest --cov=app --cov-report=term-missing
```

## Linting / Type Checking

**No linting or type checking tools are configured.** Recommended additions to `requirements.txt`:

```
flake8
mypy
isort
```

Commands after installation:

```bash
# Run flake8 (linting)
flake8 app.py

# Run isort (import sorting)
isort --check-only app.py

# Run mypy (type checking)
mypy app.py

# Fix all linting issues
flake8 --fix app.py
isort app.py
```

## Code Style Guidelines

### General Principles

- Keep it simple and readable
- Match existing code style in the project
- Single-file app (`app.py`) — prefer adding to the main file unless it grows too large (>500 lines)

### Imports

- Standard library imports first (`os`, `time`, `datetime`)
- Third-party imports second (`flask`, `groq`, `supabase`)
- Use `from x import y` for clarity rather than `import x`
- No wildcard imports (`from x import *`)

Example:
```python
import os
import time
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from groq import Groq
from supabase import Client, create_client
```

### Formatting

- Maximum line length: 100 characters
- Use 4 spaces for indentation (PEP 8 default)
- No trailing whitespace
- One blank line between top-level definitions
- Use f-strings for string formatting
- Use parentheses for line continuation

### Naming Conventions

- Functions: `snake_case` (e.g., `fetch_profile`, `build_system_prompt`)
- Variables: `snake_case` (e.g., `groq_client`, `CACHE_TTL`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `CACHE_TTL = 300`)
- Classes: Use only if needed (not currently used in this project)
- File names: `snake_case` (e.g., `app.py`, `passenger_wsgi.py`)

### Type Hints

- Not currently enforced, but add when beneficial:
  ```python
  def fetch_profile() -> str:
      row: dict = supabase.table("profile").select("*").single().execute().data
      return f"..."
  ```
- Use `typing` module for complex types (List, Dict, Optional, Union)

### Error Handling

- Wrap route handlers in try/except when calling external services
- Return JSON error responses with appropriate HTTP status codes
- Use specific exception handling rather than bare `except:`

```python
try:
    # external call
    response = groq_client.chat.completions.create(...)
    return jsonify({"reply": response.choices[0].message.content})

except Exception as e:
    return jsonify({"error": str(e)}), 500
```

### Route Handlers

- Use `@app.route("/path", methods=["POST"])` decorator
- Validate request data early with appropriate 400 responses
- Use `request.get_json()` for JSON body parsing
- Return tuples `(response, status_code)` for non-200 responses

### Data Layer Functions

- One fetch function per Supabase table
- Return formatted strings (not raw JSON/dicts) for prompt assembly
- Use descriptive names: `fetch_<table_name>()`
- Order by `display_order` column when applicable

### Caching

- Use simple in-memory cache with TTL for prompt data
- Cache key: `_cache = {"prompt": None, "timestamp": 0}`
- Cache TTL constant: `CACHE_TTL = 300` (5 minutes)
- Check cache validity before fetching fresh data

### API Clients

- Initialize lazily or at module level with environment variables
- Use type hints for client objects: `supabase: Client = create_client(...)`
- Handle missing environment variables gracefully

### Comments

- Keep to a minimum
- Use only for complex logic or non-obvious decisions
- No commented-out code — remove dead code

### Security

- Never log or expose secrets/API keys
- Validate input on all endpoints
- Use environment variables for configuration, not hardcoded values

### Git Practices

- Create meaningful commit messages
- Commit related changes together
- Do not commit `.env` files or secrets

## File Structure

```
.
├── app.py                 # Main Flask application
├── passenger_wsgi.py     # WSGI entry point for production
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (not committed)
└── .gitignore            # Git ignore rules
```

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `CACHE_TTL` | 300 | Cache TTL in seconds (5 minutes) |
| Model | `llama-3.1-8b-instant` | Groq LLM model |
| `max_tokens` | 500 | Maximum response tokens |
| Port | 5000 | Development server port |

## Common Tasks

### Adding a new Supabase table
1. Create fetch function: `def fetch_<table>() -> str:`
2. Add to `build_system_prompt()` in the context aggregation
3. Update CLAUDE.md with table schema

### Adding a new route
1. Add decorator: `@app.route("/new-route", methods=["POST"])`
2. Implement handler with input validation
3. Return JSON response with appropriate status code

### Debugging
1. Set `debug=True` in `app.run()` for development
2. Check console output for errors
3. Verify environment variables are loaded: `print(os.getenv("KEY"))`