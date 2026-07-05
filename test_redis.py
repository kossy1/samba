# test_redis.py
import redis
import os
from dotenv import load_dotenv

load_dotenv()

def test_redis():
    try:
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        r = redis.from_url(redis_url, decode_responses=True)
        
        # Test connection
        r.set('test_key', 'test_value')
        value = r.get('test_key')
        
        print(f"✅ Redis connection successful!")
        print(f"   Test value: {value}")
        
        # Clean up
        r.delete('test_key')
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

if __name__ == "__main__":
    test_redis()