import pytest
from app.services.ocr_service import OCRService


def test_ocr_service_initialization():
    """Test OCR service can be initialized"""
    service = OCRService()
    assert service is not None


def test_mock_extraction():
    """Test mock extraction returns valid data with >90% confidence"""
    service = OCRService()
    
    # Mock file bytes (empty for mock extraction)
    file_bytes = b"mock invoice data"
    
    # Extract data
    extracted_data, confidence = service.extract_invoice_data(file_bytes)
    
    # Verify confidence is >90%
    assert confidence > 0.90, f"Expected confidence >90%, got {confidence*100}%"
    
    # Verify required fields exist
    assert "invoice_number" in extracted_data
    assert "total_amount" in extracted_data
    assert "line_items" in extracted_data
    assert len(extracted_data["line_items"]) > 0
    
    # Verify line items have required fields
    line_item = extracted_data["line_items"][0]
    assert "description" in line_item
    assert "quantity" in line_item
    assert "unit_price" in line_item
    assert "amount" in line_item


def test_parse_amount():
    """Test amount parsing utility"""
    service = OCRService()
    
    assert service._parse_amount("$1,234.56") == 1234.56
    assert service._parse_amount("100.00") == 100.00
    assert service._parse_amount("$500") == 500.0
    assert service._parse_amount("invalid") is None


def test_parse_number():
    """Test number parsing utility"""
    service = OCRService()
    
    assert service._parse_number("123") == 123.0
    assert service._parse_number("12.5") == 12.5
    assert service._parse_number("1,000") == 1000.0
    assert service._parse_number("invalid") == 0.0
