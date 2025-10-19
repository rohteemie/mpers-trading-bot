"""Tests for data structures module"""

import pytest
from datetime import datetime, timedelta
import pandas as pd
from mpers_bot.data.structures import Candle, OHLCV, Timeframe


class TestTimeframe:
    """Tests for Timeframe enum"""

    def test_timeframe_values(self):
        """Test timeframe values"""
        assert Timeframe.M1.value == "1m"
        assert Timeframe.M5.value == "5m"
        assert Timeframe.M15.value == "15m"
        assert Timeframe.H1.value == "1h"
        assert Timeframe.H4.value == "4h"
        assert Timeframe.D1.value == "1d"

    def test_timeframe_minutes(self):
        """Test timeframe minutes property"""
        assert Timeframe.M1.minutes == 1
        assert Timeframe.M5.minutes == 5
        assert Timeframe.M15.minutes == 15
        assert Timeframe.H1.minutes == 60
        assert Timeframe.H4.minutes == 240
        assert Timeframe.D1.minutes == 1440

    def test_from_string(self):
        """Test creating timeframe from string"""
        assert Timeframe.from_string("1m") == Timeframe.M1
        assert Timeframe.from_string("5m") == Timeframe.M5
        assert Timeframe.from_string("1h") == Timeframe.H1

    def test_from_string_invalid(self):
        """Test creating timeframe from invalid string"""
        with pytest.raises(ValueError):
            Timeframe.from_string("invalid")


class TestCandle:
    """Tests for Candle dataclass"""

    def test_candle_creation(self, sample_candle):
        """Test creating a valid candle"""
        assert sample_candle.timestamp == datetime(2024, 1, 1, 12, 0, 0)
        assert sample_candle.open == 1.0850
        assert sample_candle.high == 1.0875
        assert sample_candle.low == 1.0840
        assert sample_candle.close == 1.0865
        assert sample_candle.volume == 1000.0
        assert sample_candle.timeframe == Timeframe.M5

    def test_invalid_high(self):
        """Test candle with invalid high price"""
        with pytest.raises(ValueError):
            Candle(
                timestamp=datetime(2024, 1, 1),
                open=1.0850,
                high=1.0800,  # High less than open
                low=1.0840,
                close=1.0860,
                volume=1000.0,
                timeframe=Timeframe.M5,
            )

    def test_invalid_low(self):
        """Test candle with invalid low price"""
        with pytest.raises(ValueError):
            Candle(
                timestamp=datetime(2024, 1, 1),
                open=1.0850,
                high=1.0900,
                low=1.0870,  # Low greater than open
                close=1.0860,
                volume=1000.0,
                timeframe=Timeframe.M5,
            )

    def test_negative_volume(self):
        """Test candle with negative volume"""
        with pytest.raises(ValueError):
            Candle(
                timestamp=datetime(2024, 1, 1),
                open=1.0850,
                high=1.0900,
                low=1.0840,
                close=1.0860,
                volume=-1000.0,
                timeframe=Timeframe.M5,
            )

    def test_is_bullish(self, sample_candle):
        """Test bullish candle detection"""
        assert sample_candle.is_bullish is True

    def test_is_bearish(self):
        """Test bearish candle detection"""
        candle = Candle(
            timestamp=datetime(2024, 1, 1),
            open=1.0850,
            high=1.0875,
            low=1.0840,
            close=1.0845,  # Close < open
            volume=1000.0,
            timeframe=Timeframe.M5,
        )
        assert candle.is_bearish is True

    def test_body_size(self, sample_candle):
        """Test candle body size calculation"""
        expected_body = abs(sample_candle.close - sample_candle.open)
        assert sample_candle.body_size == expected_body

    def test_upper_wick(self, sample_candle):
        """Test upper wick calculation"""
        expected_wick = sample_candle.high - max(
            sample_candle.open, sample_candle.close
        )
        assert sample_candle.upper_wick == expected_wick

    def test_lower_wick(self, sample_candle):
        """Test lower wick calculation"""
        expected_wick = min(sample_candle.open, sample_candle.close) - sample_candle.low
        assert sample_candle.lower_wick == expected_wick

    def test_range(self, sample_candle):
        """Test candle range calculation"""
        expected_range = sample_candle.high - sample_candle.low
        assert sample_candle.range == expected_range

    def test_to_dict(self, sample_candle):
        """Test converting candle to dictionary"""
        candle_dict = sample_candle.to_dict()
        assert candle_dict["timestamp"] == sample_candle.timestamp
        assert candle_dict["open"] == sample_candle.open
        assert candle_dict["high"] == sample_candle.high
        assert candle_dict["low"] == sample_candle.low
        assert candle_dict["close"] == sample_candle.close
        assert candle_dict["volume"] == sample_candle.volume
        assert candle_dict["timeframe"] == sample_candle.timeframe.value


