import numpy as np
from typing import List, Tuple
import faiss
import pickle

class ProductDataManager:
    """Manages product data and embeddings for efficient processing."""
    
    def __init__(self):
        """Initialize the data manager."""
        self._product_index = faiss.read_index('data/faiss/product_index.faiss')
        self._combined_index = faiss.read_index('data/faiss/combined_index.faiss')
        with open('data/faiss/metadata.pkl', 'rb') as f:
            self._metadata = pickle.load(f)
    
    def search_products(self, query_embedding: np.ndarray, k: int = 6, recommendations=None) -> List[Tuple]:
        """Search products using FAISS index."""

        query_embedding = np.array(query_embedding)
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        if recommendations:
            # Get indices of current recommendations in the metadata
            current_indices = []
            for rec in recommendations:
                product_name = rec[0]
                try:
                    idx = self._metadata['product_names'].index(product_name)
                    current_indices.append(idx)
                except ValueError:
                    continue
            
            if not current_indices:
                return recommendations
            
            # Create a subset of the combined index with only current recommendations
            subset_index = faiss.IndexFlatL2(self._combined_index.d)
            subset_index.add(self._combined_index.reconstruct_n(0, len(self._metadata['product_names']))[current_indices])
            
            # Search in the subset
            distances, local_indices = subset_index.search(query_embedding.astype('float32'), k)
            
            # Map local indices back to original indices
            indices = [current_indices[i] for i in local_indices[0]]
        else:
            # Use product index for initial search
            distances, indices = self._product_index.search(query_embedding.astype('float32'), k)
            indices = indices[0]
        
        # Convert distances to similarity scores
        max_distance = np.max(distances)
        similarity_scores = 1 - (distances / max_distance)
        
        # Create recommendations
        recommendations = []
        for idx, score in zip(indices, similarity_scores[0]):
            recommendations.append((
                self._metadata['product_names'][idx],
                float(score),
                self._metadata['review_titles'][idx],
                self._metadata['review_texts'][idx],
                self._metadata['product_images'][idx],
                self._metadata['ratings'][idx]
            ))
        
        return recommendations
    
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
    

if __name__ == "__main__":
    from llm_handler import process_user_intent, get_embeddings
    user_query = "I am looking for light colored tops that may go well with the grey formal pants I already own"
    search_query = process_user_intent(user_query)
    print(search_query)
    search_query_embedding = get_embeddings(search_query)

    product_manager = ProductDataManager()
    recos = product_manager.search_products(search_query_embedding)
    print("*"*100)
    for reco in recos:
        print(reco)

    followup_query = "I need something in white color"
    followup_query_embedding = get_embeddings(followup_query)

    reranked_recos = product_manager.rerank_recommendations(followup_query_embedding, recos)
    print('*'*100)
    for reco in reranked_recos:
        print(reco)