from pathlib import Path
import os
import httpx

from dotenv import load_dotenv
from supabase import create_client, Client
from supabase.lib.client_options import SyncClientOptions

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        f"Supabase environment variables are missing. Expected .env at: {ENV_FILE}"
    )

# Dedicated HTTP client for Supabase.
# Keep-alive is disabled to avoid stale Windows socket reuse.
http_client = httpx.Client(
    timeout=httpx.Timeout(
        30.0,
        connect=10.0,
    ),
    limits=httpx.Limits(
        max_connections=20,
        max_keepalive_connections=0,
    ),
)

options = SyncClientOptions(
    schema="public",
    postgrest_client_timeout=30,
    httpx_client=http_client,
)

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
    options=options,
)
