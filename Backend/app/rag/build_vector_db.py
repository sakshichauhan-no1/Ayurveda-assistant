import json
import os

import chromadb
from sentence_transformers import SentenceTransformer


INPUT_FILE = "app/ingestion/extracted_output.json"
CHROMA_DIR = "app/data/vector_db"
COLLECTION_NAME = "patents_act"

SOURCE_NAME = "The Patents Act, 1970"


def load_blocks():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def clean_blocks(blocks):
    cleaned = []

    for block in blocks:
        text = block["text"].strip()

        # Skip very small junk blocks such as page numbers
        if len(text) < 20:
            continue

        cleaned.append(block)

    return cleaned


def create_chunks(blocks, max_chars=1200):
    chunks = []

    current_text = ""
    current_page = None
    current_bboxes = []

    for block in blocks:
        text = block["text"]
        page = block["page_number"]
        bbox = block["bbox"]

        if (
            current_text
            and (page != current_page or len(current_text) + len(text) > max_chars)
        ):
            chunks.append(
                {
                    "text": current_text.strip(),
                    "page_number": current_page,
                    "bboxes": current_bboxes,
                }
            )

            current_text = ""
            current_bboxes = []

        if not current_text:
            current_page = page

        current_text += text + "\n"
        current_bboxes.append(bbox)

    if current_text.strip():
        chunks.append(
            {
                "text": current_text.strip(),
                "page_number": current_page,
                "bboxes": current_bboxes,
            }
        )

    return chunks


def build_vector_database():
    print("Loading extracted PDF blocks...")

    blocks = load_blocks()

    print(f"Original blocks: {len(blocks)}")

    blocks = clean_blocks(blocks)

    print(f"Clean blocks: {len(blocks)}")

    chunks = create_chunks(blocks)

    print(f"Created chunks: {len(chunks)}")

    print("Loading embedding model...")

    model = SentenceTransformer("all-MiniLM-L6-v2")

    os.makedirs(CHROMA_DIR, exist_ok=True)

    client = chromadb.PersistentClient(path=CHROMA_DIR)

    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME
    )

    print("Generating embeddings...")

    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        show_progress_bar=True
    ).tolist()

    ids = []
    metadatas = []

    for index, chunk in enumerate(chunks):
        ids.append(f"chunk_{index}")

        metadatas.append(
            {
                "source_name": SOURCE_NAME,
                "page_number": chunk["page_number"],
                "bbox_json": json.dumps(chunk["bboxes"]),
            }
        )

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print()
    print("Vector database created successfully.")
    print(f"Stored {len(chunks)} chunks.")
    print(f"Database location: {CHROMA_DIR}")


if __name__ == "__main__":
    build_vector_database()