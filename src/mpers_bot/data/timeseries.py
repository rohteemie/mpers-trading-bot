"""Time series data handler module"""

from datetime import datetime
from typing import List, Optional
import logging
import pandas as pd
from mpers_bot.data.structures import OHLCV, Timeframe


logger = logging.getLogger(__name__)


class TimeSeriesHandler:
    """
    Handler for time series operations on OHLCV data

    Features:
    - Resampling to different timeframes
    - Data alignment and synchronization
    - Forward fill and backward fill for missing data
    - Rolling window calculations
    - Data slicing by time ranges
    """

    def __init__(self):
        """Initialize time series handler"""
        logger.info("TimeSeriesHandler initialized")

    def resample(
        self, ohlcv: OHLCV, target_timeframe: Timeframe
    ) -> OHLCV:
        """
        Resample OHLCV data to a different timeframe

        Args:
            ohlcv: Source OHLCV data
            target_timeframe: Target timeframe to resample to

        Returns:
            New OHLCV object with resampled data

        Note:
            Can only resample to higher timeframes (e.g., M1 to M5, H1 to H4)
        """
        if ohlcv.timeframe.minutes >= target_timeframe.minutes:
            raise ValueError(
                "Cannot resample from %s to %s. Target must be higher timeframe.",
                ohlcv.timeframe.value,
                target_timeframe.value,
            )

        # Convert to DataFrame for easier resampling
        df = ohlcv.to_dataframe()

        # Resample using pandas
        freq = self._get_pandas_frequency(target_timeframe)
        resampled = df.resample(freq).agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            }
        )

        # Remove any NaN rows (incomplete periods)
        resampled = resampled.dropna()

        # Convert back to OHLCV
        result = OHLCV.from_dataframe(
            resampled, symbol=ohlcv.symbol, timeframe=target_timeframe
        )

        logger.info(
            "Resampled %d candles from %s to %s, resulting in %d candles",
            len(ohlcv),
            ohlcv.timeframe.value,
            target_timeframe.value,
            len(result),
        )

        return result

    def forward_fill(self, ohlcv: OHLCV, max_fill: int = 3) -> OHLCV:
        """
        Forward fill missing data points

        Args:
            ohlcv: OHLCV data with potential gaps
            max_fill: Maximum number of consecutive missing values to fill

        Returns:
            New OHLCV object with filled data
        """
        if len(ohlcv) < 2:
            return ohlcv

        df = ohlcv.to_dataframe()

        # Create complete time range
        start = df.index.min()
        end = df.index.max()
        freq = self._get_pandas_frequency(ohlcv.timeframe)
        complete_index = pd.date_range(start=start, end=end, freq=freq)

        # Reindex to include all timestamps
        df = df.reindex(complete_index)

        # Forward fill with limit
        df = df.ffill(limit=max_fill)

        # Drop any remaining NaN values
        df = df.dropna()

        # Reset index to make timestamp a column for from_dataframe
        df = df.reset_index()
        df = df.rename(columns={"index": "timestamp"})

        # Convert back to OHLCV
        result = OHLCV.from_dataframe(
            df, symbol=ohlcv.symbol, timeframe=ohlcv.timeframe
        )

        if len(result) > len(ohlcv):
            logger.info(
                "Forward filled %d missing candles for %s",
                len(result) - len(ohlcv),
                ohlcv.symbol,
            )

        return result

    def slice_by_time(
        self,
        ohlcv: OHLCV,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> OHLCV:
        """
        Slice OHLCV data by time range

        Args:
            ohlcv: Source OHLCV data
            start: Start datetime (inclusive). If None, starts from beginning
            end: End datetime (inclusive). If None, goes to end

        Returns:
            New OHLCV object with sliced data
        """
        candles = ohlcv.candles

        if start is not None:
            candles = [c for c in candles if c.timestamp >= start]

        if end is not None:
            candles = [c for c in candles if c.timestamp <= end]

        result = OHLCV(symbol=ohlcv.symbol, timeframe=ohlcv.timeframe, candles=candles)

        logger.debug(
            "Sliced %d candles to %d candles for %s from %s to %s",
            len(ohlcv),
            len(result),
            ohlcv.symbol,
            start,
            end,
        )

        return result

    def get_rolling_window(
        self, ohlcv: OHLCV, window_size: int, step: int = 1
    ) -> List[OHLCV]:
        """
        Get rolling windows of OHLCV data

        Args:
            ohlcv: Source OHLCV data
            window_size: Size of each window in number of candles
            step: Step size between windows

        Returns:
            List of OHLCV objects, each containing a window of data
        """
        windows = []

        for i in range(0, len(ohlcv) - window_size + 1, step):
            window_candles = ohlcv.candles[i:i + window_size]
            window = OHLCV(
                symbol=ohlcv.symbol,
                timeframe=ohlcv.timeframe,
                candles=window_candles,
            )
            windows.append(window)

        logger.debug(
            "Created %d rolling windows of size %d for %s",
            len(windows),
            window_size,
            ohlcv.symbol,
        )

        return windows

    def align_multiple_series(
        self, series_list: List[OHLCV], method: str = "inner"
    ) -> List[OHLCV]:
        """
        Align multiple OHLCV series by timestamp

        Args:
            series_list: List of OHLCV objects to align
            method: Alignment method - 'inner' (intersection) or 'outer' (union)

        Returns:
            List of aligned OHLCV objects

        Note:
            All series must have the same timeframe
        """
        if not series_list:
            return []

        if len(series_list) == 1:
            return series_list

        # Check that all series have the same timeframe
        timeframe = series_list[0].timeframe
        if not all(s.timeframe == timeframe for s in series_list):
            raise ValueError("All series must have the same timeframe for alignment")

        # Convert all to DataFrames
        dfs = [s.to_dataframe() for s in series_list]

        # Get common or union timestamps based on method
        if method == "inner":
            # Get intersection of all timestamps
            common_timestamps = set(dfs[0].index)
            for df in dfs[1:]:
                common_timestamps &= set(df.index)
            common_timestamps = sorted(common_timestamps)
        elif method == "outer":
            # Get union of all timestamps
            all_timestamps = set()
            for df in dfs:
                all_timestamps |= set(df.index)
            common_timestamps = sorted(all_timestamps)
        else:
            raise ValueError(f"Unknown alignment method: {method}")

        # Reindex all DataFrames to common timestamps
        aligned_dfs = []
        for df in dfs:
            aligned = df.reindex(common_timestamps)
            if method == "outer":
                # Forward fill for outer join
                aligned = aligned.ffill()
            aligned_dfs.append(aligned.dropna())

        # Convert back to OHLCV objects
        result = []
        for i, df in enumerate(aligned_dfs):
            ohlcv = OHLCV.from_dataframe(
                df, symbol=series_list[i].symbol, timeframe=timeframe
            )
            result.append(ohlcv)

        logger.info(
            "Aligned %d series using %s method, resulting in %d common candles",
            len(series_list),
            method,
            len(result[0]),
        )

        return result

    def calculate_returns(self, ohlcv: OHLCV, period: int = 1) -> pd.Series:
        """
        Calculate returns for OHLCV data

        Args:
            ohlcv: Source OHLCV data
            period: Period for calculating returns (default: 1)

        Returns:
            Pandas Series with returns indexed by timestamp
        """
        df = ohlcv.to_dataframe()
        returns = df["close"].pct_change(periods=period)
        return returns

    def calculate_volatility(
        self, ohlcv: OHLCV, window: int = 20, method: str = "std"
    ) -> pd.Series:
        """
        Calculate volatility for OHLCV data

        Args:
            ohlcv: Source OHLCV data
            window: Rolling window size
            method: Method to use - 'std' (standard deviation) or 'atr' (ATR)

        Returns:
            Pandas Series with volatility indexed by timestamp
        """
        df = ohlcv.to_dataframe()

        if method == "std":
            returns = df["close"].pct_change()
            volatility = returns.rolling(window=window).std()
        elif method == "atr":
            # Average True Range
            high_low = df["high"] - df["low"]
            high_close = abs(df["high"] - df["close"].shift())
            low_close = abs(df["low"] - df["close"].shift())
            true_range = pd.concat(
                [high_low, high_close, low_close], axis=1
            ).max(axis=1)
            volatility = true_range.rolling(window=window).mean()
        else:
            raise ValueError(f"Unknown volatility method: {method}")

        return volatility

    def _get_pandas_frequency(self, timeframe: Timeframe) -> str:
        """Convert Timeframe to pandas frequency string"""
        freq_map = {
            "1m": "1min",
            "5m": "5min",
            "15m": "15min",
            "1h": "1h",
            "4h": "4h",
            "1d": "1D",
        }
        return freq_map[timeframe.value]

    def get_summary_statistics(self, ohlcv: OHLCV) -> dict:
        """
        Get summary statistics for OHLCV data

        Args:
            ohlcv: Source OHLCV data

        Returns:
            Dictionary with summary statistics
        """
        df = ohlcv.to_dataframe()

        stats = {
            "count": len(df),
            "start_date": df.index.min(),
            "end_date": df.index.max(),
            "open_first": df["open"].iloc[0],
            "close_last": df["close"].iloc[-1],
            "high_max": df["high"].max(),
            "low_min": df["low"].min(),
            "volume_total": df["volume"].sum(),
            "volume_mean": df["volume"].mean(),
            "price_change": df["close"].iloc[-1] - df["open"].iloc[0],
            "price_change_pct": (
                (df["close"].iloc[-1] - df["open"].iloc[0]) / df["open"].iloc[0] * 100
            ),
        }

        return stats
