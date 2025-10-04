from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models import User, Invoice, Approval, ApprovalStatus, InvoiceStatus
from app.schemas import ApprovalCreate, ApprovalResponse, ApprovalUpdate
from app.api.auth import get_current_user
from app.services import quickbooks_service

router = APIRouter(prefix="/api/approvals", tags=["approvals"])


@router.post("/", response_model=ApprovalResponse)
def create_approval(
    approval_data: ApprovalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create approval request for an invoice
    Part of role-based approval workflow
    """
    # Check if invoice exists
    invoice = db.query(Invoice).filter(Invoice.id == approval_data.invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Only admin can create approval requests
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    # Create approval
    approval = Approval(
        invoice_id=approval_data.invoice_id,
        required_role=approval_data.required_role,
        approval_order=approval_data.approval_order,
        status=ApprovalStatus.PENDING
    )

    db.add(approval)

    # Update invoice status
    invoice.status = InvoiceStatus.PENDING_APPROVAL

    db.commit()
    db.refresh(approval)

    return approval


@router.get("/", response_model=List[ApprovalResponse])
def list_approvals(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List approval requests
    Role-based: users see approvals relevant to their role
    """
    query = db.query(Approval)

    # Filter by status if provided
    if status_filter:
        query = query.filter(Approval.status == status_filter)

    # Filter by role - users only see approvals for their role
    if current_user.role != "admin":
        query = query.filter(Approval.required_role == current_user.role)

    approvals = query.offset(skip).limit(limit).all()
    return approvals


@router.get("/{approval_id}", response_model=ApprovalResponse)
def get_approval(
    approval_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get approval details"""
    approval = db.query(Approval).filter(Approval.id == approval_id).first()

    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")

    # Check permissions
    if current_user.role not in ["admin"] and approval.required_role != current_user.role:
        raise HTTPException(status_code=403, detail="Not authorized")

    return approval


@router.put("/{approval_id}", response_model=ApprovalResponse)
def update_approval(
    approval_id: int,
    approval_update: ApprovalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update approval status (approve/reject)
    Role-based approval: only users with matching role can approve
    """
    approval = db.query(Approval).filter(Approval.id == approval_id).first()

    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")

    # Check if user has the required role
    if current_user.role != approval.required_role and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail=f"Only users with role '{approval.required_role}' can approve this"
        )

    # Update approval
    approval.status = approval_update.status
    approval.comments = approval_update.comments
    approval.approver_id = current_user.id

    # Update invoice status based on approval
    invoice = db.query(Invoice).filter(Invoice.id == approval.invoice_id).first()

    if approval_update.status == ApprovalStatus.APPROVED:
        # Check if all approvals are complete
        all_approvals = db.query(Approval).filter(
            Approval.invoice_id == approval.invoice_id
        ).all()

        all_approved = all(a.status == ApprovalStatus.APPROVED for a in all_approvals)

        if all_approved:
            invoice.status = InvoiceStatus.APPROVED

            # Sync to QuickBooks if approved
            # Note: In production, this would use stored OAuth tokens
            # For now, this is a stub showing the integration point
            sync_result = quickbooks_service.sync_invoice(
                invoice_data={
                    "invoice_number": invoice.invoice_number,
                    "invoice_date": str(invoice.invoice_date) if invoice.invoice_date else None,
                    "due_date": str(invoice.due_date) if invoice.due_date else None,
                    "customer_name": invoice.customer_name,
                    "line_items": [
                        {
                            "description": li.description,
                            "quantity": li.quantity,
                            "unit_price": li.unit_price,
                            "amount": li.amount
                        }
                        for li in invoice.line_items
                    ]
                },
                access_token=None,  # Would be retrieved from user's stored tokens
                realm_id=None  # Would be retrieved from user's QuickBooks connection
            )

            if sync_result.get("status") == "success":
                invoice.status = InvoiceStatus.SYNCED

    elif approval_update.status == ApprovalStatus.REJECTED:
        invoice.status = InvoiceStatus.REJECTED

    db.commit()
    db.refresh(approval)

    return approval


@router.get("/pending/count")
def get_pending_approvals_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of pending approvals for current user's role"""
    query = db.query(Approval).filter(Approval.status == ApprovalStatus.PENDING)

    if current_user.role != "admin":
        query = query.filter(Approval.required_role == current_user.role)

    count = query.count()
    return {"count": count}
