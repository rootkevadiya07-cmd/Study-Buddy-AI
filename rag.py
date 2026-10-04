import numpy as np
import faiss
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
from config import Config

class RAGPipeline:
    """Retrieval-Augmented Generation Pipeline using SentenceTransformers and FAISS."""
    
    def __init__(self, model_name: str = Config.EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self.embedder = None
        self.index = None
        self.chunks: List[str] = []
        self.dimension = None

    def _load_embedder(self):
        """Lazy load the SentenceTransformer model to optimize app startup."""
        if self.embedder is None:
            self.embedder = SentenceTransformer(self.model_name)

    @staticmethod
    def chunk_text(text: str, chunk_size: int = Config.CHUNK_SIZE, overlap: int = Config.CHUNK_OVERLAP) -> List[str]:
        """
        Divide text into overlapping word-based chunks for context retrieval.
        """
        words = text.split()
        if not words:
            return []
            
        chunks = []
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            if end == len(words):
                break
            start += (chunk_size - overlap)
            
        return chunks

    def build_index(self, text: str) -> Dict[str, Any]:
        """
        Chunks input text, generates embeddings, and creates FAISS vector index.
        """
        self._load_embedder()
        self.chunks = self.chunk_text(text)
        
        if not self.chunks:
            return {
                "success": False,
                "num_chunks": 0,
                "error": "No text content found to create vector index."
            }

        # Generate embeddings
        embeddings = self.embedder.encode(self.chunks, show_progress_bar=False, convert_to_numpy=True)
        
        # Normalize vectors for Cosine Similarity using IndexFlatIP
        faiss.normalize_L2(embeddings)
        
        self.dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(embeddings.astype(np.float32))

        return {
            "success": True,
            "num_chunks": len(self.chunks),
            "dimension": self.dimension,
            "error": None
        }

    def search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Perform semantic search against FAISS vector index.
        Returns list of relevant chunks with relevance scores.
        """
        if not self.index or not self.chunks:
            return []
            
        self._load_embedder()
        query_vector = self.embedder.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_vector)

        scores, indices = self.index.search(query_vector.astype(np.float32), min(top_k, len(self.chunks)))
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunks) and idx >= 0:
                results.append({
                    "chunk": self.chunks[idx],
                    "score": float(score),
                    "chunk_id": int(idx)
                })
                
        return results

    def get_formatted_context(self, query: str, top_k: int = 4) -> str:
        """
        Search vector store and return a combined context block for LLM prompt.
        """
        search_results = self.search(query, top_k=top_k)
        if not search_results:
            return ""
            
        context_blocks = []
        for i, res in enumerate(search_results, 1):
            context_blocks.append(f"[Excerpt {i}]:\n{res['chunk']}")
            
        return "\n\n".join(context_blocks)
