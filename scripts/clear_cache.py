import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.cache_manager import CacheManager

def clear_cache():
    try:
        cm = CacheManager()
        cm.client.flushdb()
        print("Cache cleared successfully.")
    except Exception as e:
        print(f"Error clearing cache: {e}")

if __name__ == "__main__":
    clear_cache()
