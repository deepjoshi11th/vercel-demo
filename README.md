# FastAPI + Vercel

This is an example project to learn how supabase db + vercel deployment of flask  bakend works.

## Demo

https://vercel-demo-sooty-xi.vercel.app/

## How it Works

This example uses the Asynchronous Server Gateway Interface (ASGI) with FastAPI to enable handling requests with Serverless Functions.

## Running Locally

```
source venv/bin/activate
source env.sh
lsof -i :8000
kill <pid>
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Your FastAPI application is now available at `http://localhost:8000`.