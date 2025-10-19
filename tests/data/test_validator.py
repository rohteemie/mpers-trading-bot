"""Tests for data validator module"""

import pytest
from datetime import datetime, timedelta
import pandas as pd
from mpers_bot.data.validator import DataValidator, ValidationError
from mpers_bot.data.structures import Candle, OHLCV, Timeframe


class TestDataValidator:
    """Tests for DataValidator"""

    @pytest.fixture
    def validator(self):
        """Create a validator instance"""
        return DataValidator(strict_mode=False)

    @pytest.fixture
    def strict_validator(self):
        """Create a strict validator instance"""
        return DataValidator(strict_mode=True)

    def test_validator_initialization(self, validator):
        """Test validator initialization"""
        assert validator is not None
        assert validator.strict_mode is False

    def test_validate_valid_candle(self, validator, sample_candle):
        """Test validating a valid candle"""
        assert validator.validate_candle(sample_candle) is True

    def test_validate_candle_with_nan(self, validator):
        """Test validating candle with NaN values"""
        # NaN values don't raise ValueError in Candle creation,
        # but validator should catch them
        # We need to bypass the Candle validation to test the validator
        import pandas as pd

        # Create a valid candle first
        candle = Candle(
            timestamp=datetime(2024, 1, 1),
            open=1.0850,
            high=1.0875,
            low=1.0840,
            close=1.0865,
            volume=1000.0,
            timeframe=Timeframe.M5,
        )
        # Manually set NaN to bypass __post_init__ validation
        object.__setattr__(candle, 'open', float('nan'))

        # Now validator should detect the NaN
        assert validator.validate_candle(candle) is False

    def test_validate_candle_invalid_high(self, validator):
        """Test validating candle with invalid high"""
        # This is caught by Candle's own validation
        with pytest.raises(ValueError):
            Candle(
                timestamp=datetime(2024, 1, 1),
                open=1.0850,
                high=1.0800,
                low=1.0840,
                close=1.0865,
                volume=1000.0,
                timeframe=Timeframe.M5,
            )

    def test_validate_candle_negative_volume(self, validator):
        """Test validating candle with negative volume"""
        with pytest.raises(ValueError):
            Candle(
                timestamp=datetime(2024, 1, 1),
                open=1.0850,
                high=1.0875,
                low=1.0840,
                close=1.0865,
                volume=-1000.0,
                timeframe=Timeframe.M5,
            )

    def test_validate_ohlcv(self, validator, sample_ohlcv):
        """Test validating OHLCV data"""
        assert validator.validate_ohlcv(sample_ohlcv) is True

    def test_validate_empty_ohlcv(self, validator):
        """Test validating empty OHLCV"""
        ohlcv = OHLCV(symbol="EURUSD", timeframe=Timeframe.M5, candles=[])
        assert validator.validate_ohlcv(ohlcv) is False

    def test_validate_ohlcv_duplicate_timestamps(self, validator):
        """Test validating OHLCV with duplicate timestamps"""
        candles = [
            Candle(
                timestamp=datetime(2024, 1, 1, 12, 0, 0),
                open=1.0850,
                high=1.0875,
                low=1.0840,
                close=1.0865,
                volume=1000.0,
                timeframe=Timeframe.M5,
            ),
            Candle(
                timestamp=datetime(2024, 1, 1, 12, 0, 0),  # Duplicate
                open=1.0860,
                high=1.0885,
                low=1.0850,
                close=1.0875,
                volume=1100.0,
                timeframe=Timeframe.M5,
            ),
        ]
        ohlcv = OHLCV(symbol="EURUSD", timeframe=Timeframe.M5, candles=candles)
        assert validator.validate_ohlcv(ohlcv) is False

    def test_validate_dataframe(self, validator, sample_ohlcv):
        """Test validating DataFrame"""
        df = sample_ohlcv.to_dataframe()
        assert validator.validate_dataframe(df) is True

    def test_validate_empty_dataframe(self, validator):
        """Test validating empty DataFrame"""
        df = pd.DataFrame()
        assert validator.validate_dataframe(df) is False

    def test_validate_dataframe_missing_columns(self, validator, sample_ohlcv):
        """Test validating DataFrame with missing columns"""
        df = sample_ohlcv.to_dataframe()
        df = df.drop(columns=["volume"])
        assert validator.validate_dataframe(df) is False

    def test_check_data_gaps(self, validator):
        """Test checking for data gaps"""
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
            Candle(
                timestamp=base_time + timedelta(minutes=20),  # Gap of 15 minutes
                open=1.0860,
                high=1.0885,
                low=1.0850,
                close=1.0875,
                volume=1100.0,
                timeframe=Timeframe.M5,
            ),
        ]
        ohlcv = OHLCV(symbol="EURUSD", timeframe=Timeframe.M5, candles=candles)
        gaps = validator.check_data_gaps(ohlcv)
        assert len(gaps) > 0

    def test_check_data_gaps_no_gaps(self, validator, sample_ohlcv):
        """Test checking for data gaps when there are none"""
        gaps = validator.check_data_gaps(sample_ohlcv)
        assert len(gaps) == 0

    def test_validate_price_range(self, validator, sample_candle):
        """Test validating price range"""
        assert validator.validate_price_range(sample_candle) is True

    def test_validate_price_range_out_of_range(self, validator):
        """Test validating price out of range"""
        candle = Candle(
            timestamp=datetime(2024, 1, 1),
            open=2000000.0,  # Unrealistic price
            high=2000100.0,
            low=1999900.0,
            close=2000050.0,
            volume=1000.0,
            timeframe=Timeframe.M5,
        )
        assert validator.validate_price_range(candle) is False

    def test_strict_mode_raises_exception(self, strict_validator):
        """Test that strict mode raises exceptions"""
        ohlcv = OHLCV(symbol="EURUSD", timeframe=Timeframe.M5, candles=[])
        with pytest.raises(ValidationError):
            strict_validator.validate_ohlcv(ohlcv)

    def test_timeframe_consistency(self, validator, sample_ohlcv):
        """Test timeframe consistency validation"""
        assert validator._validate_timeframe_consistency(sample_ohlcv) is True

    def test_timeframe_inconsistency(self, validator):
        """Test timeframe inconsistency detection"""
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
            Candle(
                timestamp=base_time + timedelta(minutes=10),  # Should be 5
                open=1.0860,
                high=1.0885,
                low=1.0850,
                close=1.0875,
                volume=1100.0,
                timeframe=Timeframe.M5,
            ),
        ]
        ohlcv = OHLCV(symbol="EURUSD", timeframe=Timeframe.M5, candles=candles)
        assert validator._validate_timeframe_consistency(ohlcv) is False
