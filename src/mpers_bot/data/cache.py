"""Data caching module"""

import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
import logging
from mpers_bot.data.structures import OHLCV, Timeframe


logger = logging.getLogger(__name__)


class CacheError(Exception):
    """Base exception for cache errors"""

    pass


class DataCache:
    """
    Data caching system with both memory and file-based storage

    Features:
    - In-memory LRU cache for fast access
    - File-based persistent cache
    - Automatic cache invalidation based on TTL
    - Support for multiple timeframes
    """

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        ttl_minutes: Optional[Dict[str, int]] = None,
        max_memory_items: int = 100,
    ):
        """
        Initialize data cache

        Args:
            cache_dir: Directory for file-based cache. If None, uses ./data/cache
            ttl_minutes: TTL in minutes for each timeframe. If None, uses defaults.
            max_memory_items: Maximum number of items in memory cache
        """
        self.cache_dir = Path(cache_dir) if cache_dir else Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Default TTL values (in minutes)
        self.ttl_minutes = ttl_minutes or {
            "1m": 5,  # 5 minutes for M1
            "5m": 10,  # 10 minutes for M5
            "15m": 30,  # 30 minutes for M15
            "1h": 120,  # 2 hours for H1
            "4h": 480,  # 8 hours for H4
            "1d": 1440,  # 24 hours for D1
        }

        self.max_memory_items = max_memory_items
        self._memory_cache: Dict[str, tuple] = {}  # {cache_key: (data, timestamp)}

        logger.info(f"DataCache initialized with cache_dir={self.cache_dir}")

    def get(
        self, symbol: str, timeframe: Timeframe, force_refresh: bool = False
    ) -> Optional[OHLCV]:
        """
        Get cached OHLCV data

        Args:
            symbol: Trading symbol
            timeframe: Data timeframe
            force_refresh: If True, bypass cache and return None

        Returns:
            Cached OHLCV data or None if not in cache or expired
        """
        if force_refresh:
            return None

        cache_key = self._get_cache_key(symbol, timeframe)

        # Try memory cache first
        cached_data = self._get_from_memory(cache_key, timeframe)
        if cached_data is not None:
            logger.debug(f"Cache hit (memory) for {cache_key}")
            return cached_data

        # Try file cache
        cached_data = self._get_from_file(cache_key, timeframe)
        if cached_data is not None:
            logger.debug(f"Cache hit (file) for {cache_key}")
            # Store in memory cache for faster access next time
            self._store_in_memory(cache_key, cached_data)
            return cached_data

        logger.debug(f"Cache miss for {cache_key}")
        return None

    def set(self, ohlcv: OHLCV):
        """
        Store OHLCV data in cache

        Args:
            ohlcv: OHLCV data to cache
        """
        cache_key = self._get_cache_key(ohlcv.symbol, ohlcv.timeframe)

        # Store in memory cache
        self._store_in_memory(cache_key, ohlcv)

        # Store in file cache
        self._store_in_file(cache_key, ohlcv)

        logger.debug(f"Cached data for {cache_key}")

    def invalidate(self, symbol: str, timeframe: Timeframe):
        """
        Invalidate cache for a specific symbol and timeframe

        Args:
            symbol: Trading symbol
            timeframe: Data timeframe
        """
        cache_key = self._get_cache_key(symbol, timeframe)

        # Remove from memory cache
        if cache_key in self._memory_cache:
            del self._memory_cache[cache_key]

        # Remove from file cache
        cache_file = self._get_cache_file_path(cache_key)
        if cache_file.exists():
            cache_file.unlink()

        logger.debug(f"Invalidated cache for {cache_key}")

    def clear(self):
        """Clear all cached data"""
        # Clear memory cache
        self._memory_cache.clear()

        # Clear file cache
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()

        logger.info("Cleared all cache")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dictionary with cache statistics
        """
        file_cache_count = len(list(self.cache_dir.glob("*.pkl")))
        memory_cache_count = len(self._memory_cache)

        return {
            "memory_cache_items": memory_cache_count,
            "file_cache_items": file_cache_count,
            "cache_dir": str(self.cache_dir),
            "max_memory_items": self.max_memory_items,
        }

    def _get_cache_key(self, symbol: str, timeframe: Timeframe) -> str:
        """Generate cache key from symbol and timeframe"""
        return f"{symbol}_{timeframe.value}"

    def _get_from_memory(
        self, cache_key: str, timeframe: Timeframe
    ) -> Optional[OHLCV]:
        """Get data from memory cache"""
        if cache_key not in self._memory_cache:
            return None

        data, timestamp = self._memory_cache[cache_key]

        # Check if cache is expired
        if self._is_expired(timestamp, timeframe):
            del self._memory_cache[cache_key]
            return None

        return data

    def _store_in_memory(self, cache_key: str, data: OHLCV):
        """Store data in memory cache with LRU eviction"""
        # If cache is full, remove oldest item
        if len(self._memory_cache) >= self.max_memory_items:
            oldest_key = min(
                self._memory_cache.keys(), key=lambda k: self._memory_cache[k][1]
            )
            del self._memory_cache[oldest_key]

        self._memory_cache[cache_key] = (data, datetime.now())

    def _get_from_file(self, cache_key: str, timeframe: Timeframe) -> Optional[OHLCV]:
        """Get data from file cache"""
        cache_file = self._get_cache_file_path(cache_key)

        if not cache_file.exists():
            return None

        try:
            # Check file modification time
            mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if self._is_expired(mtime, timeframe):
                cache_file.unlink()
                return None

            # Load cached data
            with open(cache_file, "rb") as f:
                data = pickle.load(f)

            return data

        except Exception as e:
            logger.error(f"Error reading cache file {cache_file}: {e}")
            # If corrupted, remove the cache file
            if cache_file.exists():
                cache_file.unlink()
            return None

    def _store_in_file(self, cache_key: str, data: OHLCV):
        """Store data in file cache"""
        cache_file = self._get_cache_file_path(cache_key)

        try:
            with open(cache_file, "wb") as f:
                pickle.dump(data, f)
        except Exception as e:
            logger.error(f"Error writing cache file {cache_file}: {e}")
            raise CacheError(f"Failed to write cache: {e}") from e

    def _get_cache_file_path(self, cache_key: str) -> Path:
        """Get file path for cache key"""
        return self.cache_dir / f"{cache_key}.pkl"

    def _is_expired(self, timestamp: datetime, timeframe: Timeframe) -> bool:
        """Check if cache is expired based on TTL"""
        ttl = self.ttl_minutes.get(timeframe.value, 60)
        age = datetime.now() - timestamp
        return age > timedelta(minutes=ttl)
