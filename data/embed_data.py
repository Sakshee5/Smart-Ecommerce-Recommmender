import pandas as pd
from sentence_transformers import SentenceTransformer

data = pd.read_csv('data/amazon_fashion_embeddings.csv')

# # Create data_to_embed by combining product name, description and product details
# # Handle NaN values by replacing them with empty strings
# data['description'] = data['description'].fillna('')
# data['features'] = data['features'].fillna('')
data['all_review_titles'] = data['all_review_titles'].fillna('')
data['all_review_texts'] = data['all_review_texts'].fillna('')

# # Combine the fields with proper string formatting
# data_to_embed = data.apply(lambda row: f"{row['product_name']}\n{row['description']}\n{row['features']}", axis=1)

# print("Sample of data to embed:")
# print(data_to_embed[0])

reviews_to_embed = data.apply(lambda row: f"{row['product_name']}\n{row['description']}\n{row['features']}\n\n Reviews: \n{row['all_review_titles']}\n{row['all_review_texts']}", axis=1)

print("Sample of reviews to embed:")
print(reviews_to_embed[1])

# Initialize the sentence transformer model
sentence_transformer = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

# Generate embeddings
# embeddings = sentence_transformer.encode(data_to_embed.tolist(), show_progress_bar=True).tolist()
embeddings = sentence_transformer.encode(reviews_to_embed.tolist(), show_progress_bar=True).tolist()

# Add embeddings to the dataframe
# data['embeddings'] = embeddings
data['review_embeddings'] = embeddings

# Save the results
data.to_csv('data/amazon_fashion_embeddings.csv', index=False)













