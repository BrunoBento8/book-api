from pydantic import BaseModel, Field
from typing import Optional, Any, Dict


class PaginationMeta(BaseModel):
    """Pagination metadata for list responses"""
    page: int
    page_size: int
    total_items: int
    total_pages: int


class SuccessResponse(BaseModel):
    """Standard success response wrapper"""
    status: str = "success"
    data: Any
    meta: Optional[PaginationMeta] = None


class ErrorDetail(BaseModel):
    """Error detail information"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Standard error response wrapper"""
    status: str = "error"
    error: ErrorDetail
