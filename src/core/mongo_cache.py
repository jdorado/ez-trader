from pymongo import MongoClient
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os


class MongoCache:
    """
    MongoDB-based cache for ticker data.
    """
    
    def __init__(self, db_name: str = "ez_stocks", collection_name: str = "ticker_cache"):
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        
        # Create index on ticker and timestamp
        self.collection.create_index("ticker")
        self.collection.create_index("timestamp")
        
    def get(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get cached ticker data if not expired (24h)."""
        try:
            doc = self.collection.find_one({"ticker": ticker})
            if doc:
                # Check if expired
                cached_time = doc.get('timestamp')
                if cached_time:
                    age = datetime.now() - cached_time
                    if age < timedelta(hours=24):
                        return doc.get('data')
            return None
        except Exception as e:
            print(f"Cache get error for {ticker}: {e}")
            return None
    
    def set(self, ticker: str, data: Dict[str, Any]):
        """Cache ticker data with timestamp."""
        try:
            self.collection.update_one(
                {"ticker": ticker},
                {"$set": {
                    "ticker": ticker,
                    "data": data,
                    "timestamp": datetime.now()
                }},
                upsert=True
            )
        except Exception as e:
            print(f"Cache set error for {ticker}: {e}")
    
    def clear_all(self):
        """Clear all cached data."""
        self.collection.delete_many({})
        print("✅ Cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self.collection.count_documents({})
        recent = self.collection.count_documents({
            "timestamp": {"$gte": datetime.now() - timedelta(hours=24)}
        })
        return {
            "total_entries": total,
            "recent_entries_24h": recent,
            "hit_rate": f"{(recent/total*100):.1f}%" if total > 0 else "0%"
        }
