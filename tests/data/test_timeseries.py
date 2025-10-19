"""Tests for time series handler module"""

import pytest
from datetime import datetime, timedelta
import pandas as pd
from mpers_bot.data.timeseries import TimeSeriesHandler
from mpers_bot.data.structures import OHLCV, Candle, Timeframe


class TestTimeSeriesHandler:
    """Tests for TimeSeriesHandler"""

    @pytest.fixture
    def handler(self):
        """Create a handler instance"""
        return TimeSeriesHandler()

    def test_handler_initialization(self, handler):
        """Test handler initialization"""
        assert handler is not None

    def test_resample_m5_to_h1(self, handler, sample_candles):
        """Test resampling from M5 to H1"""
        # Create more candles to have a complete hour
        base_time = datetime(2024, 1, 1, 12, 0, 0)
        candles = []
        base_price = 1.0850

        for i in range(12):  # 12 * 5min = 1 hour
            timestamp = base_time + timedelta(minutes=5 * i)
            candle = Candle(
                timestamp=timestamp,
                open=base_price + i * 0.0001,
                high=base_price + i * 0.0001 + 0.0005,
                low=base_price + i * 0.0001 - 0.0003,
                close=base_price + i * 0.0001 + 0.0002,
                volume=1000.0,
                timeframe=Timeframe.M5,
            )
            candles.append(candle)

        ohlcv = OHLCV(symbol="EURUSD", timeframe=Timeframe.M5, candles=candles)
        resampled = handler.resample(ohlcv, Timeframe.H1)

        assert resampled.timeframe == Timeframe.H1
        assert len(resampled) <= len(ohlcv)

    def test_resample_invalid_downsampling(self, handler, sample_ohlcv):
        """Test that downsampling raises error"""
        with pytest.raises(ValueError):
            handler.resample(sample_ohlcv, Timeframe.M1)

    def test_slice_by_time(self, handler, sample_ohlcv):
        """Test slicing OHLCV by time range"""
        start = sample_ohlcv.candles[2].timestamp
        end = sample_ohlcv.candles[7].timestamp
        sliced = handler.slice_by_time(sample_ohlcv, start=start, end=end)

        assert len(sliced) <= len(sample_ohlcv)
        assert all(start <= c.timestamp <= end for c in sliced.candles)

    def test_slice_by_time_no_start(self, handler, sample_ohlcv):
        """Test slicing with no start time"""
        end = sample_ohlcv.candles[5].timestamp
        sliced = handler.slice_by_time(sample_ohlcv, end=end)

        assert len(sliced) <= len(sample_ohlcv)
        assert all(c.timestamp <= end for c in sliced.candles)

    def test_slice_by_time_no_end(self, handler, sample_ohlcv):
        """Test slicing with no end time"""
        start = sample_ohlcv.candles[3].timestamp
        sliced = handler.slice_by_time(sample_ohlcv, start=start)

        assert len(sliced) <= len(sample_ohlcv)
        assert all(c.timestamp >= start for c in sliced.candles)

    def test_get_rolling_window(self, handler, sample_ohlcv):
        """Test getting rolling windows"""
        window_size = 3
        windows = handler.get_rolling_window(sample_ohlcv, window_size=window_size)

        assert len(windows) > 0
        assert all(len(w) == window_size for w in windows)
        assert all(isinstance(w, OHLCV) for w in windows)

    def test_get_rolling_window_with_step(self, handler, sample_ohlcv):
        """Test getting rolling windows with step"""
        window_size = 3
        step = 2
        windows = handler.get_rolling_window(
            sample_ohlcv, window_size=window_size, step=step
        )

        expected_count = (len(sample_ohlcv) - window_size) // step + 1
        assert len(windows) == expected_count

    def test_align_multiple_series(self, handler, sample_candles):
        """Test aligning multiple series"""
        ohlcv1 = OHLCV(symbol="EURUSD", timeframe=Timeframe.M5, candles=sample_candles)
        ohlcv2 = OHLCV(symbol="GBPUSD", timeframe=Timeframe.M5, candles=sample_candles)

        aligned = handler.align_multiple_series([ohlcv1, ohlcv2], method="inner")

        assert len(aligned) == 2
        assert len(aligned[0]) == len(aligned[1])

    def test_align_multiple_series_different_lengths(self, handler, sample_candles):
        """Test aligning series with different lengths"""
        ohlcv1 = OHLCV(symbol="EURUSD", timeframe=Timeframe.M5, candles=sample_candles)
        ohlcv2 = OHLCV(
            symbol="GBPUSD", timeframe=Timeframe.M5, candles=sample_candles[:5]
        )

        aligned = handler.align_multiple_series([ohlcv1, ohlcv2], method="inner")

        assert len(aligned) == 2
        assert len(aligned[0]) <= len(ohlcv1)
        assert len(aligned[1]) <= len(ohlcv2)

    def test_align_different_timeframes_raises_error(self, handler, sample_candles):
        """Test that aligning different timeframes raises error"""
        candles_h1 = []
        for candle in sample_candles:
            new_candle = Candle(
                timestamp=candle.timestamp,
                open=candle.open,
                high=candle.high,
                low=candle.low,
                close=candle.close,
                volume=candle.volume,
                timeframe=Timeframe.H1,
            )
            candles_h1.append(new_candle)

        ohlcv1 = OHLCV(symbol="EURUSD", timeframe=Timeframe.M5, candles=sample_candles)
        ohlcv2 = OHLCV(symbol="GBPUSD", timeframe=Timeframe.H1, candles=candles_h1)

        with pytest.raises(ValueError):
            handler.align_multiple_series([ohlcv1, ohlcv2])

    def test_calculate_returns(self, handler, sample_ohlcv):
        """Test calculating returns"""
        returns = handler.calculate_returns(sample_ohlcv)

        assert isinstance(returns, pd.Series)
        assert len(returns) == len(sample_ohlcv)
        # First return should be NaN
        assert pd.isna(returns.iloc[0])

    def test_calculate_returns_multi_period(self, handler, sample_ohlcv):
        """Test calculating returns with multiple periods"""
        returns = handler.calculate_returns(sample_ohlcv, period=2)

        assert isinstance(returns, pd.Series)
        # First two returns should be NaN
        assert pd.isna(returns.iloc[0])
        assert pd.isna(returns.iloc[1])

    def test_calculate_volatility_std(self, handler, sample_ohlcv):
        """Test calculating volatility using standard deviation"""
        volatility = handler.calculate_volatility(
            sample_ohlcv, window=5, method="std"
        )

        assert isinstance(volatility, pd.Series)
        assert len(volatility) == len(sample_ohlcv)

    def test_calculate_volatility_atr(self, handler, sample_ohlcv):
        """Test calculating volatility using ATR"""
        volatility = handler.calculate_volatility(
            sample_ohlcv, window=5, method="atr"
        )

        assert isinstance(volatility, pd.Series)
        assert len(volatility) == len(sample_ohlcv)

    def test_calculate_volatility_invalid_method(self, handler, sample_ohlcv):
        """Test calculating volatility with invalid method"""
        with pytest.raises(ValueError):
            handler.calculate_volatility(sample_ohlcv, method="invalid")

    def test_get_summary_statistics(self, handler, sample_ohlcv):
        """Test getting summary statistics"""
        stats = handler.get_summary_statistics(sample_ohlcv)

        assert isinstance(stats, dict)
        assert "count" in stats
        assert "start_date" in stats
        assert "end_date" in stats
        assert "open_first" in stats
        assert "close_last" in stats
        assert "high_max" in stats
        assert "low_min" in stats
        assert "volume_total" in stats
        assert "volume_mean" in stats
        assert "price_change" in stats
        assert "price_change_pct" in stats

        assert stats["count"] == len(sample_ohlcv)

    def test_forward_fill(self, handler):
        """Test forward fill for missing data"""
        base_time = datetime(2024, 1, 1, 12, 0, 0)
        candles = [
            Candle(
                timestamp=base_time,
                open=1.0850,
                high=1.0875,
                low=1.0840,
                close=1.0865,
                volume=1000.0,
                timeframe=Timeframe.M5,
            ),
            # Missing candle at 12:05
            Candle(
                timestamp=base_time + timedelta(minutes=10),
                open=1.0860,
                high=1.0885,
                low=1.0850,
                close=1.0875,
                volume=1100.0,
                timeframe=Timeframe.M5,
            ),
        ]
        ohlcv = OHLCV(symbol="EURUSD", timeframe=Timeframe.M5, candles=candles)
        filled = handler.forward_fill(ohlcv, max_fill=3)

        assert len(filled) >= len(ohlcv)

    def test_pandas_frequency_conversion(self, handler):
        """Test pandas frequency conversion"""
        assert handler._get_pandas_frequency(Timeframe.M1) == "1min"
        assert handler._get_pandas_frequency(Timeframe.M5) == "5min"
        assert handler._get_pandas_frequency(Timeframe.M15) == "15min"
        assert handler._get_pandas_frequency(Timeframe.H1) == "1h"
        assert handler._get_pandas_frequency(Timeframe.H4) == "4h"
        assert handler._get_pandas_frequency(Timeframe.D1) == "1D"
