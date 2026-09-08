import chromadb

CHROMA_DIR = "app/data/vector_db"
COLLECTION_NAME = "legal_documents"

client = chromadb.PersistentClient(path=CHROMA_DIR)

collection = client.get_collection(
    name=COLLECTION_NAME
)

results = collection.get(
    where={
        "jurisdiction": "india"
    },
    include=["documents", "metadatas"]
)

print("=" * 60)
print("SEARCHING VECTOR DATABASE FOR SECTION 22")
print("=" * 60)

found = False

for text, metadata in zip(
    results["documents"],
    results["metadatas"]
):

    if "22. Term of copyright" in text:
        found = True

        print("\nFOUND SECTION 22!")
        print("-" * 60)

        print("Source:", metadata.get("source_name"))
        print("Page:", metadata.get("page_number"))
        print("Document ID:", metadata.get("document_id"))

        print("\nTEXT:")
        print(text)

        print("-" * 60)

if not found:
    print("\nSECTION 22 WAS NOT FOUND IN THE VECTOR DATABASE.")

print("\nTotal Indian chunks checked:", len(results["documents"]))