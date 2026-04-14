#!/bin/bash
# Activate virtual environment and run uvicorn with environment variables
source venv/bin/activate
source .env 2>/dev/null || echo "Note: .env not found, ensure environment variables are set"
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
