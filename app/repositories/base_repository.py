from app.extensions import kv
import json
from typing import Optional, List, Dict, Any

class BaseRepository:
    """Base repository with common CRUD operations"""
    
    def __init__(self, key_prefix: str):
        self.key_prefix = key_prefix
    
    def _get_key(self, identifier: str) -> str:
        """Generate Redis key"""
        return f"{self.key_prefix}:{identifier}"
    
    def _get_all_key(self) -> str:
        """Key for storing all items"""
        return f"{self.key_prefix}:all"
    
    def save(self, identifier: str, data: Dict[str, Any]) -> bool:
        """Save data to Redis"""
        try:
            key = self._get_key(identifier)
            kv.set(key, json.dumps(data))
            # Add to index set
            kv.sadd(self._get_all_key(), identifier)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def find_by_id(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Find data by identifier"""
        try:
            key = self._get_key(identifier)
            data = kv.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Error finding data: {e}")
            return None
    
    def find_all(self) -> List[Dict[str, Any]]:
        """Find all data"""
        try:
            identifiers = kv.smembers(self._get_all_key())
            results = []
            for identifier in identifiers:
                data = self.find_by_id(identifier)
                if data:
                    results.append(data)
            return results
        except Exception as e:
            print(f"Error finding all data: {e}")
            return []
    
    def delete(self, identifier: str) -> bool:
        """Delete data by identifier"""
        try:
            key = self._get_key(identifier)
            kv.delete(key)
            kv.srem(self._get_all_key(), identifier)
            return True
        except Exception as e:
            print(f"Error deleting data: {e}")
            return False
    
    def update(self, identifier: str, data: Dict[str, Any]) -> bool:
        """Update data"""
        return self.save(identifier, data)
    
    def exists(self, identifier: str) -> bool:
        """Check if data exists"""
        try:
            key = self._get_key(identifier)
            return kv.exists(key) > 0
        except Exception:
            return False