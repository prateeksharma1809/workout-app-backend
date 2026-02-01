from dataclasses import dataclass
from typing import Optional
from fastapi import Request


@dataclass
class PaginationParams:
    offset: int
    limit: int


@dataclass
class PaginationMeta:
    total: int
    offset: int
    limit: int
    request: Request  # inject the current request

    @property
    def base_url(self) -> str:
        # Builds full URL without any query params
        # e.g. http://localhost:8000/api/v1/exercises
        return str(self.request.base_url).rstrip("/") + self.request.url.path

    @property
    def current_page(self) -> int:
        return (self.offset // self.limit) + 1

    @property
    def total_pages(self) -> int:
        return (self.total + self.limit - 1) // self.limit

    @property
    def previous_page(self) -> Optional[str]:
        if self.offset <= 0:
            return None
        params = dict(self.request.query_params)
        params["offset"] = str(max(0, self.offset - self.limit))
        params["limit"] = str(self.limit)
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.base_url}?{query_string}"

    @property
    def next_page(self) -> Optional[str]:
        if self.offset + self.limit >= self.total:
            return None
        params = dict(self.request.query_params)
        params["offset"] = str(self.offset + self.limit)
        params["limit"] = str(self.limit)
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.base_url}?{query_string}"
    def to_dict(self) -> dict:
        return {
            "totalExercises": self.total,
            "totalPages": self.total_pages,
            "currentPage": self.current_page,
            "previousPage": self.previous_page,
            "nextPage": self.next_page,
        }


def build_response(data: list, meta: PaginationMeta) -> dict:
    return {
        "success": True,
        "metadata": meta.to_dict(),
        "data": data,
    }