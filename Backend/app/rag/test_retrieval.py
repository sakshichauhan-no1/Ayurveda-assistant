import chromadb
from sentence_transformers import SentenceTransformer


CHROMA_DIR = "app/data/vector_db"
COLLECTION_NAME = "patents_act"


def search(query, top_k=5):
    print(f"\nSearching for: {query}\n")

    # Load the same embedding model used when building the database
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Open our existing ChromaDB
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    collection = client.get_collection(name=COLLECTION_NAME)

    # Convert the question into an embedding
    query_embedding = model.encode(query).tolist()

    # Search for the most similar chunks
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    # Display results
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for i in range(len(documents)):
        print("=" * 70)
        print(f"RESULT {i + 1}")
        print(f"Page: {metadatas[i]['page_number']}")
        print(f"Distance: {distances[i]:.4f}")
        print()
        print(documents[i])

    print("=" * 70)


if __name__ == "__main__":
    question = input("\nEnter your question: ")

    search(question)