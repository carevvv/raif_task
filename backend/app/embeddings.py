"""
Embeddings generation and semantic search using sentence-transformers.
"""
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from app.config import settings
from typing import List, Tuple
import structlog

logger = structlog.get_logger()


class EmbeddingService:
    """Service for generating embeddings and performing semantic search."""
    
    def __init__(self):
        logger.info("Loading embedding model", model=settings.EMBEDDING_MODEL)
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info("Embedding model loaded successfully")
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding vector for text.
        
        Args:
            text: Input text
            
        Returns:
            Numpy array of embedding vector
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return np.zeros(self.model.get_sentence_embedding_dimension())
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def serialize_embedding(self, embedding: np.ndarray) -> bytes:
        """
        Serialize numpy array to bytes for database storage.
        
        Args:
            embedding: Numpy array
            
        Returns:
            Bytes representation
        """
        return embedding.tobytes()
    
    def deserialize_embedding(self, embedding_bytes: bytes) -> np.ndarray:
        """
        Deserialize bytes back to numpy array.
        
        Args:
            embedding_bytes: Bytes from database
            
        Returns:
            Numpy array
        """
        # Reconstruct array with correct shape
        dimension = self.model.get_sentence_embedding_dimension()
        return np.frombuffer(embedding_bytes, dtype=np.float32).reshape(dimension)
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (0-1)
        """
        # Reshape for sklearn
        emb1 = embedding1.reshape(1, -1)
        emb2 = embedding2.reshape(1, -1)
        
        similarity = cosine_similarity(emb1, emb2)[0][0]
        return float(similarity)
    
    def search_similar(
        self, 
        query_embedding: np.ndarray, 
        embeddings_list: List[Tuple[int, bytes]], 
        top_k: int = 10
    ) -> List[Tuple[int, float]]:
        """
        Search for most similar embeddings using linear search.
        
        Args:
            query_embedding: Query embedding vector
            embeddings_list: List of (receipt_id, embedding_bytes) tuples
            top_k: Number of top results to return
            
        Returns:
            List of (receipt_id, similarity_score) tuples, sorted by score
        """
        if not embeddings_list:
            return []
        
        results = []
        
        for receipt_id, embedding_bytes in embeddings_list:
            try:
                embedding = self.deserialize_embedding(embedding_bytes)
                similarity = self.compute_similarity(query_embedding, embedding)
                results.append((receipt_id, similarity))
            except Exception as e:
                logger.error("Failed to compute similarity", receipt_id=receipt_id, error=str(e))
                continue
        
        # Sort by similarity descending
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k
        return results[:top_k]
    
    def generate_text_for_embedding(self, receipt_data: dict) -> str:
        """
        Generate combined text from receipt data for embedding.
        Combines vendor, items, category, and summary.
        
        Args:
            receipt_data: Receipt data dictionary
            
        Returns:
            Combined text string
        """
        parts = []
        
        if receipt_data.get("vendor"):
            parts.append(f"Продавец: {receipt_data['vendor']}")
        
        if receipt_data.get("category"):
            parts.append(f"Категория: {receipt_data['category']}")
        
        if receipt_data.get("llm_summary"):
            parts.append(f"Описание: {receipt_data['llm_summary']}")
        
        if receipt_data.get("raw_text"):
            # Take first 500 chars of raw text
            raw_excerpt = receipt_data["raw_text"][:500]
            parts.append(f"Текст чека: {raw_excerpt}")
        
        return " | ".join(parts)


# Global instance (lazy loading)
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service instance."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
