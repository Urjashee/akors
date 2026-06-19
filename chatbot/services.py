import uuid
from pathlib import Path

from django.conf import settings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_postgres import PGVector
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage

COLLECTION_NAME = "akors_documents"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
RETRIEVER_K = 5
SIMILARITY_THRESHOLD = 0.0
LLM_TEMPERATURE = 0
MAX_HISTORY_TURNS = 5
NOT_FOUND_MSG = "I could not find that information in the documents."

SYSTEM_PROMPT = """You are a document assistant. Answer questions using ONLY the context provided below.

Guidelines:
- You may summarize, explain, or synthesize information from the context.
- Base every statement strictly on what the context contains — do not add outside knowledge or invented facts.
- If the context contains no relevant information to answer the question, respond with exactly: "I could not find that information in the documents."
- If the question is a greeting or small talk with no relation to the documents, respond with exactly: "I could not find that information in the documents."

Previous conversation:
{chat_history}

Context:
{context}
"""

SESSION_STORE: dict[str, ChatMessageHistory] = {}


def _get_session_history(session_id: str) -> ChatMessageHistory:
    if session_id not in SESSION_STORE:
        SESSION_STORE[session_id] = ChatMessageHistory()
    return SESSION_STORE[session_id]


def _get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=settings.OPENAI_API_KEY,
    )


def _get_vector_store() -> PGVector:
    return PGVector(
        embeddings=_get_embeddings(),
        collection_name=COLLECTION_NAME,
        connection=settings.PGVECTOR_CONNECTION_STRING,
        use_jsonb=True,
    )


def ingest_documents(documents_dir: str = None) -> dict:
    if documents_dir is None:
        documents_dir = str(Path(settings.BASE_DIR) / "documents")

    pdf_files = list(Path(documents_dir).glob("*.pdf"))
    if not pdf_files:
        return {"files_processed": 0, "chunks_stored": 0}

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    all_chunks: list[Document] = []
    for pdf_path in pdf_files:
        loader = PyPDFLoader(str(pdf_path))
        pages = loader.load()
        chunks = splitter.split_documents(pages)
        for chunk in chunks:
            chunk.metadata["file"] = Path(chunk.metadata.get("source", "")).name
            chunk.metadata["page"] = chunk.metadata.get("page", 0)
        all_chunks.extend(chunks)

    vector_store = _get_vector_store()
    vector_store.add_documents(all_chunks)

    return {"files_processed": len(pdf_files), "chunks_stored": len(all_chunks)}


def answer_question(question: str, session_id: str = None, user=None) -> dict:
    if not session_id:
        session_id = str(uuid.uuid4())

    history = _get_session_history(session_id)

    # Build chat_history string from last MAX_HISTORY_TURNS turns
    recent_messages = history.messages[-(MAX_HISTORY_TURNS * 2):]
    chat_history = "\n".join(
        f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
        for m in recent_messages
    ) if recent_messages else "None"

    vector_store = _get_vector_store()

    docs_with_scores = vector_store.similarity_search_with_relevance_scores(
        question, k=RETRIEVER_K
    )

    relevant_docs = [doc for doc, score in docs_with_scores if score >= SIMILARITY_THRESHOLD]

    if not relevant_docs:
        history.add_user_message(question)
        history.add_ai_message(NOT_FOUND_MSG)
        return {"answer": NOT_FOUND_MSG, "sources": [], "session_id": session_id}

    llm = ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=LLM_TEMPERATURE,
        openai_api_key=settings.OPENAI_API_KEY,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{question}"),
    ])

    context = "\n\n".join(doc.page_content for doc in relevant_docs)

    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"context": context, "question": question, "chat_history": chat_history})

    history.add_user_message(question)
    history.add_ai_message(answer)

    if answer.strip() == NOT_FOUND_MSG:
        return {"answer": answer, "sources": [], "session_id": session_id}

    seen = set()
    sources = []
    for doc in relevant_docs:
        key = (doc.metadata.get("file", ""), doc.metadata.get("page", 0))
        if key not in seen:
            seen.add(key)
            sources.append({"file": key[0], "page": key[1]})

    if user:
        from chatbot.models import ChatHistory
        ChatHistory.objects.create(
            user=user,
            question=question,
            answer=answer,
            sources=sources,
        )

    return {"answer": answer, "sources": sources, "session_id": session_id}
