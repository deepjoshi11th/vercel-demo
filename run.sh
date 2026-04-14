#!/bin/bash
# Activate virtual environment and run uvicorn with environment variables
source venv/bin/activate
source env.sh
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
