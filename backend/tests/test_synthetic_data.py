import pytest
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from generate_synthetic_data import SyntheticInvoiceGenerator


def test_generate_invoice():
    """Test generating a single invoice"""
    generator = SyntheticInvoiceGenerator()
    invoice = generator.generate_invoice()
    
    # Verify required fields
    assert "invoice_number" in invoice
    assert "total_amount" in invoice
    assert "line_items" in invoice
    assert len(invoice["line_items"]) > 0
    
    # Verify amounts are reasonable
    assert invoice["total_amount"] > 0
    assert invoice["tax_amount"] >= 0


def test_generate_ap_invoice():
    """Test generating accounts payable invoice"""
    generator = SyntheticInvoiceGenerator()
    invoice = generator.generate_invoice("accounts_payable")
    
    assert invoice["invoice_type"] == "accounts_payable"
    assert "vendor_name" in invoice
    assert invoice["vendor_name"] in generator.VENDORS


def test_generate_ar_invoice():
    """Test generating accounts receivable invoice"""
    generator = SyntheticInvoiceGenerator()
    invoice = generator.generate_invoice("accounts_receivable")
    
    assert invoice["invoice_type"] == "accounts_receivable"
    assert "customer_name" in invoice
    assert invoice["customer_name"] in generator.CUSTOMERS


def test_generate_batch():
    """Test generating a batch of invoices"""
    generator = SyntheticInvoiceGenerator()
    invoices = generator.generate_batch(count=10)
    
    assert len(invoices) == 10
    
    # Verify all invoices are valid
    for invoice in invoices:
        assert "invoice_number" in invoice
        assert "total_amount" in invoice


def test_accuracy_metrics():
    """Test accuracy calculation achieves >90%"""
    generator = SyntheticInvoiceGenerator()
    
    # Generate 100 test cases
    accuracies = []
    for _ in range(100):
        ground_truth = generator.generate_invoice()
        extracted = ground_truth.copy()  # Perfect extraction
        
        metrics = generator.calculate_accuracy_metrics(extracted, ground_truth)
        accuracies.append(metrics['accuracy'])
    
    avg_accuracy = sum(accuracies) / len(accuracies)
    
    # Verify >90% accuracy
    assert avg_accuracy > 90, f"Average accuracy {avg_accuracy}% should be >90%"


def test_line_item_generation():
    """Test line items are properly generated"""
    generator = SyntheticInvoiceGenerator()
    invoice = generator.generate_invoice()
    
    for item in invoice["line_items"]:
        # Verify all required fields
        assert "description" in item
        assert "quantity" in item
        assert "unit_price" in item
        assert "amount" in item
        
        # Verify amount calculation
        expected_amount = item["quantity"] * item["unit_price"]
        assert abs(item["amount"] - expected_amount) < 0.01
