from fastapi import FastAPI
from fastapi.responses import FileResponse
import os
from supabase import create_client, Client
from datetime import datetime


app = FastAPI(
    title="Vercel + FastAPI",
    description="Vercel + FastAPI",
    version="1.0.0",
)

url: str = str(os.environ.get("SUPABASE_URL"))
key: str = str(os.environ.get("SUPABASE_SECRET_KEY"))
supabase: Client = create_client(url, key)


@app.get("/api/data")
def get_sample_data():
    response = supabase.table("sample_table").select("*").execute()
    data = response.data
    return {
        "data": data,
        "total": len(data),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.get("/api/items/{item_id}")
def get_item(item_id: int):
    response = supabase.table("sample_table").select("*").eq("id", item_id).execute()
    data = response.data
    if data:
        item = data[0]
        return {
            "item": item,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    else:
        return {"error": "Item not found"}


@app.get("/")
def read_root():
    return FileResponse("index.html")
