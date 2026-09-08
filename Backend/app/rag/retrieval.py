import re

import chromadb
from sentence_transformers import SentenceTransformer


CHROMA_DIR = "app/data/vector_db"

COLLECTION_NAME = "legal_documents"

MODEL_NAME = "all-MiniLM-L6-v2"

# Maximum semantic distance allowed.
# Lower distance = more semantically relevant.
MAX_DISTANCE = 1.00

# Retrieve more candidates first, then rank and return the best ones.
CANDIDATE_COUNT = 100


# Load the embedding model once when the application starts.
model = SentenceTransformer(MODEL_NAME)


# Connect to the existing ChromaDB database.
client = chromadb.PersistentClient(path=CHROMA_DIR)

collection = client.get_collection(
    name=COLLECTION_NAME
)


def extract_requested_section(query: str):
    """
    Detect whether the user explicitly asked for a section number.

    Examples:
        "What does Section 4 say?"
        -> "4"

        "Explain section 48"
        -> "48"

        "What are not patentable inventions?"
        -> None
    """

    match = re.search(
        r"\bsection\s+(\d+[A-Za-z]?)\b",
        query,
        re.IGNORECASE
    )

    if match:
        return match.group(1)

    return None


def extract_sections(text: str):
    """
    Extract actual legal section headings from a chunk.

    Examples recognized:
        1. Short title, extent and commencement.—
        48. Rights of patentees.—
        50. Rights of co-owners of patents.—
        101. Rights of third parties...—

    Amendment footnotes such as:
        1. Subs. by Act 38 of 2002...
        2. Sub-clause (i) omitted...
        3. Ins. by Act 38 of 2002...

    are ignored because they do not contain a legal-heading dash.
    """

    pattern = r"(?m)^\s*(?:\d+\[)?(\d+[A-Za-z]?)\.\s+([^\n]{2,200})[—–-]"

    matches = re.findall(pattern, text)

    sections = []

    for number, heading in matches:
        # Ignore common amendment-footnote text.
        heading_lower = heading.strip().lower()

        if heading_lower.startswith((
            "subs.",
            "sub-clause",
            "ins.",
            "omitted",
            "the words",
        )):
            continue

        section = f"Section {number}"

        if section not in sections:
            sections.append(section)

    return sections

def section_matches(
    query_section,
    document_section
):
    """
    Check whether the section requested by the user
    matches the section identified in the retrieved document.
    """

    if not query_section or not document_section:
        return False

    document_number = re.search(
        r"Section\s+(\d+[A-Za-z]?)",
        document_section,
        re.IGNORECASE
    )

    if not document_number:
        return False

    return (
        query_section.lower()
        == document_number.group(1).lower()
    )

def calculate_confidence(
    distance,
    section_match=False,
    same_source_count=1,
    substantive_evidence=False
):
    """
    Calculate retrieval/evidence confidence.

    This is NOT legal correctness confidence.
    It measures how strongly the retrieved evidence supports
    the retrieval result.
    """

    # Convert semantic distance into a basic similarity score.
    similarity = max(
        0.0,
        min(1.0, 1.0 - distance)
    )

    confidence = similarity

    # Explicit section match is strong evidence.
    if section_match:
        confidence += 0.25

    # Multiple results from the same source provide
    # additional supporting evidence.
    if same_source_count >= 3:
        confidence += 0.10
    elif same_source_count == 2:
        confidence += 0.05

    # Recognizable substantive legal wording.
    if substantive_evidence:
        confidence += 0.05

    confidence = max(
        0.0,
        min(1.0, confidence)
    )

    if confidence >= 0.75:
        level = "High"
        human_verification_needed = "Low"
    elif confidence >= 0.50:
        level = "Medium"
        human_verification_needed = "Medium"
    else:
        level = "Low"
        human_verification_needed = "High"

    return (
        round(confidence, 3),
        level,
        human_verification_needed
    )


