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


@router.post("/query", response_model=QueryResponse)
async def query_assistant(request: QueryRequest):

    try:
        # 1. Retrieve relevant passages from the Patents Act
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

        # 2. Build the evidence supplied to Gemini
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

TEXT:
{document["text"]}
"""
            )

        evidence = "\n".join(evidence_parts)

        # 3. Tell Gemini to answer ONLY from retrieved evidence
        prompt = f"""
You are an Indian legal information assistant.

Answer the user's question using ONLY the authoritative
document excerpts provided below.

USER QUESTION:
{request.query}

JURISDICTION:
{request.jurisdiction}

RESPONSE LANGUAGE:
{request.language}

AUTHORITATIVE DOCUMENT EXCERPTS:
{evidence}

RULES:
1. Use only the information contained in the excerpts.
2. Do not invent sections, laws, cases, dates, or legal conclusions.
3. If the excerpts do not contain enough information to answer,
   clearly say that the available evidence is insufficient.
4. Give a concise and understandable answer.
5. Mention relevant section numbers when they are present
   in the supplied text.
6. Do not claim that something is legally true unless supported
   by the supplied excerpts.
"""

        # 4. Generate the grounded answer
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        answer = response.text.strip()

        # 5. Build citations from the retrieved evidence
        citations = []

        for document in retrieved_documents:
            citations.append(
                {
                    "source_name": document["source_name"],
                    "page_number": document["page_number"],
                    "section": None,
                    "highlight_text": document["text"]
                }
            )

        # 6. Return answer + evidence citations
        return QueryResponse(
            answer=answer,
            citations=citations,
            confidence="medium",
            needs_human_review=True
        )

    except Exception as exc:
        print(f"Query error: {exc}")

        raise HTTPException(
            status_code=500,
            detail="Unable to process the legal query."
        )