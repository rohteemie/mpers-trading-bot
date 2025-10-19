"""Data validation module"""

from datetime import timedelta
from typing import List, Optional
import logging
import pandas as pd
from mpers_bot.data.structures import OHLCV, Candle


logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Base exception for validation errors"""

    pass


class DataValidator:
    """Validator for OHLCV market data"""

    def __init__(self, strict_mode: bool = False):
        """
        Initialize data validator

        Args:
            strict_mode: If True, validation errors raise exceptions.
                        If False, validation issues are logged as warnings.
        """
        self.strict_mode = strict_mode

    def validate_candle(self, candle: Candle) -> bool:
        """
        Validate a single candle

        Args:
            candle: Candle to validate

        Returns:
            True if valid, False otherwise

        Raises:
            ValidationError: If strict_mode is True and validation fails
        """
        errors = []

        # Check for NaN values
        if any(
            pd.isna(val)
            for val in [candle.open, candle.high, candle.low, candle.close, candle.volume]
        ):
            errors.append("Candle contains NaN values")

        # Check price relationships
        if candle.high < candle.open or candle.high < candle.close:
            errors.append(
                f"High price {candle.high} is less than open/close "
                f"({candle.open}/{candle.close})"
            )

        if candle.low > candle.open or candle.low > candle.close:
            errors.append(
                f"Low price {candle.low} is greater than open/close "
                f"({candle.open}/{candle.close})"
            )

        # Check for negative values
        if candle.volume < 0:
            errors.append(f"Volume is negative: {candle.volume}")

        if any(price < 0 for price in [candle.open, candle.high, candle.low, candle.close]):
            errors.append("Price values cannot be negative")

        # Check for zero prices (unusual but not impossible)
        if any(
            price == 0 for price in [candle.open, candle.high, candle.low, candle.close]
        ):
            logger.warning(f"Candle at {candle.timestamp} has zero price values")

        if errors:
            error_msg = f"Candle validation failed at {candle.timestamp}: {'; '.join(errors)}"
            if self.strict_mode:
                raise ValidationError(error_msg)
            logger.warning(error_msg)
            return False

        return True

    def validate_ohlcv(self, ohlcv: OHLCV) -> bool:
        """
        Validate OHLCV data structure

        Args:
            ohlcv: OHLCV object to validate

        Returns:
            True if all candles are valid, False otherwise

        Raises:
            ValidationError: If strict_mode is True and validation fails
        """
        if not ohlcv.candles:
            error_msg = "OHLCV object has no candles"
            if self.strict_mode:
                raise ValidationError(error_msg)
            logger.warning(error_msg)
            return False

        # Validate each candle
        all_valid = True
        for candle in ohlcv.candles:
            if not self.validate_candle(candle):
                all_valid = False

        # Check for duplicate timestamps
        timestamps = [c.timestamp for c in ohlcv.candles]
        if len(timestamps) != len(set(timestamps)):
            error_msg = f"OHLCV for {ohlcv.symbol} contains duplicate timestamps"
            if self.strict_mode:
                raise ValidationError(error_msg)
            logger.warning(error_msg)
            all_valid = False

        # Check if candles are sorted by timestamp
        sorted_timestamps = sorted(timestamps)
        if timestamps != sorted_timestamps:
            error_msg = f"OHLCV for {ohlcv.symbol} candles are not sorted by timestamp"
            logger.info(error_msg)
            # This is automatically fixed by OHLCV, so not an error

        # Validate timeframe consistency
        if not self._validate_timeframe_consistency(ohlcv):
            all_valid = False

        return all_valid

    def _validate_timeframe_consistency(self, ohlcv: OHLCV) -> bool:
        """
        Check if candle timestamps are consistent with the timeframe

        Args:
            ohlcv: OHLCV object to validate

        Returns:
            True if timestamps are consistent, False otherwise
        """
        if len(ohlcv.candles) < 2:
            return True

        expected_delta = timedelta(minutes=ohlcv.timeframe.minutes)
        inconsistencies = []

        for i in range(1, len(ohlcv.candles)):
            delta = ohlcv.candles[i].timestamp - ohlcv.candles[i - 1].timestamp
            if delta != expected_delta:
                inconsistencies.append(
                    f"Gap between candles {i-1} and {i}: expected {expected_delta}, "
                    f"got {delta}"
                )

        if inconsistencies:
            error_msg = (
                f"Timeframe consistency issues for {ohlcv.symbol} "
                f"{ohlcv.timeframe.value}: {'; '.join(inconsistencies[:5])}"
            )
            if len(inconsistencies) > 5:
                error_msg += f" (and {len(inconsistencies) - 5} more)"

            logger.warning(error_msg)
            return False

        return True

    def validate_dataframe(
        self, df: pd.DataFrame, required_columns: Optional[List[str]] = None
    ) -> bool:
        """
        Validate a pandas DataFrame containing OHLCV data

        Args:
            df: DataFrame to validate
            required_columns: List of required column names

        Returns:
            True if valid, False otherwise

        Raises:
            ValidationError: If strict_mode is True and validation fails
        """
        if required_columns is None:
            required_columns = ["open", "high", "low", "close", "volume"]

        errors = []

        # Check if DataFrame is empty
        if df.empty:
            errors.append("DataFrame is empty")

        # Check for required columns
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")

        if not errors:
            # Check for NaN values
            nan_columns = df[required_columns].isna().sum()
            nan_columns = nan_columns[nan_columns > 0]
            if not nan_columns.empty:
                errors.append(f"NaN values found in columns: {nan_columns.to_dict()}")

            # Check for negative values in OHLC
            for col in ["open", "high", "low", "close"]:
                if col in df.columns and (df[col] < 0).any():
                    errors.append(f"Negative values found in {col} column")

            # Check for negative volume
            if "volume" in df.columns and (df["volume"] < 0).any():
                errors.append("Negative volume values found")

        if errors:
            error_msg = f"DataFrame validation failed: {'; '.join(errors)}"
            if self.strict_mode:
                raise ValidationError(error_msg)
            logger.warning(error_msg)
            return False

        return True

    def check_data_gaps(
        self, ohlcv: OHLCV, max_gap_multiple: int = 2
    ) -> List[tuple]:
        """
        Check for gaps in the data

        Args:
            ohlcv: OHLCV object to check
            max_gap_multiple: Maximum allowed gap as multiple of timeframe

        Returns:
            List of tuples (start_timestamp, end_timestamp) representing gaps
        """
        if len(ohlcv.candles) < 2:
            return []

        expected_delta = timedelta(minutes=ohlcv.timeframe.minutes)
        max_gap = expected_delta * max_gap_multiple
        gaps = []

        for i in range(1, len(ohlcv.candles)):
            delta = ohlcv.candles[i].timestamp - ohlcv.candles[i - 1].timestamp
            if delta > max_gap:
                gaps.append((ohlcv.candles[i - 1].timestamp, ohlcv.candles[i].timestamp))

        if gaps:
            logger.info(f"Found {len(gaps)} data gaps in {ohlcv.symbol} {ohlcv.timeframe.value}")

        return gaps

    def validate_price_range(
        self, candle: Candle, min_price: float = 0.0001, max_price: float = 1000000.0
    ) -> bool:
        """
        Validate that prices are within a reasonable range

        Args:
            candle: Candle to validate
            min_price: Minimum acceptable price
            max_price: Maximum acceptable price

        Returns:
            True if prices are in range, False otherwise
        """
        prices = [candle.open, candle.high, candle.low, candle.close]

        for price in prices:
            if price < min_price or price > max_price:
                error_msg = (
                    f"Price {price} out of range [{min_price}, {max_price}] "
                    f"at {candle.timestamp}"
                )
                if self.strict_mode:
                    raise ValidationError(error_msg)
                logger.warning(error_msg)
                return False

        return True
