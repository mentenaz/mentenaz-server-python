# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Flask backend for a portfolio chatbot that answers questions about Francois Huyzers's professional profile. It fetches data from Supabase and uses the Groq API (LLaMA 3.1 8B Instant) to generate responses.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server (debug mode, port 5000)
python app.py
```

Production is served via Passenger WSGI (`passenger_wsgi.py` imports `app` as `application`).

## Environment Variables

Required in `.env`:
- `GROQ_API_KEY` — Groq API key
- `SUPABASE_URL` — Supabase project URL
- `SUPABASE_KEY` — Supabase publishable key
- `ALLOWED_ORIGIN` — CORS origin (defaults to `*`)

## Architecture

Single-file app (`app.py`) with three layers:

**Data layer** — Six functions (`fetch_profile`, `fetch_experience`, `fetch_skills`, `fetch_projects`, `fetch_skills_progression`, `fetch_education`) each query a specific Supabase table and return structured dicts.

**Caching + prompt assembly** — `build_system_prompt()` aggregates all six data functions, caches the result for 5 minutes (in-memory TTL via `_cache` dict), and constructs a context-rich system prompt including today's date and strict instructions to avoid inventing facts.

**Chat endpoint** — `POST /chat` accepts `{ message, history[] }`, prepends the system prompt to the conversation history, calls Groq with max 500 tokens, and returns the assistant reply as JSON.

### Key constants
- Cache TTL: `CACHE_TTL = 300` (line 21)
- LLM model: `llama-3.1-8b-instant` (line 189)
- Max output tokens: `500` (line 191)

## Supabase Schema

Tables: `profile`, `experience`, `skills`, `projects`, `skills_progression`, `education`. Each fetch function documents the exact columns it selects — refer to `app.py` lines 24–131 for the full field list.
