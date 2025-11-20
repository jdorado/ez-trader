import redis
import json
import pickle
import os
from typing import Any, Optional
from datetime import timedelta

class CacheManager:
    """
    Manages caching of data using Redis.
    Supports JSON for simple data and Pickle for complex objects (like DataFrames).
    """
    
    def __init__(self, host: str = 'redis', port: int = 6379, db: int = 0):
        # Allow overriding via env vars
        host = os.getenv('REDIS_HOST', host)
        port = int(os.getenv('REDIS_PORT', port))
        self.client = redis.Redis(host=host, port=port, db=db)
        
    def get(self, key: str) -> Optional[Any]:
        """Retrieve item from cache."""
        try:
            data = self.client.get(key)
            if data:
                try:
                    return json.loads(data)
                except:
                    return pickle.loads(data)
            return None
        except Exception as e:
            # Fail silently (log in real app) so we fall back to fresh fetch
            print(f"Cache Get Error: {e}")
            return None

    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Store item in cache with TTL (default 5 mins)."""
        try:
            if isinstance(value, (dict, list, str, int, float, bool)):
                data = json.dumps(value)
            else:
                data = pickle.dumps(value)
            
            self.client.setex(key, timedelta(seconds=ttl_seconds), data)
        except Exception as e:
            print(f"Cache Set Error: {e}")

    def exists(self, key: str) -> bool:
        return self.client.exists(key) > 0
