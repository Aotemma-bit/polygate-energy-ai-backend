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


def embed_documents():
    response = (
        supabase
        .table("documents")
        .select("id, content")
        .is_("embedding", "null")
        .execute()
    )

    documents = response.data

    print(f"Documents without embeddings: {len(documents)}")

    for index, document in enumerate(documents, start=1):

        embedding = create_embedding(document["content"])

        (
            supabase
            .table("documents")
            .update({
                "embedding": embedding
            })
            .eq("id", document["id"])
            .execute()
        )

        print(
            f"[{index}/{len(documents)}] "
            f"Embedded document ID {document['id']}"
        )


if __name__ == "__main__":
    embed_documents()