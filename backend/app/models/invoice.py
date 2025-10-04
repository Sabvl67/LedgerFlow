from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
import enum


class InvoiceStatus(str, enum.Enum):
    PENDING_EXTRACTION = "pending_extraction"
    PENDING_VALIDATION = "pending_validation"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    SYNCED = "synced"


class InvoiceType(str, enum.Enum):
    ACCOUNTS_PAYABLE = "accounts_payable"
    ACCOUNTS_RECEIVABLE = "accounts_receivable"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, index=True)
    invoice_type = Column(SQLEnum(InvoiceType), nullable=False)
    vendor_name = Column(String)
    customer_name = Column(String)
    invoice_date = Column(DateTime)
    due_date = Column(DateTime)
    total_amount = Column(Float)
    tax_amount = Column(Float)
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.PENDING_EXTRACTION)
    file_url = Column(String)
    raw_ocr_data = Column(JSON)
    extraction_confidence = Column(Float)  # OCR confidence score
    created_by = Column(Integer, ForeignKey("users.id"))
    validated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    created_by_user = relationship("User", foreign_keys=[created_by], back_populates="invoices")
    line_items = relationship("LineItem", back_populates="invoice", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="invoice", cascade="all, delete-orphan")


class LineItem(Base):
    __tablename__ = "line_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    description = Column(Text)
    category = Column(String)
    quantity = Column(Float)
    unit_price = Column(Float)
    amount = Column(Float)
    tax_rate = Column(Float)
    confidence_score = Column(Float)  # Individual line item extraction confidence
    created_at = Column(DateTime, default=datetime.utcnow)

    invoice = relationship("Invoice", back_populates="line_items")
