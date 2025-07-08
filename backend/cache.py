"""
Redis caching implementation for enterprise scaling
"""
import json
import os
from typing import Optional, Any
from datetime import timedelta
import redis
from redis.exceptions import ConnectionError, TimeoutError
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Manages Redis caching with fallback to in-memory cache"""
    
    def __init__(self):
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.redis_client = None
        self.memory_cache = {}  # Fallback cache
        self.cache_ttl = int(os.getenv('CACHE_TTL', '300'))  # 5 minutes default
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection with retry logic"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                retry_on_error=[ConnectionError, TimeoutError],
                retry=redis.Retry(retries=3, backoff=redis.backoff.ExponentialBackoff())
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed, using in-memory cache: {e}")
            self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with fallback"""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                # Use in-memory cache
                if key in self.memory_cache:
                    return self.memory_cache[key]
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL"""
        if ttl is None:
            ttl = self.cache_ttl
        
        try:
            serialized = json.dumps(value)
            if self.redis_client:
                self.redis_client.setex(key, ttl, serialized)
            else:
                # Use in-memory cache
                self.memory_cache[key] = value
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                self.memory_cache.pop(key, None)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        count = 0
        try:
            if self.redis_client:
                for key in self.redis_client.scan_iter(match=pattern):
                    self.redis_client.delete(key)
                    count += 1
            else:
                # For in-memory cache
                keys_to_delete = [k for k in self.memory_cache if pattern.replace('*', '') in k]
                for key in keys_to_delete:
                    del self.memory_cache[key]
                    count += 1
        except Exception as e:
            logger.error(f"Cache clear pattern error for pattern {pattern}: {e}")
        return count
    
    def health_check(self) -> dict:
        """Check cache health status"""
        if self.redis_client:
            try:
                self.redis_client.ping()
                return {"status": "healthy", "type": "redis"}
            except:
                return {"status": "degraded", "type": "memory", "reason": "Redis unavailable"}
        return {"status": "healthy", "type": "memory"}

# Global cache instance
cache_manager = CacheManager()
