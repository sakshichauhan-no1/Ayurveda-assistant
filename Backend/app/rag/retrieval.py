import chromadb
from sentence_transformers import SentenceTransformer


CHROMA_DIR = "app/data/vector_db"
COLLECTION_NAME = "patents_act"
MODEL_NAME = "all-MiniLM-L6-v2"


# Load model once when the application starts.
# We don't want to download/load it for every question.
model = SentenceTransformer(MODEL_NAME)

# Connect to the existing ChromaDB database.
client = chromadb.PersistentClient(path=CHROMA_DIR)

collection = client.get_collection(name=COLLECTION_NAME)


def retrieve_documents(query: str, top_k: int = 5):
    """
    Retrieve the most relevant chunks from the Patents Act vector database.
    """

    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    retrieved_documents = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):
        retrieved_documents.append(
            {
                "text": document,
                "source_name": metadata.get(
                    "source_name",
                    "The Patents Act, 1970"
                ),
                "page_number": metadata.get("page_number"),
                "distance": distance
            }
        )

    return retrieved_documents