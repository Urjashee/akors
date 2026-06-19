# PDF Chatbot using Django, LangChain, OpenAI, PostgreSQL (PGVector) and UV

## Overview

This project implements a Retrieval-Augmented Generation (RAG) chatbot that answers questions from PDF documents stored locally inside the Django project.

### Technology Stack

* Backend: Django
* LLM: OpenAI GPT-4o Mini
* Embeddings: OpenAI text-embedding-3-small
* Vector Database: PostgreSQL + PGVector
* Framework: LangChain
* Package Manager: UV

---

## Architecture

```text
React/Vite Frontend
        │
        ▼
Django API
        │
        ▼
LangChain RAG Pipeline
        │
        ├── OpenAI Embeddings
        ├── PostgreSQL + PGVector
        └── OpenAI Chat Model
        │
        ▼
Answer Returned to Frontend
```

---

## Project Structure

```text
project/
│
├── backend/
│   ├── app/
│   │   ├── views.py
│   │   ├── rag.py
│   │   ├── ingest.py
│   │   └── urls.py
│   │
│   ├── documents/
│   │   ├── policy1.pdf
│   │   ├── policy2.pdf
│   │   └── policy3.pdf
│   │
│   ├── .env
│   ├── manage.py
│   └── pyproject.toml
```


## Install Dependencies

```bash

uv add langchain
uv add langchain-openai
uv add langchain-community
uv add langchain-postgres

uv add pypdf

uv add psycopg[binary]
uv add pgvector

uv add python-dotenv
```

---

## PostgreSQL Setup

Enable PGVector extension:

```sql
CREATE EXTENSION vector;
```

Verify:

```sql
SELECT * FROM pg_extension;
```

Expected result:

```text
vector
```

---

## PDF Ingestion Flow

### Step 1

Read PDFs from:

```text
backend/documents/
```

### Step 2

Extract text using:

```python
PyPDFLoader
```

### Step 3

Split text into chunks:

```python
RecursiveCharacterTextSplitter
```

Recommended settings:

```python
chunk_size = 1000
chunk_overlap = 200
```

### Step 4

Generate embeddings:

```python
OpenAIEmbeddings()
```

### Step 5

Store embeddings in PGVector.

---

## Ingestion Pipeline

```text
PDF
 ↓
Load
 ↓
Split
 ↓
Create Embeddings
 ↓
Store in PGVector
```

---

## Retrieval Flow

When a user asks a question:

```text
Question
 ↓
Generate Embedding
 ↓
Similarity Search
 ↓
Retrieve Relevant Chunks
 ↓
Build Context
 ↓
Send Context + Question to GPT
 ↓
Return Answer
```

---

## Example User Question

```text
What is the cancellation policy?
```

### Retrieved Context

```text
Cancellation requests must be submitted
within 30 days of enrollment...
```

### Prompt Sent to OpenAI

```text
Answer ONLY using the provided context.

Context:
Cancellation requests must be submitted
within 30 days of enrollment...

Question:
What is the cancellation policy?
```

### Response

```text
Cancellation requests must be submitted
within 30 days of enrollment.
```

---

## Django API Endpoint

### Request

```http
POST /api/chat/
```

Body:

```json
{
  "question": "What is the cancellation policy?"
}
```

---

### Response

```json
{
  "answer": "Cancellation requests must be submitted within 30 days.",
  "sources": [
    "policy1.pdf"
  ]
}
```

---

## LangChain Components

### Embeddings

```python
OpenAIEmbeddings
```

Model:

```text
text-embedding-3-small
```

---

### LLM

```python
ChatOpenAI
```

Model:

```text
gpt-4o-mini
```

Temperature:

```python
0
```

---

### Vector Store

```python
PGVector
```

---

### Retriever

```python
vector_store.as_retriever()
```

Recommended:

```python
search_kwargs={"k": 5}
```

---

## Hallucination Prevention

### Rule 1

Only answer from retrieved context.

Prompt:

```text
Answer ONLY using the context provided.
If the answer is not present, say:

"I could not find that information in the documents."
```

---

### Rule 2

Use similarity threshold.

If retrieval score is too low:

```text
I could not find that information in the documents.
```

---

### Rule 3

Return sources.

Example:

```json
{
  "answer": "...",
  "sources": [
    {
      "file": "policy1.pdf",
      "page": 4
    }
  ]
}
```

---

## Future Enhancements

### Phase 2

Conversation Memory

Store:

* User ID
* Question
* Answer
* Timestamp

in PostgreSQL.

---

### Phase 3

Multi-PDF Filtering

Example:

```text
Search only in:

employee_handbook.pdf
```

---

### Phase 4

Hybrid Search

Combine:

* Vector Search
* Keyword Search

for better retrieval accuracy.

---

### Phase 5

LangGraph Workflow

```text
Question
 ↓
Retriever
 ↓
Relevance Check
 ↓
Answer Generation
 ↓
Citation Validation
 ↓
Response
```

---

## Production Recommendations

### Embeddings

```text
text-embedding-3-small
```

### Chat Model

```text
gpt-4o-mini
```

### Database

```text
PostgreSQL + PGVector
```

### Backend

```text
Django REST Framework
```

### Frontend

```text
React + Vite
```

### Package Manager

```text
UV
```

---

## Final Flow

```text
1. Place PDFs in documents folder
2. Run ingestion script
3. Create embeddings
4. Store vectors in PGVector
5. User asks question
6. Retrieve relevant chunks
7. Send context to GPT
8. Return answer + sources
```

This architecture is suitable for a production-grade PDF chatbot and can easily scale from a few PDFs to thousands of documents while maintaining good retrieval quality.
