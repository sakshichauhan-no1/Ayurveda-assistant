from app.rag.retrieval import collection, model


QUERY = "What rights does a patent grant to the patent holder?"
JURISDICTION = "india"


def main():

    print("=" * 70)
    print("SECTION 48 SIMILARITY DIAGNOSTIC")
    print("=" * 70)

    # Get all Indian chunks
    results = collection.get(
        where={"jurisdiction": JURISDICTION},
        include=["documents", "metadatas"]
    )

    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])

    query_embedding = model.encode(QUERY)

    matches = []

    for document, metadata in zip(documents, metadatas):

        text = document.lower()

        # Identify the two actual Section 48 chunks.
        if (
            "48. rights of patentees" in text
            or "exclusive right to prevent third parties" in text
        ):

            document_embedding = model.encode(document)

            # Cosine similarity
            similarity = (
                query_embedding @ document_embedding
                / (
                    (query_embedding @ query_embedding) ** 0.5
                    * (document_embedding @ document_embedding) ** 0.5
                )
            )

            matches.append(
                {
                    "similarity": float(similarity),
                    "page": metadata.get("page_number"),
                    "text": document
                }
            )

    matches.sort(
        key=lambda x: x["similarity"],
        reverse=True
    )

    print(f"\nSection 48-related chunks found: {len(matches)}")

    for i, match in enumerate(matches, start=1):

        print("\n" + "-" * 60)
        print(f"MATCH #{i}")
        print("-" * 60)

        print(f"Cosine similarity: {match['similarity']:.4f}")
        print(f"Page: {match['page']}")

        print("\nText:")
        print(match["text"][:1800])


if __name__ == "__main__":
    main()