from app.rag.retrieval import collection


def main():

    print("=" * 70)
    print("PATENT ACT SECTIONS 46-50 DIAGNOSTIC")
    print("=" * 70)

    results = collection.get(
        where={
            "$and": [
                {"jurisdiction": "india"},
                {"source_name": "Patentact 1970 India"}
            ]
        },
        include=["documents", "metadatas"]
    )

    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])

    found = []

    for document, metadata in zip(documents, metadatas):

        text = document.lower()

        # Look for actual section headings 46-50.
        if any(
            heading in text
            for heading in [
                "46. form, extent and effect of patent",
                "47. grant of patents to be subject to certain conditions",
                "48. rights of patentees",
                "49. patent rights not infringed",
                "50. rights of co-owners of patents"
            ]
        ):
            found.append(
                (document, metadata)
            )

    print(f"\nMatching chunks found: {len(found)}")

    for i, (document, metadata) in enumerate(found, start=1):

        print("\n" + "-" * 70)
        print(f"MATCH #{i}")
        print("-" * 70)

        print(f"Page: {metadata.get('page_number')}")
        print(f"Section metadata: {metadata.get('section')}")
        print(f"Source: {metadata.get('source_name')}")

        print("\nTEXT:")
        print(document[:2500])


if __name__ == "__main__":
    main()