class TestOHLCV:
    """Tests for OHLCV dataclass"""

    def test_ohlcv_creation(self, sample_ohlcv):
        """Test creating OHLCV object"""
        assert sample_ohlcv.symbol == "EURUSD"
        assert sample_ohlcv.timeframe == Timeframe.M5
        assert len(sample_ohlcv.candles) == 10

    def test_candles_sorted(self):
        """Test that candles are automatically sorted"""
        candles = [
            Candle(
                timestamp=datetime(2024, 1, 1, 12, 10, 0),
                open=1.0850,
                high=1.0875,
                low=1.0840,
                close=1.0865,
                volume=1000.0,
                timeframe=Timeframe.M5,
            ),
            Candle(
                timestamp=datetime(2024, 1, 1, 12, 0, 0),
                open=1.0850,
                high=1.0875,
                low=1.0840,
                close=1.0865,
                volume=1000.0,
                timeframe=Timeframe.M5,
            ),
        ]
        ohlcv = OHLCV(symbol="EURUSD", timeframe=Timeframe.M5, candles=candles)
        assert ohlcv.candles[0].timestamp < ohlcv.candles[1].timestamp

    def test_add_candle(self, sample_ohlcv):
        """Test adding a candle"""
        new_candle = Candle(
            timestamp=datetime(2024, 1, 1, 13, 0, 0),
            open=1.0900,
            high=1.0925,
            low=1.0890,
            close=1.0915,
            volume=1500.0,
            timeframe=Timeframe.M5,
        )
        initial_count = len(sample_ohlcv)
        sample_ohlcv.add_candle(new_candle)
        assert len(sample_ohlcv) == initial_count + 1

    def test_add_candle_wrong_timeframe(self, sample_ohlcv):
        """Test adding candle with wrong timeframe"""
        wrong_candle = Candle(
            timestamp=datetime(2024, 1, 1, 13, 0, 0),
            open=1.0900,
            high=1.0925,
            low=1.0890,
            close=1.0915,
            volume=1500.0,
            timeframe=Timeframe.H1,  # Wrong timeframe
        )
        with pytest.raises(ValueError):
            sample_ohlcv.add_candle(wrong_candle)

    def test_get_latest(self, sample_ohlcv):
        """Test getting latest candles"""
        latest = sample_ohlcv.get_latest(3)
        assert len(latest) == 3
        assert latest[0].timestamp < latest[1].timestamp < latest[2].timestamp

    def test_get_latest_more_than_available(self, sample_ohlcv):
        """Test getting more candles than available"""
        latest = sample_ohlcv.get_latest(100)
        assert len(latest) == len(sample_ohlcv.candles)

    def test_get_by_date_range(self, sample_ohlcv):
        """Test getting candles by date range"""
        start = datetime(2024, 1, 1, 12, 10, 0)
        end = datetime(2024, 1, 1, 12, 30, 0)
        candles = sample_ohlcv.get_by_date_range(start, end)
        assert all(start <= c.timestamp <= end for c in candles)

    def test_to_dataframe(self, sample_ohlcv):
        """Test converting to DataFrame"""
        df = sample_ohlcv.to_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(sample_ohlcv)
        assert "open" in df.columns
        assert "high" in df.columns
        assert "low" in df.columns
        assert "close" in df.columns
        assert "volume" in df.columns

    def test_to_dataframe_empty(self):
        """Test converting empty OHLCV to DataFrame"""
        ohlcv = OHLCV(symbol="EURUSD", timeframe=Timeframe.M5, candles=[])
        df = ohlcv.to_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_from_dataframe(self, sample_ohlcv):
        """Test creating OHLCV from DataFrame"""
        df = sample_ohlcv.to_dataframe()
        new_ohlcv = OHLCV.from_dataframe(df, "EURUSD", Timeframe.M5)
        assert new_ohlcv.symbol == "EURUSD"
        assert new_ohlcv.timeframe == Timeframe.M5
        assert len(new_ohlcv) == len(sample_ohlcv)

    def test_len(self, sample_ohlcv):
        """Test length of OHLCV"""
        assert len(sample_ohlcv) == 10

    def test_getitem(self, sample_ohlcv):
        """Test getting candle by index"""
        candle = sample_ohlcv[0]
        assert isinstance(candle, Candle)
        assert candle == sample_ohlcv.candles[0]
