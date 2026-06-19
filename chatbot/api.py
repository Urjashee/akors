from ninja import Router
from django.conf import settings

from accounts.schemas import SuccessSchema, ErrorSchema
from chatbot.schemas import ChatRequestSchema, ChatResponseData, IngestResponseData
from chatbot.services import answer_question, ingest_documents, _get_vector_store

router = Router(tags=["chatbot"])


@router.post(
    "/",
    response={200: SuccessSchema[ChatResponseData], 400: ErrorSchema},
)
def chat(request, payload: ChatRequestSchema):
    try:
        result = answer_question(
            question=payload.question,
            session_id=payload.session_id,
            user=request.user,
        )
        return 200, {
            "status": "SUCCESS",
            "message": "Answer generated successfully.",
            "data": result,
        }
    except Exception as e:
        return 400, {
            "status": "ERROR",
            "message": str(e),
        }


@router.get(
    "/debug-scores/",
    auth=None,
    response={200: dict},
)
def debug_scores(request, question: str):
    vs = _get_vector_store()
    docs_with_scores = vs.similarity_search_with_relevance_scores(question, k=5)
    return 200, {
        "results": [
            {"score": round(score, 4), "file": doc.metadata.get("file", ""), "page": doc.metadata.get("page", 0), "preview": doc.page_content[:100]}
            for doc, score in docs_with_scores
        ]
    }


@router.post(
    "/ingest/",
    response={200: SuccessSchema[IngestResponseData], 400: ErrorSchema},
)
def ingest(request):
    try:
        result = ingest_documents()
        return 200, {
            "status": "SUCCESS",
            "message": f"Ingested {result['files_processed']} file(s), {result['chunks_stored']} chunk(s).",
            "data": result,
        }
    except Exception as e:
        return 400, {
            "status": "ERROR",
            "message": str(e),
        }
