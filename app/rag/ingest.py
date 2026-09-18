from pathlib import Path
from pypdf import PdfReader

from app.database.supabase_client import supabase


def read_pdf(path: str):
    reader = PdfReader(path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        pages.append({
            "page": page_number,
            "text": text.strip()
        })

    return pages


def chunk_text(text: str, size: int = 1200, overlap: int = 200):
    chunks = []

    start = 0
    chunk_number = 1

    while start < len(text):
        end = start + size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append({
                "chunk_number": chunk_number,
                "content": chunk
            })

            chunk_number += 1

        start += size - overlap

    return chunks


def ingest_pdf(pdf_path: Path):
    pages = read_pdf(str(pdf_path))

    inserted = 0

    for page in pages:
        chunks = chunk_text(page["text"])

        for chunk in chunks:
            record = {
                "filename": pdf_path.name,
                "page": page["page"],
                "content": chunk["content"],
                "metadata": {
                    "chunk_number": chunk["chunk_number"],
                    "source_type": "NUPRC guideline"
                }
            }

            supabase.table("documents").insert(record).execute()

            inserted += 1

    return len(pages), inserted


if __name__ == "__main__":
    documents_folder = Path("../data/raw/documents")

    pdf_files = list(documents_folder.glob("*.pdf"))

    print(f"Found {len(pdf_files)} PDF files")

    total_inserted = 0

    for pdf_path in pdf_files:
        print(f"\nProcessing: {pdf_path.name}")

        pages, chunks = ingest_pdf(pdf_path)

        total_inserted += chunks

        print(f"Pages: {pages}")
        print(f"Chunks inserted: {chunks}")

    print("\n-----------------------------")
    print(f"Total chunks inserted: {total_inserted}")
    print("-----------------------------")