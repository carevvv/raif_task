"""
FastAPI main application for Checko backend.
"""
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, BackgroundTasks, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, init_db
from app import crud
from app.telegram_auth import get_user_id_from_header, extract_user_id
from app.schemas import (
    ReceiptResponse, 
    ReceiptListResponse, 
    HealthResponse,
    SearchResponse,
    SearchResult
)
from app.processor import processor
from app.embeddings import get_embedding_service
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Receipt OCR and processing service with LLM integration"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(exist_ok=True)


@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup."""
    logger.info("Starting Checko backend", version="1.0.0")
    init_db()
    logger.info("Database initialized")


@app.get(f"{settings.API_V1_PREFIX}/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow()
    )


@app.post(f"{settings.API_V1_PREFIX}/upload")
async def upload_receipt(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Upload a receipt file (image or PDF) for processing.
    Processing happens in the background.
    Requires Telegram authentication via Authorization header.
    """
    # Extract user_id from Telegram initData
    user_id = get_user_id_from_header(authorization)
    if not user_id:
        # For testing without Telegram, use a default user_id
        user_id = "test_user"
        logger.warning("No valid Telegram auth, using test_user")
    # Validate file size
    file_size = 0
    chunk_size = 1024 * 1024  # 1MB
    temp_file = Path(UPLOAD_DIR) / f"temp_{file.filename}"
    
    try:
        with open(temp_file, "wb") as f:
            while chunk := await file.read(chunk_size):
                file_size += len(chunk)
                if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
                    temp_file.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Max size: {settings.MAX_FILE_SIZE_MB}MB"
                    )
                f.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to save uploaded file", error=str(e))
        temp_file.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Failed to save file")
    
    # Create receipt record
    receipt = crud.create_receipt(db, file.filename, user_id)
    
    # Move file to permanent location
    final_path = UPLOAD_DIR / f"{receipt.id}_{file.filename}"
    shutil.move(str(temp_file), str(final_path))
    
    # Schedule background processing
    background_tasks.add_task(process_receipt, receipt.id, str(final_path), db)
    
    logger.info("Receipt uploaded", receipt_id=receipt.id, filename=file.filename, user_id=user_id)
    
    return {
        "id": receipt.id,
        "filename": file.filename,
        "status": "processing",
        "message": "File uploaded successfully. Processing in background."
    }


def process_receipt(receipt_id: int, file_path: str, db: Session):
    """
    Background task to process receipt:
    1. OCR extraction
    2. LLM parsing
    3. Classification
    4. Generate embeddings
    """
    logger.info("Starting receipt processing", receipt_id=receipt_id)
    
    try:
        # Step 1: OCR
        raw_text = processor.extract_text_from_file(file_path)
        crud.update_receipt_ocr(db, receipt_id, raw_text)
        logger.info("OCR completed", receipt_id=receipt_id, text_length=len(raw_text))
        
        # Step 2: Parse with LLM
        extracted = processor.parse_receipt_fields(raw_text)
        extracted_dict = extracted.model_dump()
        crud.update_receipt_extracted(db, receipt_id, extracted_dict)
        logger.info("Fields extracted", receipt_id=receipt_id)
        
        # Step 3: Classify
        classification = processor.classify_receipt(extracted_dict, raw_text)
        classification_dict = classification.model_dump()
        crud.update_receipt_classification(db, receipt_id, classification_dict)
        logger.info("Classification completed", receipt_id=receipt_id)
        
        # Step 4: Generate embeddings (optional - for semantic search)
        try:
            embedding_service = get_embedding_service()
            receipt = crud.get_receipt(db, receipt_id)
            
            embedding_text = embedding_service.generate_text_for_embedding({
                "vendor": receipt.vendor,
                "category": receipt.category,
                "llm_summary": receipt.llm_summary,
                "raw_text": receipt.raw_text
            })
            
            embedding_vector = embedding_service.generate_embedding(embedding_text)
            embedding_bytes = embedding_service.serialize_embedding(embedding_vector)
            crud.update_receipt_embedding(db, receipt_id, embedding_bytes)
            logger.info("Embedding generated", receipt_id=receipt_id)
        except Exception as e:
            # Embedding is optional - don't fail the whole process
            logger.warning("Embedding generation failed, continuing anyway", 
                         receipt_id=receipt_id, error=str(e))
        
        # Mark as processed
        crud.mark_receipt_processed(db, receipt_id, success=True)
        logger.info("Receipt processing completed successfully", receipt_id=receipt_id)
        
    except Exception as e:
        logger.error("Receipt processing failed", receipt_id=receipt_id, error=str(e))
        crud.mark_receipt_processed(db, receipt_id, success=False, error=str(e))


