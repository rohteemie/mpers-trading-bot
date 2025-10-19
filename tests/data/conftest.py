"""Test configuration for data module tests"""
import pytest
from datetime import datetime, timedelta
from mpers_bot.data.structures import Candle, OHLCV, Timeframe


@pytest.fixture
def sample_candle():
    """Create a sample candle for testing"""
    return Candle(
        timestamp=datetime(2024, 1, 1, 12, 0, 0),
        open=1.0850,
        high=1.0875,
        low=1.0840,
        close=1.0865,
        volume=1000.0,
        timeframe=Timeframe.M5,
    )


@pytest.fixture
def sample_candles():
    """Create a list of sample candles for testing"""
    base_time = datetime(2024, 1, 1, 12, 0, 0)
    candles = []
    base_price = 1.0850

    for i in range(10):
        timestamp = base_time + timedelta(minutes=5 * i)
        candle = Candle(
            timestamp=timestamp,
            open=base_price + i * 0.0001,
            high=base_price + i * 0.0001 + 0.0005,
            low=base_price + i * 0.0001 - 0.0003,
            close=base_price + i * 0.0001 + 0.0002,
            volume=1000.0 + i * 100,
            timeframe=Timeframe.M5,
        )
        candles.append(candle)

    return candles


@pytest.fixture
def sample_ohlcv(sample_candles):
    """Create a sample OHLCV object for testing"""
    return OHLCV(symbol="EURUSD", timeframe=Timeframe.M5, candles=sample_candles)
