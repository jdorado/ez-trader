from src.core.cache_manager import CacheManager
import time
import os
from dotenv import load_dotenv

load_dotenv()
print(f"DEBUG: REDIS_HOST={os.getenv('REDIS_HOST')}")
print(f"DEBUG: REDIS_PORT={os.getenv('REDIS_PORT')}")

print("Testing Redis Connection...")
try:
    cache = CacheManager()
    cache.set("test_key", "Hello Redis", ttl_seconds=60)
    val = cache.get("test_key")
    print(f"Retrieved: {val}")
    
    if val == "Hello Redis":
        print("✅ Redis Connection SUCCESS")
    else:
        print("❌ Redis Connection FAILED (Value Mismatch)")
except Exception as e:
    print(f"❌ Redis Connection FAILED: {e}")
