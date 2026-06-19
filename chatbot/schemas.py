from ninja import Schema
from typing import List


class ChatRequestSchema(Schema):
    question: str
    session_id: str | None = None


class SourceSchema(Schema):
    file: str
    page: int


class ChatResponseData(Schema):
    answer: str
    sources: List[SourceSchema]
    session_id: str


class IngestResponseData(Schema):
    files_processed: int
    chunks_stored: int
