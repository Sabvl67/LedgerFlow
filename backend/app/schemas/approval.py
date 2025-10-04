from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.approval import ApprovalStatus


class ApprovalBase(BaseModel):
    invoice_id: int
    required_role: str
    approval_order: int = 1


class ApprovalCreate(ApprovalBase):
    pass


class ApprovalUpdate(BaseModel):
    status: ApprovalStatus
    comments: Optional[str] = None


class ApprovalResponse(ApprovalBase):
    id: int
    approver_id: Optional[int] = None
    status: ApprovalStatus
    comments: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
