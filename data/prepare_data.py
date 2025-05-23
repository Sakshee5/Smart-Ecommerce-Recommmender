import pandas as pd
from datasets import load_dataset
import json
from tqdm import tqdm

def combine_amazon_data_to_csv(category="Amazon_Fashion", output_file="data/amazon_combined_data.csv"):
    """
    Combines Amazon reviews and metadata into a single CSV file.
    
    Args:
        category: Amazon category to process (e.g., "Clothing_Shoes_and_Jewelry", "Electronics")
        output_file: Name of the output CSV file
    """
    
    print(f"Loading {category} reviews dataset...")
    # Load reviews dataset
    reviews_dataset = load_dataset(
        "McAuley-Lab/Amazon-Reviews-2023", 
        f"raw_review_{category}", 
        trust_remote_code=True
    )
    reviews_data = reviews_dataset["full"]
    
    print(f"Loading {category} metadata dataset...")
    # Load metadata dataset
    meta_dataset = load_dataset(
        "McAuley-Lab/Amazon-Reviews-2023", 
        f"raw_meta_{category}", 
        split="full",
        trust_remote_code=True
    )
    
    print("Converting datasets to pandas DataFrames...")
    # Convert to pandas DataFrames
    reviews_df = pd.DataFrame(reviews_data)
    meta_df = pd.DataFrame(meta_dataset)
    
    print("Aggregating reviews by product...")
    # Group reviews by parent_asin and aggregate
    review_aggregation = reviews_df.groupby('parent_asin').agg({
        'title': lambda x: ' | '.join(x.dropna().astype(str)),  # Join all review titles
        'text': lambda x: ' | '.join(x.dropna().astype(str)),   # Join all review texts
        'rating': ['count', 'mean'],  # Count of reviews and average rating from reviews
        'helpful_vote': 'sum',        # Total helpful votes
        'verified_purchase': lambda x: (x == True).sum()  # Count of verified purchases
    }).reset_index()
    
    # Flatten column names
    review_aggregation.columns = [
        'parent_asin', 'all_review_titles', 'all_review_texts', 
        'review_count', 'avg_review_rating', 'total_helpful_votes', 'verified_purchases'
    ]
    
    print("Processing metadata...")
    # Process metadata - handle complex fields
    def process_images(images_dict):
        if isinstance(images_dict, dict) and 'large' in images_dict:
            return ' | '.join([img for img in images_dict['large'] if img is not None])
        return ''
    
    def process_features(features_list):
        if isinstance(features_list, list):
            return ' | '.join([str(f) for f in features_list if f is not None])
        return ''
    
    def process_description(desc_list):
        if isinstance(desc_list, list):
            return ' | '.join([str(d) for d in desc_list if d is not None])
        return ''
    
    def process_details(details_str):
        if isinstance(details_str, str):
            try:
                details_dict = json.loads(details_str)
                return ' | '.join([f"{k}: {v}" for k, v in details_dict.items()])
            except:
                return details_str
        return ''
    
    # Apply processing functions
    meta_df['processed_images'] = meta_df['images'].apply(process_images)
    meta_df['processed_features'] = meta_df['features'].apply(process_features)
    meta_df['processed_description'] = meta_df['description'].apply(process_description)
    meta_df['processed_details'] = meta_df['details'].apply(process_details)
    
    # Select and rename columns from metadata
    meta_selected = meta_df[[
        'parent_asin', 'main_category', 'title', 'average_rating', 
        'processed_features', 'processed_description', 'price', 
        'processed_images', 'processed_details'
    ]].rename(columns={
        'main_category': 'product_category',
        'title': 'product_name',
        'average_rating': 'avg_rating_metadata',
        'processed_features': 'features',
        'processed_description': 'description',
        'processed_images': 'images',
        'processed_details': 'product_details'
    })
    
    print("Merging reviews and metadata...")
    # Merge reviews and metadata
    combined_df = pd.merge(
        meta_selected, 
        review_aggregation, 
        on='parent_asin', 
        how='left'  # Keep all products, even those without reviews
    )
    
    # Fill NaN values for products without reviews
    combined_df['all_review_titles'] = combined_df['all_review_titles'].fillna('')
    combined_df['all_review_texts'] = combined_df['all_review_texts'].fillna('')
    combined_df['review_count'] = combined_df['review_count'].fillna(0)
    combined_df['avg_review_rating'] = combined_df['avg_review_rating'].fillna(0)
    combined_df['total_helpful_votes'] = combined_df['total_helpful_votes'].fillna(0)
    combined_df['verified_purchases'] = combined_df['verified_purchases'].fillna(0)
    
    print(f"Saving to {output_file}...")
    # Save to CSV
    combined_df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"Dataset saved successfully!")
    print(f"Total products: {len(combined_df)}")
    print(f"Products with reviews: {len(combined_df[combined_df['review_count'] > 0])}")
    print(f"Columns: {list(combined_df.columns)}")
    
    return combined_df

# Alternative function for processing multiple categories at once
def combine_multiple_categories(categories, output_file="data/amazon_combined_data.csv"):
    """
    Combines multiple Amazon categories into a single CSV file.
    
    Args:
        categories: List of category names
        output_file: Name of the output CSV file
    """
    all_data = []
    
    for category in categories:
        print(f"\nProcessing {category}...")
        try:
            df = combine_amazon_data_to_csv(category, f"temp_{category}.csv")
            all_data.append(df)
        except Exception as e:
            print(f"Error processing {category}: {e}")
            continue
    
    if all_data:
        print("\nCombining all categories...")
        combined_all = pd.concat(all_data, ignore_index=True)
        combined_all.to_csv(output_file, index=False, encoding='utf-8')
        print(f"All categories saved to {output_file}")
        print(f"Total products across all categories: {len(combined_all)}")
        return combined_all
    else:
        print("No data to combine.")
        return pd.DataFrame()


# Example usage for different categories
if __name__ == "__main__":
    # Process Clothing_Shoes_and_Jewelry category
    # df_beauty = combine_amazon_data_to_csv("Clothing_Shoes_and_Jewelry", "amazon_fashion_combined.csv")
    
    # You can also process other categories:
    # df_electronics = combine_amazon_data_to_csv("Electronics", "amazon_electronics_combined.csv")
    # df_books = combine_amazon_data_to_csv("Books", "amazon_books_combined.csv")
    
    # Display sample of the data
    # print("\nSample of combined data:")
    # print(df_beauty.head())
    # print(f"\nDataset shape: {df_beauty.shape}")

    # Example: Process multiple categories
    categories_to_process = ["Amazon_Fashion"]
    combined_all = combine_multiple_categories(categories_to_process)