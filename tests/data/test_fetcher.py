"""Tests for data fetcher module"""

import pytest
from datetime import datetime, timedelta
from mpers_bot.data.fetcher import (
    MarketDataFetcher,
    DataFetcherError,
)
from mpers_bot.data.structures import Timeframe, OHLCV, Candle


class TestMarketDataFetcher:
    """Tests for MarketDataFetcher"""

    @pytest.fixture
    def fetcher(self):
        """Create a fetcher instance"""
        return MarketDataFetcher()

    def test_fetcher_initialization(self, fetcher):
        """Test fetcher initialization"""
        assert fetcher is not None
        assert len(fetcher.available_symbols) > 0

    def test_get_available_symbols(self, fetcher):
        """Test getting available symbols"""
        symbols = fetcher.get_available_symbols()
        assert isinstance(symbols, list)
        assert len(symbols) > 0
        assert "EURUSD" in symbols

    def test_fetch_ohlcv(self, fetcher):
        """Test fetching OHLCV data"""
        ohlcv = fetcher.fetch_ohlcv(
            symbol="EURUSD", timeframe=Timeframe.M5, limit=10
        )
        assert isinstance(ohlcv, OHLCV)
        assert ohlcv.symbol == "EURUSD"
        assert ohlcv.timeframe == Timeframe.M5
        assert len(ohlcv) > 0

    def test_fetch_ohlcv_with_dates(self, fetcher):
        """Test fetching OHLCV data with date range"""
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=1)
        ohlcv = fetcher.fetch_ohlcv(
            symbol="EURUSD",
            timeframe=Timeframe.M5,
            start_date=start_date,
            end_date=end_date,
        )
        assert isinstance(ohlcv, OHLCV)
        assert len(ohlcv) > 0
        # Check that candles are within the date range (allowing some tolerance)
        if len(ohlcv) > 0:
            assert ohlcv.candles[0].timestamp >= start_date - timedelta(minutes=5)
            assert ohlcv.candles[-1].timestamp <= end_date + timedelta(minutes=5)

    def test_fetch_ohlcv_invalid_symbol(self, fetcher):
        """Test fetching OHLCV data with invalid symbol"""
        with pytest.raises(DataFetcherError):
            fetcher.fetch_ohlcv(
                symbol="INVALID", timeframe=Timeframe.M5, limit=10
            )

    def test_fetch_latest_candle(self, fetcher):
        """Test fetching latest candle"""
        candle = fetcher.fetch_latest_candle(symbol="EURUSD", timeframe=Timeframe.M5)
        assert isinstance(candle, Candle)
        assert candle.timeframe == Timeframe.M5

    def test_fetch_latest_candle_invalid_symbol(self, fetcher):
        """Test fetching latest candle with invalid symbol"""
        with pytest.raises(DataFetcherError):
            fetcher.fetch_latest_candle(symbol="INVALID", timeframe=Timeframe.M5)

    def test_fetch_multiple_timeframes(self, fetcher):
        """Test fetching data for multiple timeframes"""
        timeframes = [Timeframe.M1, Timeframe.M5, Timeframe.H1]
        for tf in timeframes:
            ohlcv = fetcher.fetch_ohlcv(
                symbol="EURUSD", timeframe=tf, limit=5
            )
            assert ohlcv.timeframe == tf
            assert len(ohlcv) > 0

    def test_fetch_ohlcv_limit(self, fetcher):
        """Test fetching OHLCV data with limit"""
        limit = 20
        ohlcv = fetcher.fetch_ohlcv(
            symbol="EURUSD", timeframe=Timeframe.M5, limit=limit
        )
        # The actual count might be slightly different due to date rounding
        assert len(ohlcv) >= limit * 0.9  # Allow 10% tolerance

    def test_fetcher_with_config(self):
        """Test fetcher initialization with config"""
        config = {"api_key": "test_key", "base_url": "https://example.com"}
        fetcher = MarketDataFetcher(config=config)
        assert fetcher.config == config
