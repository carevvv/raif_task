"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class ReceiptExtracted(BaseModel):
    """Schema for extracted receipt fields from LLM."""
    vendor: Optional[str] = None
    date: Optional[str] = None
    total: Optional[float] = None
    currency: Optional[str] = None
    items: List[dict] = Field(default_factory=list)
    tax_id: Optional[str] = None
    payment_method: Optional[str] = None
    raw_confidence: str = "low"
    notes: Optional[str] = None


class ReceiptClassification(BaseModel):
    """Schema for receipt classification from LLM."""
    category: str = "прочее"
    tax_deduction_possible: str = "maybe"
    reasoning_short: str = ""
    required_documents: List[str] = Field(default_factory=list)


class TemplateGeneration(BaseModel):
    """Schema for generated email template from LLM."""
    subject: str
    body: str


class ReceiptResponse(BaseModel):
    """Schema for receipt API response."""
    id: int
    filename: str
    upload_ts: datetime
    raw_text: Optional[str] = None
    vendor: Optional[str] = None
    date: Optional[str] = None
    total: Optional[float] = None
    currency: Optional[str] = None
    category: Optional[str] = None
    tax_deduction_possible: Optional[str] = None
    llm_summary: Optional[str] = None
    llm_details: Optional[dict] = None
    processed: bool
    processing_error: Optional[str] = None
    extra_meta: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ReceiptListResponse(BaseModel):
    """Schema for paginated receipt list."""
    items: List[ReceiptResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SearchResult(BaseModel):
    """Schema for search result with similarity score."""
    receipt: ReceiptResponse
    similarity_score: float


class SearchResponse(BaseModel):
    """Schema for search API response."""
    query: str
    results: List[SearchResult]


class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str
    timestamp: datetime
    version: str = "1.0.0"