def retrieve_documents(
    query: str,
    jurisdiction: str,
    top_k: int = 5
):
    """
    Retrieve relevant chunks from the legal document database.

    Process:
        1. Filter documents by jurisdiction.
        2. Retrieve a larger candidate pool.
        3. Remove weak semantic matches.
        4. Detect section numbers.
        5. Boost an explicitly requested section.
        6. Sort by ranking score.
        7. Return the best top_k documents.
    """

    # -------------------------------------------------
    # Validate jurisdiction
    # -------------------------------------------------

    jurisdiction = jurisdiction.lower().strip()

    if jurisdiction not in {
        "india",
        "international"
    }:
        raise ValueError(
            "Jurisdiction must be 'india' "
            "or 'international'."
        )

    # -------------------------------------------------
    # Create query embedding
    # -------------------------------------------------

    query_embedding = model.encode(
        query
    ).tolist()

    # Retrieve more candidates than we ultimately return.
    candidate_count = max(
        top_k,
        CANDIDATE_COUNT
    )

    # -------------------------------------------------
    # Jurisdiction-filtered vector search
    # -------------------------------------------------

    results = collection.query(
        query_embeddings=[
            query_embedding
        ],

        n_results=candidate_count,

        where={
            "jurisdiction": jurisdiction
        }
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]

    requested_section = (
        extract_requested_section(query)
    )

    retrieved_documents = []

    # -------------------------------------------------
    # Rank retrieved documents
    # -------------------------------------------------

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        # Ignore weak semantic matches.
        if distance > MAX_DISTANCE:
            continue

        detected_sections = extract_sections(document)

        section_match = (
            requested_section is not None
            and any(
                section_matches(
                    requested_section,
                    section
                )
                for section in detected_sections
            )
        )

        if section_match:
            detected_section = f"Section {requested_section}"
        elif detected_sections:
            detected_section = detected_sections[0]
        else:
            detected_section = None

        # Lower score = better.
        ranking_score = distance

        if section_match:
            ranking_score -= 0.50

        # Do not apply a generic patent-rights boost here.
        # A generic phrase such as "exclusive right to prevent
        # third parties" can incorrectly rank patent text above
        # copyright/trademark results.
        #
        # Explicit section matches are already boosted above.

        retrieved_documents.append(
            {
                "text": document,

                "source_name": metadata.get(
                    "source_name",
                    "Unknown legal document"
                ),

                "source_file": metadata.get(
                    "source_file"
                ),

                "document_id": metadata.get(
                    "document_id"
                ),

                "jurisdiction": metadata.get(
                    "jurisdiction"
                ),

                "page_number": metadata.get(
                    "page_number"
                ),

                "section": detected_section,

                "distance": distance,

                "ranking_score": ranking_score,

                "section_match": section_match
            }
        )

    # -------------------------------------------------
    # Best results first
    # -------------------------------------------------

        # -------------------------------------------------
    # Section-aware fallback
    # -------------------------------------------------
    # If the user explicitly requested a section but
    # semantic search did not find it, search the
    # existing ChromaDB documents directly.
    if requested_section and not any(
        item["section_match"] for item in retrieved_documents
    ):
        all_results = collection.get(
            where={"jurisdiction": jurisdiction},
            include=["documents", "metadatas"]
        )

        # Prefer the source documents already identified
        # by semantic search. This prevents Section 22 from
        # another law being selected accidentally.
        semantic_sources = {
            item["source_name"]
            for item in retrieved_documents
            if item.get("source_name")
        }
        
        # Prefer the legal source that matches the subject
        # explicitly mentioned in the user's question.
        query_lower = query.lower()
        
        if "patent" in query_lower:
            patent_sources = {
                source
                for source in semantic_sources
                if "patent" in source.lower()
            }
        
            if patent_sources:
                semantic_sources = patent_sources
        
        elif "copyright" in query_lower:
            copyright_sources = {
                source
                for source in semantic_sources
                if "copyright" in source.lower()
            }
        
            if copyright_sources:
                semantic_sources = copyright_sources
        
        elif "trademark" in query_lower or "trade mark" in query_lower:
            trademark_sources = {
                source
                for source in semantic_sources
                if "trademark" in source.lower()
                or "trade mark" in source.lower()
            }
        
            if trademark_sources:
                semantic_sources = trademark_sources

        fallback_documents = []

        for document, metadata in zip(
            all_results.get("documents", []),
            all_results.get("metadatas", [])
        ):
            source_name = metadata.get("source_name")

            if semantic_sources and source_name not in semantic_sources:
                continue

            detected_sections = extract_sections(document)

            if any(
                section_matches(requested_section, section)
                for section in detected_sections
            ):
                fallback_documents.append(
                    {
                        "text": document,
                        "source_name": source_name,
                        "source_file": metadata.get("source_file"),
                        "document_id": metadata.get("document_id"),
                        "jurisdiction": metadata.get("jurisdiction"),
                        "page_number": metadata.get("page_number"),
                        "section": f"Section {requested_section}",
                        "distance": 0.0,
                        "ranking_score": -1.0,
                        "section_match": True
                    }
                )

        retrieved_documents.extend(fallback_documents)

    # -------------------------------------------------
    # Best results first
    # -------------------------------------------------
    retrieved_documents.sort(
        key=lambda x: x["ranking_score"]
    )
    final_results = retrieved_documents[:top_k]
    # -------------------------------------------------
    # Section 48 evidence completion
    # -------------------------------------------------
    
    # Section 48 is split across PDF chunks:
    # one chunk contains the heading and another contains
    # the actual rights under clauses (a) and (b).
    #
    # When the user explicitly asks about Section 48,
    # retrieve the stored chunk containing the substantive
    # rights and include it as evidence.
    
    if requested_section == "48":
    
        has_rights_evidence = any(
            "exclusive right to prevent third parties"
            in item["text"].lower()
            for item in final_results
        )
    
        if not has_rights_evidence:
        
            section_48_results = collection.get(
                where={"jurisdiction": jurisdiction},
                include=["documents", "metadatas"]
            )
    
            for document, metadata in zip(
                section_48_results.get("documents", []),
                section_48_results.get("metadatas", [])
            ):
    
                text_lower = document.lower()
    
                if (
                    "exclusive right to prevent third parties"
                    in text_lower
                ):
    
                    evidence_item = {
                        "text": document,
                        "source_name": metadata.get(
                            "source_name",
                            "Unknown legal document"
                        ),
                        "source_file": metadata.get(
                            "source_file"
                        ),
                        "document_id": metadata.get(
                            "document_id"
                        ),
                        "jurisdiction": metadata.get(
                            "jurisdiction"
                        ),
                        "page_number": metadata.get(
                            "page_number"
                        ),
                        "section": "Section 48",
                        "distance": 0.0,
                        "ranking_score": -0.90,
                        "section_match": True
                    }
    
                    # Put the substantive Section 48 evidence
                    # at the beginning of the final evidence.
                    final_results.insert(
                        0,
                        evidence_item
                    )
    
                    # Keep exactly top_k results.
                    final_results = final_results[:top_k]
    
                    break
    # Count how many final results come from each source.
    source_counts = {}
    for item in final_results:
        source = item.get("source_name")
        if source:
            source_counts[source] = (
                source_counts.get(source, 0) + 1
            )
    # -------------------------------------------------
    # Calculate confidence and human verification
    # -------------------------------------------------
    for item in final_results:
    
        source_count = source_counts.get(
            item.get("source_name"),
            1
        )
        text_lower = item["text"].lower()
        substantive_evidence = any(
            phrase in text_lower
            for phrase in [
                "shall",
                "rights of",
                "grant of",
                "infringement",
                "protection",
                "registration",
                "obligation",
                "patent",
                "copyright",
                "trade mark"
            ]
        )
        (
            confidence_score,
            confidence_level,
            human_verification_needed
        ) = calculate_confidence(
            distance=item["distance"],
            section_match=item["section_match"],
            same_source_count=source_count,
            substantive_evidence=substantive_evidence
        )
        item["confidence_score"] = confidence_score
        item["confidence_level"] = confidence_level
        item["human_verification_needed"] = (
            human_verification_needed
        )
    return final_results