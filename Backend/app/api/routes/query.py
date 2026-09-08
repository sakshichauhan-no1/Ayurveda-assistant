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
    raise RuntimeError(
        "GEMINI_API_KEY was not found in .env"
    )


client = genai.Client(
    api_key=api_key
)

MODEL_NAME = "gemini-3.5-flash"


@router.post(
    "/query",
    response_model=QueryResponse
)
async def query_assistant(
    request: QueryRequest
):

    try:

        # -------------------------------------------------
        # 1. Retrieve relevant legal passages
        # -------------------------------------------------

        retrieved_documents = retrieve_documents(
            request.query,
            request.jurisdiction,
            top_k=5
        )

        if not retrieved_documents:

            return QueryResponse(
                answer=(
                    "I could not find enough relevant "
                    "information in the authoritative "
                    "documents to answer this question."
                ),
                citations=[],
                confidence="Low",
                needs_human_review=True,
                confidence_score=0.0,
                confidence_level="Low",
                human_verification_needed="High"
            )


        # -------------------------------------------------
        # 2. Calculate retrieval confidence
        # -------------------------------------------------

        best_document = retrieved_documents[0]

        confidence_score = best_document.get(
            "confidence_score",
            0.0
        )

        confidence_level = best_document.get(
            "confidence_level",
            "Low"
        )

        human_verification_needed = best_document.get(
            "human_verification_needed",
            "High"
        )


        # -------------------------------------------------
        # 3. Build evidence for Gemini
        # -------------------------------------------------

        evidence_parts = []

        for index, document in enumerate(
            retrieved_documents,
            start=1
        ):

            evidence_parts.append(
                f"""
SOURCE {index}

Source:
{document["source_name"]}

Page:
{document["page_number"]}

Section:
{document.get("section")}

TEXT:
{document["text"]}
"""
            )

        evidence = "\n".join(
            evidence_parts
        )


        # -------------------------------------------------
        # 4. Build grounded Gemini prompt
        # -------------------------------------------------

        prompt = f"""
You are an Indian legal information assistant.

Answer the user's question using ONLY the authoritative
legal excerpts supplied below.

USER QUESTION:
{request.query}

JURISDICTION:
{request.jurisdiction}

RESPONSE LANGUAGE:
{request.language}

AUTHORITATIVE LEGAL EXCERPTS:
{evidence}


RULES:

1. EVIDENCE ONLY

Use only information supported by the supplied excerpts.

2. DO NOT HALLUCINATE

Do not invent:

- sections
- subsections
- Acts
- regulations
- cases
- judgments
- dates
- penalties
- exceptions
- definitions
- legal conclusions

3. INSUFFICIENT INFORMATION

If the supplied excerpts do not contain enough information
to answer the question, clearly say that the available
documents do not provide sufficient information.

Do not use outside knowledge to fill missing information.

4. SECTION NUMBERS

Mention a section number only when it is supported by
the supplied excerpts.

5. SOURCE BOUNDARIES

The supplied excerpts are the only authoritative source
available for this answer.

6. LEGAL ADVICE

Provide general legal information based on the supplied
documents.

Do not present the answer as personalized legal advice.

7. CLARITY

Answer directly and concisely.

Use headings or bullet points when useful.

8. CITATIONS

When explaining a legal rule, identify the relevant
section when that section is present in the evidence.

9. CONFLICTS

If the supplied excerpts appear to conflict, do not
resolve the conflict using outside knowledge.

Clearly identify the conflict.

10. NO OUTSIDE KNOWLEDGE

Do not supplement the answer with your own knowledge.

Before answering, verify that the important claims
are supported by the supplied excerpts.
"""


        # -------------------------------------------------
        # 5. Generate grounded answer
        # -------------------------------------------------

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        answer = response.text.strip()


        # -------------------------------------------------
        # 6. Build citations
        # -------------------------------------------------

        citations = []

        for document in retrieved_documents:

            citations.append(
                {
                    "source_name": document[
                        "source_name"
                    ],

                    "page_number": document[
                        "page_number"
                    ],

                    "section": document.get(
                        "section"
                    ),

                    "highlight_text": document[
                        "text"
                    ]
                }
            )


        # -------------------------------------------------
        # 7. Return final response
        # -------------------------------------------------

        return QueryResponse(
            answer=answer,
            citations=citations,
            confidence=confidence_level,
            needs_human_review=(
                human_verification_needed != "Low"
            ),
            confidence_score=confidence_score,
            confidence_level=confidence_level,
            human_verification_needed=human_verification_needed
        )


    except Exception as exc:

        print(
            f"Query error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to process the legal query."
        )