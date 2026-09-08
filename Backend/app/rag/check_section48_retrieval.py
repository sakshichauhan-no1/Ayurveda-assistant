from app.rag.retrieval import (
    collection,
    model,
    CANDIDATE_COUNT,
)


QUERY = "What rights does a patent grant to the patent holder?"
JURISDICTION = "india"


def contains_section_48(document):
    text = document.lower()

    return (
        "48. rights of patentees" in text
        or "exclusive right to prevent third parties" in text
    )


def main():

    print("=" * 70)
    print("SECTION 48 RETRIEVAL DIAGNOSTIC - CORRECTED")
    print("=" * 70)

    print(f"\nQuery: {QUERY}")
    print(f"Jurisdiction: {JURISDICTION}")
    print(f"Candidate count: {CANDIDATE_COUNT}")

    # -------------------------------------------------
    # PART 1
    # Find ALL chunks containing actual Section 48
    # content anywhere in the chunk.
    # -------------------------------------------------

    print("\n" + "-" * 70)
    print("PART 1: Finding actual Section 48 chunks")
    print("-" * 70)

    all_results = collection.get(
        where={"jurisdiction": JURISDICTION},
        include=["documents", "metadatas"]
    )

    all_documents = all_results.get("documents", [])
    all_metadatas = all_results.get("metadatas", [])

    section48_chunks = []

    for document, metadata in zip(
        all_documents,
        all_metadatas
    ):
        if contains_section_48(document):

            section48_chunks.append(
                {
                    "text": document,
                    "metadata": metadata
                }
            )

    print(f"\nTotal Indian chunks checked: {len(all_documents)}")
    print(f"Actual Section 48-related chunks found: {len(section48_chunks)}")

    for i, item in enumerate(section48_chunks, start=1):

        metadata = item["metadata"]

        print("\n" + "-" * 60)
        print(f"SECTION 48 CHUNK #{i}")
        print("-" * 60)

        print(f"Page: {metadata.get('page_number')}")
        print(f"Source: {metadata.get('source_name')}")
        print(f"Section metadata: {metadata.get('section')}")

        print("\nText:")
        print(item["text"][:1500])

    # -------------------------------------------------
    # PART 2
    # Run exactly the same semantic search used by
    # retrieve_documents().
    # -------------------------------------------------

    print("\n" + "-" * 70)
    print("PART 2: Checking semantic top-50 candidates")
    print("-" * 70)

    query_embedding = model.encode(QUERY).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=CANDIDATE_COUNT,
        where={"jurisdiction": JURISDICTION}
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    found_section48 = False

    for rank, (document, metadata, distance) in enumerate(
        zip(documents, metadatas, distances),
        start=1
    ):

        if contains_section_48(document):

            found_section48 = True

            print("\n" + "-" * 60)
            print("ACTUAL SECTION 48 FOUND IN SEMANTIC RESULTS")
            print("-" * 60)

            print(f"Rank: {rank}")
            print(f"Distance: {distance:.4f}")
            print(f"Page: {metadata.get('page_number')}")
            print(f"Source: {metadata.get('source_name')}")
            print(f"Section metadata: {metadata.get('section')}")

            print("\nText:")
            print(document[:1500])

    if not found_section48:
        print("\nACTUAL Section 48 was NOT found in top 50.")

    # -------------------------------------------------
    # PART 3
    # Print top 20 results.
    # -------------------------------------------------

    print("\n" + "-" * 70)
    print("PART 3: Top 20 semantic candidates")
    print("-" * 70)

    for rank, (document, metadata, distance) in enumerate(
        zip(
            documents[:20],
            metadatas[:20],
            distances[:20]
        ),
        start=1
    ):

        print(
            f"\n#{rank} | "
            f"Distance: {distance:.4f} | "
            f"Page: {metadata.get('page_number')} | "
            f"Section: {metadata.get('section')}"
        )

        print(
            f"Source: {metadata.get('source_name')}"
        )

        preview = document.replace("\n", " ")

        print(f"Text: {preview[:350]}")


if __name__ == "__main__":
    main()