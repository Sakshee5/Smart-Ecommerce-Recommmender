import pandas as pd
import os
import json
from datetime import datetime
from typing import Optional, Dict
import hashlib

class CacheManager:
    """Simplified cache manager with better error handling."""
    
    def __init__(self, cache_file: str = "data/product_summaries.json"):
        self.cache_file = cache_file
        self.cache_dir = os.path.dirname(cache_file)
        self._ensure_cache_dir()
        self._cache_data = self._load_cache()
    
    def _ensure_cache_dir(self):
        """Ensure cache directory exists."""
        if self.cache_dir and not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _load_cache(self) -> Dict:
        """Load existing cache or create new one."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading cache, creating new one: {e}")
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache to JSON file."""
        try:
            # Create backup of existing cache
            if os.path.exists(self.cache_file):
                backup_file = f"{self.cache_file}.backup"
                if os.path.exists(backup_file):
                    os.remove(backup_file)
                os.rename(self.cache_file, backup_file)
            
            # Save new cache
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._cache_data, f, indent=2, ensure_ascii=False)
                
            # Remove backup if save successful
            backup_file = f"{self.cache_file}.backup"
            if os.path.exists(backup_file):
                os.remove(backup_file)
                
        except Exception as e:
            print(f"Error saving cache: {e}")
            # Restore backup if it exists
            backup_file = f"{self.cache_file}.backup"
            if os.path.exists(backup_file) and not os.path.exists(self.cache_file):
                os.rename(backup_file, self.cache_file)
    
    def _generate_product_key(self, product_name: str) -> str:
        """Generate consistent key for product name."""
        # Clean the product name and create hash for consistency
        clean_name = product_name.lower().strip()
        return hashlib.md5(clean_name.encode('utf-8')).hexdigest()
    
    def get_summary(self, product_name: str) -> Optional[str]:
        """Get cached summary for a product."""
        try:
            product_key = self._generate_product_key(product_name)
            
            if product_key in self._cache_data:
                # Update last accessed time
                self._cache_data[product_key]['last_accessed'] = datetime.now().isoformat()
                return self._cache_data[product_key]['summary']
            
            return None
        except Exception as e:
            print(f"Error retrieving summary for {product_name}: {e}")
            return None
    
    def save_summary(self, product_name: str, summary: str):
        """Save product summary to cache."""
        try:
            product_key = self._generate_product_key(product_name)
            current_time = datetime.now().isoformat()
            
            self._cache_data[product_key] = {
                'product_name': product_name,
                'summary': summary,
                'created_at': current_time,
                'last_accessed': current_time
            }
            
            # Save to file
            self._save_cache()
            
        except Exception as e:
            print(f"Error saving summary for {product_name}: {e}")
    
    def get_cache_stats(self) -> Dict[str, any]:
        """Get cache statistics."""
        try:
            file_size = 0
            if os.path.exists(self.cache_file):
                file_size = os.path.getsize(self.cache_file) / (1024 * 1024)  # MB
            
            return {
                'total_cached_products': len(self._cache_data),
                'cache_file_size_mb': round(file_size, 2),
                'cache_file_exists': os.path.exists(self.cache_file)
            }
        except Exception as e:
            print(f"Error getting cache stats: {e}")
            return {
                'total_cached_products': 0,
                'cache_file_size_mb': 0,
                'cache_file_exists': False
            }
    
    def clear_cache(self):
        """Clear all cached data."""
        try:
            self._cache_data = {}
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
        except Exception as e:
            print(f"Error clearing cache: {e}")
    
    def cleanup_old_entries(self, days_old: int = 30):
        """Remove cache entries older than specified days."""
        try:
            if not self._cache_data:
                return
            
            cutoff_date = datetime.now()
            cutoff_timestamp = (cutoff_date - pd.Timedelta(days=days_old)).isoformat()
            
            # Find old entries
            keys_to_remove = []
            for key, entry in self._cache_data.items():
                try:
                    if entry.get('last_accessed', '1970-01-01') < cutoff_timestamp:
                        keys_to_remove.append(key)
                except Exception:
                    # If we can't parse the date, consider it old
                    keys_to_remove.append(key)
            
            # Remove old entries
            for key in keys_to_remove:
                del self._cache_data[key]
            
            if keys_to_remove:
                self._save_cache()
                print(f"Cleaned up {len(keys_to_remove)} old cache entries")
                
        except Exception as e:
            print(f"Error during cache cleanup: {e}")

# Utility functions for cache management
def get_cache_manager() -> CacheManager:
    """Get a singleton cache manager instance."""
    if not hasattr(get_cache_manager, '_instance'):
        get_cache_manager._instance = CacheManager()
    return get_cache_manager._instance

def clear_product_cache():
    """Clear the product summary cache."""
    try:
        cache_manager = get_cache_manager()
        cache_manager.clear_cache()
        print("Cache cleared successfully")
    except Exception as e:
        print(f"Error clearing cache: {e}")
    
def get_cache_info() -> Dict[str, any]:
    """Get cache information."""
    try:
        cache_manager = get_cache_manager()
        return cache_manager.get_cache_stats()
    except Exception as e:
        print(f"Error getting cache info: {e}")
        return {'error': str(e)}

if __name__ == "__main__":
    # Test cache manager
    print("Testing Cache Manager...")
    
    try:
        cache = CacheManager()
        
        # Test saving and retrieving
        test_product = "Test Product ABC 123"
        test_summary = "This is a test summary for the product with special characters: é, ñ, 中文"
        
        print(f"Saving summary for: {test_product}")
        cache.save_summary(test_product, test_summary)
        
        print("Retrieving summary...")
        retrieved = cache.get_summary(test_product)
        
        print(f"Original: {test_summary}")
        print(f"Retrieved: {retrieved}")
        print(f"Match: {test_summary == retrieved}")
        
        # Test stats
        stats = cache.get_cache_stats()
        print(f"Cache stats: {stats}")
        
        print("Cache test completed successfully!")
        
    except Exception as e:
        print(f"Cache test failed: {e}")