@app.get(f"{settings.API_V1_PREFIX}/process/{{receipt_id}}", response_model=ReceiptResponse)
async def get_receipt_status(
    receipt_id: int, 
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """Get processing status and results for a receipt."""
    # Extract user_id from Telegram initData
    user_id = get_user_id_from_header(authorization)
    if not user_id:
        user_id = "test_user"
    
    # Get receipt, filtered by user_id for security
    receipt = crud.get_receipt(db, receipt_id, user_id=user_id)
    
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    return ReceiptResponse.model_validate(receipt)


@app.get(f"{settings.API_V1_PREFIX}/list", response_model=ReceiptListResponse)
async def list_receipts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    processed_only: bool = Query(False),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """Get paginated list of receipts for the authenticated user."""
    # Extract user_id from Telegram initData
    user_id = get_user_id_from_header(authorization)
    if not user_id:
        user_id = "test_user"
    
    skip = (page - 1) * page_size
    receipts, total = crud.get_receipts(
        db, 
        skip=skip, 
        limit=page_size, 
        processed_only=processed_only,
        user_id=user_id
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return ReceiptListResponse(
        items=[ReceiptResponse.model_validate(r) for r in receipts],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@app.get(f"{settings.API_V1_PREFIX}/search", response_model=SearchResponse)
async def search_receipts(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """Semantic search across user's receipts using embeddings."""
    # Extract user_id from Telegram initData
    user_id = get_user_id_from_header(authorization)
    if not user_id:
        user_id = "test_user"
    
    logger.info("Search request", query=q, user_id=user_id)
    
    # Generate query embedding
    embedding_service = get_embedding_service()
    query_embedding = embedding_service.generate_embedding(q)
    
    # Get all user's receipts with embeddings
    all_receipts = crud.get_all_receipts_with_embeddings(db, user_id=user_id)
    
    if not all_receipts:
        return SearchResponse(query=q, results=[])
    
    # Prepare embeddings list
    embeddings_list = [
        (r.id, r.embedding) for r in all_receipts if r.embedding
    ]
    
    # Search
    similar_ids = embedding_service.search_similar(query_embedding, embeddings_list, top_k=limit)
    
    # Build results
    results = []
    for receipt_id, score in similar_ids:
        receipt = crud.get_receipt(db, receipt_id)
        if receipt:
            results.append(SearchResult(
                receipt=ReceiptResponse.model_validate(receipt),
                similarity_score=score
            ))
    
    logger.info("Search completed", query=q, results_count=len(results))
    
    return SearchResponse(query=q, results=results)


@app.post(f"{settings.API_V1_PREFIX}/generate-template/{{receipt_id}}")
async def generate_template(
    receipt_id: int, 
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """Generate email template for accounting department."""
    # Extract user_id from Telegram initData
    user_id = get_user_id_from_header(authorization)
    if not user_id:
        user_id = "test_user"
    
    receipt = crud.get_receipt(db, receipt_id, user_id=user_id)
    
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    if not receipt.processed:
        raise HTTPException(status_code=400, detail="Receipt not yet processed")
    
    # Prepare data
    receipt_data = {
        "vendor": receipt.vendor,
        "date": receipt.date,
        "total": receipt.total,
        "currency": receipt.currency,
        "category": receipt.category
    }
    
    classification_data = receipt.llm_details or {}
    
    # Generate template
    template = processor.generate_template(receipt_data, classification_data)
    
    return template


@app.get(f"{settings.API_V1_PREFIX}/download/{{receipt_id}}")
async def download_receipt(
    receipt_id: int, 
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """Download original receipt file."""
    # Extract user_id from Telegram initData
    user_id = get_user_id_from_header(authorization)
    if not user_id:
        user_id = "test_user"
    
    receipt = crud.get_receipt(db, receipt_id, user_id=user_id)
    
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    # Find file
    file_path = UPLOAD_DIR / f"{receipt_id}_{receipt.filename}"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        filename=receipt.filename,
        media_type="application/octet-stream"
    )


@app.delete(f"{settings.API_V1_PREFIX}/receipt/{{receipt_id}}")
async def delete_receipt(
    receipt_id: int, 
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """Delete a specific receipt and its file."""
    # Extract user_id from Telegram initData
    user_id = get_user_id_from_header(authorization)
    if not user_id:
        user_id = "test_user"
    
    receipt = crud.get_receipt(db, receipt_id, user_id=user_id)
    
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    # Delete file
    file_path = UPLOAD_DIR / f"{receipt_id}_{receipt.filename}"
    file_path.unlink(missing_ok=True)
    
    # Delete from DB
    crud.delete_receipt(db, receipt_id)
    
    logger.info("Receipt deleted", receipt_id=receipt_id)
    
    return {"message": "Receipt deleted successfully"}


@app.delete(f"{settings.API_V1_PREFIX}/delete_all")
async def delete_all_data(
    confirm: str = Query(..., description="Type 'DELETE_ALL' to confirm"),
    db: Session = Depends(get_db)
):
    """Delete all receipts and files. Requires confirmation."""
    if confirm != "DELETE_ALL":
        raise HTTPException(status_code=400, detail="Confirmation required")
    
    # Delete all files
    for file_path in UPLOAD_DIR.glob("*"):
        if file_path.is_file():
            file_path.unlink()
    
    # Delete all receipts from DB
    count = crud.delete_all_receipts(db)
    
    logger.warning("All data deleted", count=count)
    
    return {"message": f"Deleted {count} receipts and all files"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
