import numpy as np
from typing import List, Tuple, Optional, Dict
import faiss
import pickle

class ProductDataManager:
    """Manages product data and embeddings for efficient processing."""
    
    def __init__(self, cache_size: int = 1000):
        """Initialize the data manager with caching."""
        self._product_index = faiss.read_index('data/faiss/product_index.faiss')
        self._combined_index = faiss.read_index('data/faiss/combined_index.faiss')
        
        with open('data/faiss/metadata.pkl', 'rb') as f:
            self._metadata = pickle.load(f)
        
        self._cache_size = cache_size
        self._search_cache = {}
    
    def _normalize_embedding(self, embedding: np.ndarray) -> np.ndarray:
        """Normalize embedding for consistent processing."""
        embedding = np.array(embedding, dtype=np.float32)
        if len(embedding.shape) == 1:
            embedding = embedding.reshape(1, -1)
        return embedding
    
    def _calculate_similarity_scores(self, distances: np.ndarray) -> np.ndarray:
        """Convert distances to similarity scores."""
        if len(distances) == 0:
            return np.array([])
        
        # Avoid division by zero
        max_distance = np.max(distances)
        if max_distance == 0:
            return np.ones_like(distances)
        
        return 1 - (distances / max_distance)
    
    def _create_recommendations(self, indices: List[int], scores: np.ndarray) -> List[Tuple]:
        """Create recommendation tuples from indices and scores."""
        recommendations = []
        for idx, score in zip(indices, scores):
            if idx < len(self._metadata['product_names']):
                recommendations.append((
                    self._metadata['product_names'][idx],
                    float(score),
                    self._metadata['review_titles'][idx],
                    self._metadata['review_texts'][idx],
                    self._metadata['product_images'][idx],
                    self._metadata['ratings'][idx]
                ))
        return recommendations
    
    def search_products(
        self, 
        query_embedding: np.ndarray, 
        k: int = 6, 
        recommendations: Optional[List[Tuple]] = None
    ) -> List[Tuple]:
        """Search products using FAISS index with optional reranking."""
        
        query_embedding = self._normalize_embedding(query_embedding)
        
        if recommendations:
            return self._rerank_existing_recommendations(query_embedding, recommendations, k)
        else:
            return self._search_new_products(query_embedding, k)
    
    def _search_new_products(self, query_embedding: np.ndarray, k: int) -> List[Tuple]:
        """Search for new products using the product index."""
        try:
            distances, indices = self._product_index.search(query_embedding, k)
            indices = indices[0]
            similarity_scores = self._calculate_similarity_scores(distances[0])
            
            return self._create_recommendations(indices, similarity_scores)
        
        except Exception as e:
            print(f"Error in product search: {e}")
            return []
    
    def _rerank_existing_recommendations(
        self, 
        query_embedding: np.ndarray, 
        recommendations: List[Tuple], 
        k: int
    ) -> List[Tuple]:
        """Rerank existing recommendations based on new query."""
        try:
            # Get indices of current recommendations
            current_indices = []
            for rec in recommendations:
                product_name = rec[0]
                try:
                    idx = self._metadata['product_names'].index(product_name)
                    current_indices.append(idx)
                except ValueError:
                    continue
            
            if not current_indices:
                return recommendations[:k]
            
            # Get embeddings for current recommendations
            current_embeddings = []
            for idx in current_indices:
                # Reconstruct embedding from combined index
                embedding = self._combined_index.reconstruct(idx)
                current_embeddings.append(embedding)
            
            if not current_embeddings:
                return recommendations[:k]
            
            # Calculate similarities with the new query
            current_embeddings = np.array(current_embeddings, dtype=np.float32)
            similarities = np.dot(current_embeddings, query_embedding.T).flatten()
            
            # Sort by similarity and return top k
            sorted_indices = np.argsort(similarities)[::-1][:k]
            reranked_recommendations = [recommendations[i] for i in sorted_indices if i < len(recommendations)]
            
            # Update similarity scores
            for i, rec_idx in enumerate(sorted_indices):
                if rec_idx < len(reranked_recommendations) and i < len(similarities):
                    rec_list = list(reranked_recommendations[i])
                    rec_list[1] = float(similarities[sorted_indices[i]])  # Update similarity score
                    reranked_recommendations[i] = tuple(rec_list)
            
            return reranked_recommendations
        
        except Exception as e:
            print(f"Error in reranking: {e}")
            return recommendations[:k]
    
    def get_recommendations(
        self,
        query_embedding: np.ndarray,
        k: int = 6,
    ) -> List[Tuple[str, float, List[str], List[str], str, float]]:
        """Get top k product recommendations based on similarity scores."""
        return self.search_products(query_embedding, k)
    
    def rerank_recommendations(
        self,
        followup_embedding: np.ndarray,
        current_recommendations: List[Tuple],
        k: int = 6
    ) -> List[Tuple]:
        """Re-rank existing recommendations based on follow-up response."""
        return self.search_products(followup_embedding, k, current_recommendations)
    
    def get_product_details(self, product_name: str) -> Optional[Dict]:
        """Get detailed information for a specific product."""
        try:
            idx = self._metadata['product_names'].index(product_name)
            return {
                'product_name': self._metadata['product_names'][idx],
                'review_titles': self._metadata['review_titles'][idx],
                'review_texts': self._metadata['review_texts'][idx],
                'product_image': self._metadata['product_images'][idx],
                'rating': self._metadata['ratings'][idx]
            }
        except (ValueError, IndexError):
            return None
    
    def get_similar_products(self, product_name: str, k: int = 5) -> List[Tuple]:
        """Get products similar to a given product."""
        try:
            idx = self._metadata['product_names'].index(product_name)
            # Get embedding for the product
            product_embedding = self._combined_index.reconstruct(idx).reshape(1, -1)
            
            # Search for similar products
            distances, indices = self._combined_index.search(product_embedding, k + 1)  # +1 to exclude self
            indices = indices[0][1:]  # Remove the product itself
            distances = distances[0][1:]
            
            similarity_scores = self._calculate_similarity_scores(distances)
            return self._create_recommendations(indices, similarity_scores)
        
        except (ValueError, IndexError) as e:
            print(f"Error finding similar products: {e}")
            return []
    
    def get_metadata_stats(self) -> Dict[str, int]:
        """Get statistics about the loaded metadata."""
        return {
            'total_products': len(self._metadata['product_names']),
            'index_dimension': self._product_index.d,
            'combined_index_dimension': self._combined_index.d
        }

# Utility functions
def create_product_manager() -> ProductDataManager:
    """Create and return a ProductDataManager instance."""
    return ProductDataManager()

def batch_search_products(
    queries: List[str], 
    embedding_function, 
    k: int = 6
) -> List[List[Tuple]]:
    """Batch search for multiple queries."""
    manager = create_product_manager()
    results = []
    
    for query in queries:
        embedding = embedding_function(query)
        recommendations = manager.get_recommendations(embedding, k)
        results.append(recommendations)
    
    return results

if __name__ == "__main__":
    from llm_handler import process_user_intent, get_openai_embedding
    
    # Test the optimized data handler
    user_query = "I am looking for light colored tops that may go well with the grey formal pants I already own"
    search_query = process_user_intent(user_query)
    print(f"Search query: {search_query}")
    
    search_query_embedding = get_openai_embedding(search_query)
    
    product_manager = ProductDataManager()
    
    # Test initial recommendations
    recos = product_manager.get_recommendations(search_query_embedding, k=10)
    print("Initial recommendations:")
    for i, reco in enumerate(recos):
        print(f"{i+1}. {reco[0]} (Score: {reco[1]:.3f})")
    
    # Test reranking with follow-up