"""
Query result caching module
"""

import hashlib
import json
import time
from typing import Any, Dict, Optional
from pathlib import Path


class QueryCache:
    """Cache for query results to avoid redundant executions."""
    
    def __init__(self, cache_dir: str = '.cache', ttl_seconds: int = 3600):
        """
        Initialize query cache.
        
        Args:
            cache_dir: Directory to store cache files
            ttl_seconds: Time-to-live for cache entries in seconds (default: 1 hour)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl_seconds = ttl_seconds
        self.memory_cache = {}
    
    def _get_cache_key(self, sql_query: str, database: str = '') -> str:
        """Generate a cache key from SQL query and database."""
        content = f"{database}:{sql_query}".lower().strip()
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, sql_query: str, database: str = '') -> Optional[Dict[str, Any]]:
        """
        Get cached results for a query.
        
        Args:
            sql_query: The SQL query
            database: Database name
            
        Returns:
            Cached results or None if not found/expired
        """
        cache_key = self._get_cache_key(sql_query, database)
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            if time.time() - entry['timestamp'] < self.ttl_seconds:
                entry['hit_count'] = entry.get('hit_count', 0) + 1
                return entry['data']
            else:
                # Expired
                del self.memory_cache[cache_key]
        
        # Check disk cache
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    entry = json.load(f)
                
                if time.time() - entry['timestamp'] < self.ttl_seconds:
                    # Load into memory cache
                    self.memory_cache[cache_key] = entry
                    return entry['data']
                else:
                    # Expired, delete file
                    cache_file.unlink()
            except Exception:
                pass
        
        return None
    
    def set(self, sql_query: str, results: Any, database: str = '', 
            metadata: Optional[Dict] = None):
        """
        Cache query results.
        
        Args:
            sql_query: The SQL query
            results: Query results to cache
            database: Database name
            metadata: Optional metadata about the query
        """
        cache_key = self._get_cache_key(sql_query, database)
        
        entry = {
            'timestamp': time.time(),
            'sql_query': sql_query,
            'database': database,
            'data': results,
            'metadata': metadata or {},
            'hit_count': 0
        }
        
        # Store in memory cache
        self.memory_cache[cache_key] = entry
        
        # Store in disk cache
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(entry, f, default=str)
        except Exception as e:
            # If serialization fails, just skip disk cache
            pass
    
    def invalidate(self, sql_query: str = None, database: str = None):
        """
        Invalidate cache entries.
        
        Args:
            sql_query: Specific query to invalidate (None = all)
            database: Database to invalidate (None = all)
        """
        if sql_query:
            cache_key = self._get_cache_key(sql_query, database or '')
            
            # Remove from memory
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]
            
            # Remove from disk
            cache_file = self.cache_dir / f"{cache_key}.json"
            if cache_file.exists():
                cache_file.unlink()
        else:
            # Clear all cache
            self.memory_cache.clear()
            for cache_file in self.cache_dir.glob('*.json'):
                cache_file.unlink()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(self.memory_cache)
        total_hits = sum(entry.get('hit_count', 0) for entry in self.memory_cache.values())
        
        disk_entries = len(list(self.cache_dir.glob('*.json')))
        
        return {
            'memory_entries': total_entries,
            'disk_entries': disk_entries,
            'total_hits': total_hits,
            'ttl_seconds': self.ttl_seconds
        }
    
    def cleanup_expired(self):
        """Remove expired cache entries."""
        current_time = time.time()
        
        # Clean memory cache
        expired_keys = [
            key for key, entry in self.memory_cache.items()
            if current_time - entry['timestamp'] >= self.ttl_seconds
        ]
        for key in expired_keys:
            del self.memory_cache[key]
        
        # Clean disk cache
        for cache_file in self.cache_dir.glob('*.json'):
            try:
                with open(cache_file, 'r') as f:
                    entry = json.load(f)
                
                if current_time - entry['timestamp'] >= self.ttl_seconds:
                    cache_file.unlink()
            except Exception:
                # If we can't read it, delete it
                cache_file.unlink()
