from math import ceil
from typing import Generic, List, TypeVar

from ninja import Schema

T = TypeVar("T")


class PaginationSchema(Schema):
    current_page: int = 1
    page_size: int = 20


class PaginatedResponseSchema(Schema, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


def paginate_queryset(queryset, current_page: int, page_size: int) -> dict:
    """
    Slice a Django queryset and return a dict matching PaginatedResponseSchema.
    Issues one SELECT COUNT(*) then a LIMIT/OFFSET slice — the full queryset
    is never loaded into memory.
    page_size is clamped to [1, 200].
    """
    page_size = max(1, min(page_size, 200))
    total = queryset.count()
    total_pages = ceil(total / page_size) if total > 0 else 1
    current_page = max(1, min(current_page, total_pages))
    offset = (current_page - 1) * page_size
    items = list(queryset[offset: offset + page_size])
    return {
        "items": items,
        "total": total,
        "current_page": current_page,
        "page_size": page_size,
        "total_pages": total_pages,
    }
