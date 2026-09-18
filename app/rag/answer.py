import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from app.rag.search import search_documents


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def build_context(results):
    context_blocks = []

    for index, result in enumerate(results, start=1):
        filename = result.get("filename", "Unknown source")
        page = result.get("page", "Unknown page")
        content = result.get("content", "")

        context_blocks.append(
            f"""
SOURCE {index}
Filename: {filename}
Page: {page}

{content}
""".strip()
        )

    return "\n\n".join(context_blocks)


def answer_question(query: str):
    results = search_documents(
        query=query,
        match_threshold=0.50,
        match_count=6
    )

    if not results:
        return {
            "answer": (
                "I could not find sufficient supporting material "
                "in the current FieldFlow knowledge base."
            ),
            "sources": []
        }

    context = build_context(results)

    system_prompt = """
You are FieldFlow, an industrial oil and gas operations assistant.

Answer the user's question ONLY using the supplied source material.

Rules:
1. Do not invent regulations, procedures, technical requirements, or facts.
2. If the sources are insufficient, explicitly say so.
3. Use simple, professional engineering language.
4. Cite claims using this exact format:
   [filename, p.X]
5. Do not cite a source that does not support the claim.
6. Do not give autonomous instructions to operate industrial equipment.
7. Operational recommendations must be framed as items for qualified human review.
8. Distinguish clearly between regulatory requirements and engineering recommendations.
"""

    user_prompt = f"""
QUESTION:
{query}

SOURCE MATERIAL:
{context}

Provide a concise answer grounded only in the supplied sources.
"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        instructions=system_prompt,
        input=user_prompt
    )

    sources = []

    for result in results:
        sources.append({
            "filename": result["filename"],
            "page": result["page"],
            "similarity": result["similarity"]
        })

    return {
        "answer": response.output_text,
        "sources": sources
    }
def stream_answer_question(query: str):
    results = search_documents(
        query=query,
        match_threshold=0.50,
        match_count=6
    )

    if not results:
        yield {
            "type": "error",
            "message": (
                "I could not find sufficient supporting material "
                "in the current FieldFlow knowledge base."
            )
        }
        return

    context = build_context(results)

    system_prompt = """
You are FieldFlow, an industrial oil and gas operations assistant.

Answer the user's question ONLY using the supplied source material.

Rules:
1. Do not invent regulations, procedures, technical requirements, or facts.
2. If the sources are insufficient, explicitly say so.
3. Use simple, professional engineering language.
4. Cite claims using this exact format:
   [filename, p.X]
5. Do not cite a source that does not support the claim.
6. Do not give autonomous instructions to operate industrial equipment.
7. Operational recommendations must be framed as items for qualified human review.
8. Distinguish clearly between regulatory requirements and engineering recommendations.
"""

    user_prompt = f"""
QUESTION:
{query}

SOURCE MATERIAL:
{context}

Provide a concise answer grounded only in the supplied sources.
"""

    stream = client.responses.create(
        model="gpt-5.6-luna",
        instructions=system_prompt,
        input=user_prompt,
        stream=True
    )

    for event in stream:
        if event.type == "response.output_text.delta":
            yield {
                "type": "token",
                "text": event.delta
            }

    sources = []

    for result in results:
        sources.append({
            "filename": result["filename"],
            "page": result["page"],
            "similarity": result["similarity"]
        })

    yield {
        "type": "sources",
        "sources": sources
    }
