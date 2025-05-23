"""Module for handling data operations and embeddings."""
import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Any
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import ast
from functools import lru_cache
import streamlit as st
import time

# Cache the sentence transformer model
@lru_cache(maxsize=1)
def get_sentence_transformer(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    """Get cached sentence transformer model."""
    return SentenceTransformer(model_name, device="cpu")

class ProductDataManager:
    """Manages product data and embeddings for efficient processing."""
    
    def __init__(self, file_path: str = 'data/amazon_fashion_embeddings.csv'):
        """Initialize the data manager."""
        # Show loading message
        with st.spinner('Loading product data...'):
            self.data = pd.read_csv(file_path, nrows=2000)

        with st.spinner('Preprocessing embeddings...'):
            self._preprocess_embeddings()
    
    def _preprocess_embeddings(self):
        """Preprocess embeddings for faster similarity calculations."""
        start_time = time.time()
        
        # Convert string embeddings to numpy arrays once
        print("Processing product embeddings...")
        self.embeddings = []
        self.product_names = []
        total_rows = len(self.data)

        for idx, row in self.data.iterrows():
            if idx % 100 == 0:  # Show progress every 100 rows
                print(f"Processing row {idx}/{total_rows}")
            self.embeddings.append(np.array(ast.literal_eval(row['embeddings'])))
            self.product_names.append(row['product_name'])

        self.embeddings = np.array(self.embeddings)

        # Pre-compute review embeddings for reranking
        print("Processing review embeddings...")
        self.review_embeddings = {}
        
        for idx, row in self.data.iterrows():
            if idx % 100 == 0:  # Show progress every 100 rows
                print(f"Processing row {idx}/{total_rows}")
            self.review_embeddings[row['product_name']] = np.array(
                ast.literal_eval(row['review_embeddings'])
            )
        
        end_time = time.time()
        print(f"Data preprocessing completed in {end_time - start_time:.2f} seconds")
    
    def get_embeddings(self, data: List[str]) -> np.ndarray:
        """Generate embeddings for input text data."""
        model = get_sentence_transformer()
        embeddings = model.encode(data)
        return np.array(embeddings) if isinstance(embeddings, list) else embeddings
    
    def calculate_similarity(self, query_embedding: np.ndarray) -> np.ndarray:
        """Calculate cosine similarity between query and product embeddings."""

        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
        return cosine_similarity(query_embedding, self.embeddings)[0]
    
    def get_recommendations(
        self,
        query_embedding: np.ndarray,
        k: int = 6
    ) -> List[Tuple[str, float, List[str], List[str], str, float]]:
        """Get top k product recommendations based on similarity scores."""

        similarity_scores = self.calculate_similarity(query_embedding)
        
        # Get indices of top k scores
        top_k_indices = np.argsort(similarity_scores)[-k:][::-1]
        
        recommendations = []
        for idx in top_k_indices:
            product_name = self.product_names[idx]
            row = self.data[self.data['product_name'] == product_name].iloc[0]
            recommendations.append((
                product_name,
                similarity_scores[idx],
                row['all_review_titles'],
                row['all_review_texts'],
                row['images'],
                row['avg_review_rating']
            ))
        
        return recommendations
    
    def rerank_recommendations(
        self,
        followup_embedding: np.ndarray,
        current_recommendations: List[Tuple],
        k: int = 6
    ) -> List[Tuple]:
        """Re-rank existing recommendations based on follow-up response."""
        if len(followup_embedding.shape) == 1:
            followup_embedding = followup_embedding.reshape(1, -1)
        
        # Get review embeddings for current recommendations
        review_embeddings = np.array([
            self.review_embeddings[rec[0]] for rec in current_recommendations
        ])
        
        # Calculate similarity scores
        similarity_scores = cosine_similarity(followup_embedding, review_embeddings)[0]
        
        # Create reranked recommendations
        reranked = [
            (rec[0], score, rec[2], rec[3], rec[4], rec[5])
            for rec, score in zip(current_recommendations, similarity_scores)
        ]
        
        return sorted(reranked, key=lambda x: x[1], reverse=True)[:k]

# Create a singleton instance
@st.cache_resource
def get_product_manager():
    """Get or create the singleton ProductDataManager instance."""
    return ProductDataManager()

product_manager = get_product_manager() 