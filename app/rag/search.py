import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from app.database.supabase_client import supabase


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def create_embedding(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding


def search_documents(
    query: str,
    match_threshold: float = 0.40,
    match_count: int = 5
):
    query_embedding = create_embedding(query)

    response = supabase.rpc(
        "match_documents",
        {
            "query_embedding": query_embedding,
            "match_threshold": match_threshold,
            "match_count": match_count
        }
    ).execute()

    return response.data