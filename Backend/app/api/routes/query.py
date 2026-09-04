from fastapi import APIRouter

from app.schemas.query import QueryRequest, QueryResponse

import chromadb
from sentence_transformers import SentenceTransformer


router = APIRouter(
    prefix="/api/v1",
    tags=["Query"]
)


# Load the embedding model once when the server starts
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to our existing ChromaDB
chroma_client = chromadb.PersistentClient(
    path="app/data/vector_db"
)

collection = chroma_client.get_collection(
    name="patents_act"
)


@router.post("/query", response_model=QueryResponse)
async def query_assistant(request: QueryRequest):

    # Convert user's question into an embedding
    query_embedding = embedding_model.encode(
        request.query
    ).tolist()

    # Search ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    # Build answer from retrieved source text
    answer_parts = []

    citations = []

    for i in range(len(documents)):

        document = documents[i]
        metadata = metadatas[i]

        answer_parts.append(document)

        citations.append(
            {
                "source_name": metadata["source_name"],
                "page_number": metadata["page_number"],
                "section": "Patents Act, 1970",
                "highlight_text": document
            }
        )

    answer = "\n\n".join(answer_parts)

    return QueryResponse(
        answer=answer,
        citations=citations,
        confidence="medium",
        needs_human_review=True
    )