"""
SQLAlchemy database models for TaxSnap.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, LargeBinary, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class Receipt(Base):
    """Receipt model for storing processed receipt data."""
    
    __tablename__ = "receipts"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # User identification (Telegram user ID)
    user_id = Column(String(50), nullable=False, index=True)
    
    # File metadata
    filename = Column(String(255), nullable=False)
    upload_ts = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # OCR results
    raw_text = Column(Text, nullable=True)
    
    # Extracted fields
    vendor = Column(String(255), nullable=True, index=True)
    date = Column(String(50), nullable=True)  # Store as string for flexibility
    total = Column(Float, nullable=True)
    currency = Column(String(10), nullable=True)
    
    # Classification
    category = Column(String(100), nullable=True)
    tax_deduction_possible = Column(String(20), nullable=True)  # yes/no/maybe
    
    # LLM results
    llm_summary = Column(Text, nullable=True)
    llm_details = Column(JSON, nullable=True)
    
    # Embeddings
    embedding = Column(LargeBinary, nullable=True)  # Serialized numpy array
    
    # Processing status
    processed = Column(Boolean, default=False, nullable=False)
    processing_error = Column(Text, nullable=True)
    
    # Extra metadata
    extra_meta = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Receipt(id={self.id}, vendor={self.vendor}, total={self.total})>"


# Create indexes
Index("idx_receipts_user_id", Receipt.user_id)
Index("idx_receipts_upload_ts", Receipt.upload_ts)
Index("idx_receipts_vendor", Receipt.vendor)
Index("idx_receipts_processed", Receipt.processed)
Index("idx_receipts_user_processed", Receipt.user_id, Receipt.processed)
