from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
import enum


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    approver_id = Column(Integer, ForeignKey("users.id"))
    status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING)
    comments = Column(Text)
    required_role = Column(String)  # Role required to approve this level
    approval_order = Column(Integer)  # For multi-level approvals
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    invoice = relationship("Invoice", back_populates="approvals")
    approver = relationship("User", back_populates="approvals")
