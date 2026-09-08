from .retrieval import retrieve_documents


if __name__ == "__main__":

    tests = [
        (
            "india",
            "What is the purpose of the Patents Act, 1970?"
        ),
        (
            "international",
            "What is the purpose of the TRIPS Agreement?"
        ),
        (
            "india",
            "What does Section 22 provide regarding patents?"
        ),
    ]

    print("=" * 70)
    print("RAG METADATA VALIDATION")
    print("=" * 70)

    for index, (jurisdiction, question) in enumerate(
        tests,
        start=1
    ):

        print()
        print(f"TEST {index}")
        print(f"Question: {question}")
        print(f"Jurisdiction: {jurisdiction}")
        print("-" * 70)

        results = retrieve_documents(
            question,
            jurisdiction,
            top_k=3
        )

        if not results:
            print("No results found.")
            continue

        for result_index, result in enumerate(
            results,
            start=1
        ):

            print(f"\nResult {result_index}")

            metadata_fields = {
                "source_name": result.get("source_name"),
                "source_file": result.get("source_file"),
                "document_id": result.get("document_id"),
                "jurisdiction": result.get("jurisdiction"),
                "page_number": result.get("page_number"),
                "section": result.get("section"),
            }

            for field, value in metadata_fields.items():

                status = "OK" if value is not None else "MISSING"

                print(
                    f"{field}: {value} [{status}]"
                )

    print()
    print("=" * 70)
    print("METADATA VALIDATION COMPLETE")
    print("=" * 70)