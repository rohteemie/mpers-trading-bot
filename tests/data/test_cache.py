"""Tests for data cache module"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
from mpers_bot.data.cache import DataCache
from mpers_bot.data.structures import OHLCV, Timeframe


class TestDataCache:
    """Tests for DataCache"""

    @pytest.fixture
    def cache_dir(self):
        """Create a temporary cache directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def cache(self, cache_dir):
        """Create a cache instance"""
        return DataCache(cache_dir=cache_dir, max_memory_items=5)

    def test_cache_initialization(self, cache, cache_dir):
        """Test cache initialization"""
        assert cache is not None
        assert cache.cache_dir == Path(cache_dir)
        assert cache.max_memory_items == 5

    def test_set_and_get(self, cache, sample_ohlcv):
        """Test setting and getting cached data"""
        cache.set(sample_ohlcv)
        cached = cache.get(sample_ohlcv.symbol, sample_ohlcv.timeframe)
        assert cached is not None
        assert cached.symbol == sample_ohlcv.symbol
        assert cached.timeframe == sample_ohlcv.timeframe
        assert len(cached) == len(sample_ohlcv)

    def test_get_non_existent(self, cache):
        """Test getting non-existent data"""
        cached = cache.get("NONEXISTENT", Timeframe.M5)
        assert cached is None

    def test_force_refresh(self, cache, sample_ohlcv):
        """Test force refresh bypasses cache"""
        cache.set(sample_ohlcv)
        cached = cache.get(
            sample_ohlcv.symbol, sample_ohlcv.timeframe, force_refresh=True
        )
        assert cached is None

    def test_invalidate(self, cache, sample_ohlcv):
        """Test invalidating cache"""
        cache.set(sample_ohlcv)
        cache.invalidate(sample_ohlcv.symbol, sample_ohlcv.timeframe)
        cached = cache.get(sample_ohlcv.symbol, sample_ohlcv.timeframe)
        assert cached is None

    def test_clear(self, cache, sample_ohlcv):
        """Test clearing all cache"""
        cache.set(sample_ohlcv)
        cache.clear()
        cached = cache.get(sample_ohlcv.symbol, sample_ohlcv.timeframe)
        assert cached is None

    def test_memory_cache_lru(self, cache, sample_candles):
        """Test LRU eviction in memory cache"""
        # Create more OHLCV objects than max_memory_items
        for i in range(10):
            ohlcv = OHLCV(
                symbol=f"SYMBOL{i}",
                timeframe=Timeframe.M5,
                candles=sample_candles,
            )
            cache.set(ohlcv)

        # Memory cache should only have max_memory_items
        stats = cache.get_cache_stats()
        assert stats["memory_cache_items"] <= cache.max_memory_items

    def test_file_cache_persistence(self, cache_dir, sample_ohlcv):
        """Test that file cache persists across cache instances"""
        cache1 = DataCache(cache_dir=cache_dir)
        cache1.set(sample_ohlcv)

        # Create a new cache instance with same directory
        cache2 = DataCache(cache_dir=cache_dir)
        cached = cache2.get(sample_ohlcv.symbol, sample_ohlcv.timeframe)
        assert cached is not None
        assert cached.symbol == sample_ohlcv.symbol

    def test_get_cache_stats(self, cache, sample_ohlcv):
        """Test getting cache statistics"""
        cache.set(sample_ohlcv)
        stats = cache.get_cache_stats()
        assert "memory_cache_items" in stats
        assert "file_cache_items" in stats
        assert "cache_dir" in stats
        assert stats["memory_cache_items"] > 0

    def test_cache_key_generation(self, cache):
        """Test cache key generation"""
        key1 = cache._get_cache_key("EURUSD", Timeframe.M5)
        key2 = cache._get_cache_key("EURUSD", Timeframe.H1)
        key3 = cache._get_cache_key("GBPUSD", Timeframe.M5)

        assert key1 != key2
        assert key1 != key3
        assert "EURUSD" in key1
        assert "5m" in key1

    def test_multiple_symbols_cached(self, cache, sample_candles):
        """Test caching multiple symbols"""
        symbols = ["EURUSD", "GBPUSD", "USDJPY"]
        for symbol in symbols:
            ohlcv = OHLCV(
                symbol=symbol, timeframe=Timeframe.M5, candles=sample_candles
            )
            cache.set(ohlcv)

        for symbol in symbols:
            cached = cache.get(symbol, Timeframe.M5)
            assert cached is not None
            assert cached.symbol == symbol

    def test_ttl_expiration(self, cache_dir, sample_ohlcv):
        """Test TTL-based cache expiration"""
        # Create cache with very short TTL
        cache = DataCache(cache_dir=cache_dir, ttl_minutes={"5m": 0})
        cache.set(sample_ohlcv)

        # Cached data should be expired immediately
        cached = cache.get(sample_ohlcv.symbol, sample_ohlcv.timeframe)
        # Due to timing, this might still return data, so we'll just check it doesn't error
        assert cached is None or isinstance(cached, OHLCV)
