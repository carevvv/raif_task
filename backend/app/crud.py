"""
CRUD operations for database models.
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from app.models import Receipt
from typing import List, Optional
import structlog

logger = structlog.get_logger()


def create_receipt(db: Session, filename: str) -> Receipt:
    """Create a new receipt record."""
    receipt = Receipt(filename=filename, processed=False)
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    logger.info("Receipt created", receipt_id=receipt.id, filename=filename)
    return receipt


def get_receipt(db: Session, receipt_id: int) -> Optional[Receipt]:
    """Get receipt by ID."""
    return db.query(Receipt).filter(Receipt.id == receipt_id).first()


def get_receipts(
    db: Session, 
    skip: int = 0, 
    limit: int = 20,
    processed_only: bool = False
) -> tuple[List[Receipt], int]:
    """
    Get paginated list of receipts.
    Returns (receipts, total_count).
    """
    query = db.query(Receipt)
    
    if processed_only:
        query = query.filter(Receipt.processed == True)
    
    total = query.count()
    receipts = query.order_by(desc(Receipt.upload_ts)).offset(skip).limit(limit).all()
    
    return receipts, total


def update_receipt_ocr(db: Session, receipt_id: int, raw_text: str) -> Optional[Receipt]:
    """Update receipt with OCR results."""
    receipt = get_receipt(db, receipt_id)
    if receipt:
        receipt.raw_text = raw_text
        db.commit()
        db.refresh(receipt)
        logger.info("Receipt OCR updated", receipt_id=receipt_id)
    return receipt


def update_receipt_extracted(
    db: Session, 
    receipt_id: int, 
    extracted_data: dict
) -> Optional[Receipt]:
    """Update receipt with extracted structured data."""
    receipt = get_receipt(db, receipt_id)
    if receipt:
        receipt.vendor = extracted_data.get("vendor")
        receipt.date = extracted_data.get("date")
        receipt.total = extracted_data.get("total")
        receipt.currency = extracted_data.get("currency")
        receipt.extra_meta = extracted_data
        db.commit()
        db.refresh(receipt)
        logger.info("Receipt extracted data updated", receipt_id=receipt_id)
    return receipt


def update_receipt_classification(
    db: Session,
    receipt_id: int,
    classification: dict
) -> Optional[Receipt]:
    """Update receipt with classification results."""
    receipt = get_receipt(db, receipt_id)
    if receipt:
        receipt.category = classification.get("category")
        receipt.tax_deduction_possible = classification.get("tax_deduction_possible")
        receipt.llm_summary = classification.get("reasoning_short")
        receipt.llm_details = classification
        db.commit()
        db.refresh(receipt)
        logger.info("Receipt classification updated", receipt_id=receipt_id)
    return receipt


def update_receipt_embedding(db: Session, receipt_id: int, embedding_bytes: bytes) -> Optional[Receipt]:
    """Update receipt with embedding vector."""
    receipt = get_receipt(db, receipt_id)
    if receipt:
        receipt.embedding = embedding_bytes
        db.commit()
        db.refresh(receipt)
        logger.info("Receipt embedding updated", receipt_id=receipt_id)
    return receipt


def mark_receipt_processed(
    db: Session, 
    receipt_id: int, 
    success: bool = True, 
    error: Optional[str] = None
) -> Optional[Receipt]:
    """Mark receipt as processed."""
    receipt = get_receipt(db, receipt_id)
    if receipt:
        receipt.processed = success
        receipt.processing_error = error
        db.commit()
        db.refresh(receipt)
        logger.info("Receipt marked as processed", receipt_id=receipt_id, success=success)
    return receipt


def delete_receipt(db: Session, receipt_id: int) -> bool:
    """Delete receipt by ID."""
    receipt = get_receipt(db, receipt_id)
    if receipt:
        db.delete(receipt)
        db.commit()
        logger.info("Receipt deleted", receipt_id=receipt_id)
        return True
    return False


def delete_all_receipts(db: Session) -> int:
    """Delete all receipts. Returns count of deleted receipts."""
    count = db.query(Receipt).delete()
    db.commit()
    logger.info("All receipts deleted", count=count)
    return count


def get_all_receipts_with_embeddings(db: Session) -> List[Receipt]:
    """Get all receipts that have embeddings for search."""
    return db.query(Receipt).filter(
        Receipt.embedding.isnot(None),
        Receipt.processed == True
    ).all()


def search_receipts_by_text(db: Session, query: str, limit: int = 10) -> List[Receipt]:
    """Simple text-based search in vendor, raw_text, and category."""
    search_pattern = f"%{query}%"
    return db.query(Receipt).filter(
        or_(
            Receipt.vendor.ilike(search_pattern),
            Receipt.raw_text.ilike(search_pattern),
            Receipt.category.ilike(search_pattern)
        )
    ).limit(limit).all()
