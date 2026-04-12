import os
from supabase import create_client, Client

url:str = str(os.environ.get("SUPABASE_URL"))
key:str = str(os.environ.get("SUPABASE_SECRET_KEY"))
supabase: Client = create_client(url, key)
response = supabase.table("sample_table").select("*").execute()
print(response)