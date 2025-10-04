from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.invoice import InvoiceStatus, InvoiceType


class LineItemBase(BaseModel):
    description: str
    category: Optional[str] = None
    quantity: float
    unit_price: float
    amount: float
    tax_rate: Optional[float] = 0.0
    confidence_score: Optional[float] = None


class LineItemCreate(LineItemBase):
    pass


class LineItemResponse(LineItemBase):
    id: int
    invoice_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceBase(BaseModel):
    invoice_type: InvoiceType
    invoice_number: Optional[str] = None
    vendor_name: Optional[str] = None
    customer_name: Optional[str] = None
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    total_amount: Optional[float] = None
    tax_amount: Optional[float] = None


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceUpdate(BaseModel):
    invoice_number: Optional[str] = None
    vendor_name: Optional[str] = None
    customer_name: Optional[str] = None
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    total_amount: Optional[float] = None
    tax_amount: Optional[float] = None
    status: Optional[InvoiceStatus] = None
    line_items: Optional[List[LineItemCreate]] = None


class InvoiceResponse(InvoiceBase):
    id: int
    status: InvoiceStatus
    file_url: Optional[str] = None
    extraction_confidence: Optional[float] = None
    created_by: int
    validated_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    line_items: List[LineItemResponse] = []

    class Config:
        from_attributes = True


class InvoiceUploadResponse(BaseModel):
    invoice_id: int
    message: str
    extraction_confidence: float
