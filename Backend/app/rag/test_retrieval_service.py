from retrieval import retrieve_documents


if __name__ == "__main__":

    question = input("Enter your legal question: ")

    results = retrieve_documents(question, top_k=5)

    print()
    print("=" * 70)

    for index, result in enumerate(results, start=1):

        print(f"RESULT {index}")
        print(f"Page: {result['page_number']}")
        print(f"Distance: {result['distance']:.4f}")
        print()

        print(result["text"])

        print()
        print("=" * 70)