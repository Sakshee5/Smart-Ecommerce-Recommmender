import pandas as pd
import openai
import faiss
import pickle
import os
import numpy as np
from typing import List
import dotenv

dotenv.load_dotenv()
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def create_embeddings_batch(texts: List[str], batch_size=100, model: str = "text-embedding-3-small"):
    """Create embeddings for a list of texts in batches."""
    all_embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = [text[:28000] for text in texts[i:i + batch_size]]
        print(f"Processing batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
        
        try:
            response = client.embeddings.create(input=batch, model=model)
            # Extract embeddings from response
            batch_embeddings = [embedding.embedding for embedding in response.data]
            all_embeddings.extend(batch_embeddings)
        except Exception as e:
            print(f"Error processing batch {i//batch_size + 1}: {e}")
            # You might want to implement retry logic here
            raise e
    
    return np.array(all_embeddings, dtype=np.float32)

def create_faiss_index(embeddings, dimension):
    """Create a FAISS index for the given embeddings."""
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

def main():
    # Load data
    print("Loading data...")
    data = pd.read_csv('data/amazon_fashion_cleaned.csv', nrows=5000)
    print(f"Loaded {len(data)} products")

    # Create combined embeddings (product details + reviews)
    print("Creating combined embeddings...")
    combined_text = data.apply(
        lambda row: f"{row['product_name']}\n{row['description']}\n{row['features']}\n\nReviews:\n{row['all_review_titles']}\n{row['all_review_texts']}", 
        axis=1
    ).tolist()
    
    # Use smaller batch size for combined text (longer texts)
    combined_embeddings = create_embeddings_batch(combined_text)
    print(f"Created combined embeddings shape: {combined_embeddings.shape}")
    
    # Create product details embeddings
    print("Creating product details embeddings...")
    product_details = data.apply(
        lambda row: f"{row['product_name']}\n{row['description']}\n{row['features']}", 
        axis=1
    ).tolist()
    
    product_embeddings = create_embeddings_batch(product_details)
    print(f"Created product embeddings shape: {product_embeddings.shape}")
    
    # Create FAISS indices
    print("Creating FAISS indices...")
    embedding_dimension = product_embeddings.shape[1]  # Should be 1536 for text-embedding-3-small
    
    product_index = create_faiss_index(product_embeddings, embedding_dimension)
    combined_index = create_faiss_index(combined_embeddings, embedding_dimension)
    
    # Save indices and metadata
    print("Saving indices and metadata...")
    os.makedirs('data/faiss', exist_ok=True)
    
    # Save FAISS indices
    faiss.write_index(product_index, 'data/faiss/product_index.faiss')
    faiss.write_index(combined_index, 'data/faiss/combined_index.faiss')
    
    # Save metadata
    metadata = {
        'product_names': data['product_name'].tolist(),
        'product_images': data['images'].tolist(),
        'ratings': data['avg_review_rating'].tolist(),
        'review_titles': data['all_review_titles'].tolist(),
        'review_texts': data['all_review_texts'].tolist(),
        'descriptions': data['description'].tolist(),
        'features': data['features'].tolist()
    }
    
    with open('data/faiss/metadata.pkl', 'wb') as f:
        pickle.dump(metadata, f)
    
    # Save embeddings as well (optional, for debugging/reuse)
    np.save('data/faiss/product_embeddings.npy', product_embeddings)
    np.save('data/faiss/combined_embeddings.npy', combined_embeddings)
    
    print("Done! FAISS indices and metadata have been saved.")
    print(f"Product index size: {product_index.ntotal}")
    print(f"Combined index size: {combined_index.ntotal}")

if __name__ == "__main__":
    main()