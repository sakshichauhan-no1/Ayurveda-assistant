import os

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from google import genai

from app.schemas.query import QueryRequest, QueryResponse
from app.rag.retrieval import retrieve_documents


load_dotenv()


router = APIRouter(
    prefix="/api/v1",
    tags=["Query"]
)


api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY was not found in .env")


client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.5-flash"


def calculate_confidence(retrieved_documents):
    """
    Calculate confidence based on the strongest retrieved evidence.

    Lower Chroma distance means stronger semantic similarity.
    This represents retrieval confidence, not legal certainty.
    """

    if not retrieved_documents:
        return "low"

    best_distance = min(
        document["distance"]
        for document in retrieved_documents
    )

    if best_distance <= 0.70:
        return "high"

    if best_distance <= 0.85:
        return "medium"

    return "low"


@router.post("/query", response_model=QueryResponse)
async def query_assistant(request: QueryRequest):

    try:
        # 1. Retrieve relevant passages from the legal database
        retrieved_documents = retrieve_documents(
            request.query,
            top_k=5
        )

        if not retrieved_documents:
            return QueryResponse(
                answer=(
                    "I could not find enough relevant information in "
                    "the authoritative documents to answer this question."
                ),
                citations=[],
                confidence="low",
                needs_human_review=True
            )

        # 2. Calculate retrieval confidence
        confidence = calculate_confidence(
            retrieved_documents
        )

        # 3. Build evidence for Gemini
        evidence_parts = []

        for index, document in enumerate(
            retrieved_documents,
            start=1
        ):
            evidence_parts.append(
                f"""
SOURCE {index}
Source: {document["source_name"]}
Page: {document["page_number"]}
Section: {document.get("section")}
Retrieval distance: {document["distance"]}

TEXT:
{document["text"]}
"""
            )

        evidence = "\n".join(evidence_parts)

        # 4. Build a strict evidence-grounded prompt
        prompt = f"""
You are an Indian legal information assistant.

Your job is to answer the user's question using ONLY the
authoritative legal excerpts supplied below.

The supplied excerpts are the ONLY source of legal information
you may rely on for this answer.

USER QUESTION:
{request.query}

JURISDICTION:
{request.jurisdiction}

RESPONSE LANGUAGE:
{request.language}

AUTHORITATIVE LEGAL EXCERPTS:
{evidence}


STRICT RULES:

1. EVIDENCE ONLY
   Use only facts, rules, sections, and legal information that
   are supported by the supplied excerpts.

2. DO NOT HALLUCINATE
   Never invent:
   - section numbers
   - subsections
   - Acts
   - regulations
   - cases
   - judgments
   - dates
   - legal tests
   - penalties
   - exceptions
   - definitions
   - legal conclusions

3. INSUFFICIENT EVIDENCE
   If the supplied excerpts do not contain enough information
   to answer the question, explicitly say that the available
   documents do not provide sufficient information.

   Do NOT fill missing information using your general knowledge.

4. SECTION NUMBERS
   Mention section numbers only when they are actually supported
   by the supplied excerpts.

5. SOURCE BOUNDARIES
   Do not assume that a law, rule, or principle exists merely
   because it is commonly known.

   If it is not present in the supplied excerpts, do not use it.

6. LEGAL ADVICE
   Provide legal information based on the supplied documents.
   Do not present the response as personalized legal advice.

7. CLARITY
   Answer directly and concisely.
   Use headings or bullet points when they improve readability.

8. CITATION AWARENESS
   When discussing a particular rule or requirement, make it clear
   which section or supplied source supports the statement.

9. CONFLICTS
   If the supplied excerpts appear to contain conflicting
   information, do not resolve the conflict using outside
   knowledge. Clearly identify the conflict.

10. NO OUTSIDE KNOWLEDGE
    Your own prior knowledge must not be used to supplement
    missing information.

Before producing the final answer, internally check every
important legal claim against the supplied excerpts.
"""


        # 5. Generate the grounded answer
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        answer = response.text.strip()

        # 6. Build citations from retrieved evidence
        citations = []

        for document in retrieved_documents:
            citations.append(
                {
                    "source_name": document["source_name"],
                    "page_number": document["page_number"],
                    "section": document.get("section"),
                    "highlight_text": document["text"]
                }
            )

        # 7. Return answer, citations, and confidence
        return QueryResponse(
            answer=answer,
            citations=citations,
            confidence=confidence,
            needs_human_review=True
        )

    except Exception as exc:
        print(f"Query error: {exc}")

        raise HTTPException(
            status_code=500,
            detail="Unable to process the legal query."
        )