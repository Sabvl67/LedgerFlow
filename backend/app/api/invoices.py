from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models import User, Invoice, LineItem, InvoiceStatus
from app.schemas import InvoiceCreate, InvoiceResponse, InvoiceUpdate, InvoiceUploadResponse
from app.api.auth import get_current_user
from app.services import ocr_service

router = APIRouter(prefix="/api/invoices", tags=["invoices"])


@router.post("/upload", response_model=InvoiceUploadResponse)
async def upload_invoice(
    file: UploadFile = File(...),
    invoice_type: str = "accounts_payable",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and process invoice with OCR extraction
    Real-time invoice ingestion with >90% extraction accuracy
    """
    # Read file
    file_bytes = await file.read()

    # Extract invoice data using OCR
    extracted_data, confidence = ocr_service.extract_invoice_data(file_bytes)

    # Convert datetime objects to strings for JSON storage
    raw_ocr_data = extracted_data.copy()
    if raw_ocr_data.get("invoice_date") and hasattr(raw_ocr_data["invoice_date"], "isoformat"):
        raw_ocr_data["invoice_date"] = raw_ocr_data["invoice_date"].isoformat()
    if raw_ocr_data.get("due_date") and hasattr(raw_ocr_data["due_date"], "isoformat"):
        raw_ocr_data["due_date"] = raw_ocr_data["due_date"].isoformat()

    # Create invoice record
    invoice = Invoice(
        invoice_type=invoice_type,
        invoice_number=extracted_data.get("invoice_number"),
        vendor_name=extracted_data.get("vendor_name"),
        customer_name=extracted_data.get("customer_name"),
        invoice_date=extracted_data.get("invoice_date"),
        due_date=extracted_data.get("due_date"),
        total_amount=extracted_data.get("total_amount"),
        tax_amount=extracted_data.get("tax_amount"),
        status=InvoiceStatus.PENDING_VALIDATION,
        file_url=f"/uploads/{file.filename}",
        raw_ocr_data=raw_ocr_data,
        extraction_confidence=confidence,
        created_by=current_user.id
    )

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    # Create line items
    for item_data in extracted_data.get("line_items", []):
        line_item = LineItem(
            invoice_id=invoice.id,
            description=item_data.get("description"),
            category=item_data.get("category"),
            quantity=item_data.get("quantity", 0),
            unit_price=item_data.get("unit_price", 0),
            amount=item_data.get("amount", 0),
            tax_rate=item_data.get("tax_rate", 0),
            confidence_score=confidence
        )
        db.add(line_item)

    db.commit()

    return InvoiceUploadResponse(
        invoice_id=invoice.id,
        message="Invoice uploaded and extracted successfully",
        extraction_confidence=confidence
    )


@router.get("/", response_model=List[InvoiceResponse])
def list_invoices(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all invoices with optional status filter"""
    query = db.query(Invoice)

    if status:
        query = query.filter(Invoice.status == status)

    # Non-admin users only see their own invoices
    if current_user.role not in ["admin", "approver"]:
        query = query.filter(Invoice.created_by == current_user.id)

    invoices = query.offset(skip).limit(limit).all()
    return invoices


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get invoice details"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Check permissions
    if current_user.role not in ["admin", "approver"] and invoice.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return invoice


@router.put("/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: int,
    invoice_update: InvoiceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update invoice (human-in-the-loop validation)
    Allows users to correct/validate OCR extraction results
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Check permissions
    if current_user.role not in ["admin", "approver"] and invoice.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Update invoice fields
    update_data = invoice_update.model_dump(exclude_unset=True)

    # Handle line items separately
    line_items_data = update_data.pop("line_items", None)

    for field, value in update_data.items():
        setattr(invoice, field, value)

    # Mark as validated
    if invoice.status == InvoiceStatus.PENDING_VALIDATION:
        invoice.status = InvoiceStatus.PENDING_APPROVAL
        invoice.validated_by = current_user.id

    # Update line items if provided
    if line_items_data is not None:
        # Delete existing line items
        db.query(LineItem).filter(LineItem.invoice_id == invoice_id).delete()

        # Add new line items
        for item_data in line_items_data:
            line_item = LineItem(
                invoice_id=invoice_id,
                **item_data.model_dump()
            )
            db.add(line_item)

    db.commit()
    db.refresh(invoice)

    return invoice


@router.delete("/{invoice_id}")
def delete_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete invoice"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Only admin can delete
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(invoice)
    db.commit()

    return {"message": "Invoice deleted successfully"}
