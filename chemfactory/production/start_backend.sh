#!/bin/bash
cd production/backend
export DATABASE_URL="sqlite:///./production.db"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
