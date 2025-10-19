"""Data structures for OHLCV market data"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List
import pandas as pd


class Timeframe(Enum):
    """Supported timeframes for market data"""

    M1 = "1m"  # 1 minute
    M5 = "5m"  # 5 minutes
    M15 = "15m"  # 15 minutes
    H1 = "1h"  # 1 hour
    H4 = "4h"  # 4 hours
    D1 = "1d"  # 1 day

    @property
    def minutes(self) -> int:
        """Get timeframe duration in minutes"""
        timeframe_map = {
            "1m": 1,
            "5m": 5,
            "15m": 15,
            "1h": 60,
            "4h": 240,
            "1d": 1440,
        }
        return timeframe_map[self.value]

    @classmethod
    def from_string(cls, timeframe_str: str) -> "Timeframe":
        """Create Timeframe from string representation"""
        for tf in cls:
            if tf.value == timeframe_str.lower():
                return tf
        raise ValueError(f"Invalid timeframe: {timeframe_str}")


@dataclass
class Candle:
    """Single OHLCV candle data"""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    timeframe: Timeframe

    def __post_init__(self):
        """Validate candle data after initialization"""
        if self.high < max(self.open, self.close):
            raise ValueError("High price must be >= max(open, close)")
        if self.low > min(self.open, self.close):
            raise ValueError("Low price must be <= min(open, close)")
        if self.volume < 0:
            raise ValueError("Volume cannot be negative")

    @property
    def is_bullish(self) -> bool:
        """Check if candle is bullish (close > open)"""
        return self.close > self.open

    @property
    def is_bearish(self) -> bool:
        """Check if candle is bearish (close < open)"""
        return self.close < self.open

    @property
    def body_size(self) -> float:
        """Get the size of candle body"""
        return abs(self.close - self.open)

    @property
    def upper_wick(self) -> float:
        """Get size of upper wick"""
        return self.high - max(self.open, self.close)

    @property
    def lower_wick(self) -> float:
        """Get size of lower wick"""
        return min(self.open, self.close) - self.low

    @property
    def range(self) -> float:
        """Get candle range (high - low)"""
        return self.high - self.low

    def to_dict(self) -> dict:
        """Convert candle to dictionary"""
        return {
            "timestamp": self.timestamp,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "timeframe": self.timeframe.value,
        }


@dataclass
class OHLCV:
    """OHLCV data structure for multiple candles"""

    symbol: str
    timeframe: Timeframe
    candles: List[Candle] = field(default_factory=list)

    def __post_init__(self):
        """Sort candles by timestamp after initialization"""
        self.candles.sort(key=lambda c: c.timestamp)

    def add_candle(self, candle: Candle):
        """Add a new candle to the data structure"""
        if candle.timeframe != self.timeframe:
            raise ValueError(
                f"Candle timeframe {candle.timeframe} does not match OHLCV "
                f"timeframe {self.timeframe}"
            )
        self.candles.append(candle)
        self.candles.sort(key=lambda c: c.timestamp)

    def get_latest(self, n: int = 1) -> List[Candle]:
        """Get the latest n candles"""
        return self.candles[-n:] if n <= len(self.candles) else self.candles

    def get_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[Candle]:
        """Get candles within a date range"""
        return [
            candle
            for candle in self.candles
            if start_date <= candle.timestamp <= end_date
        ]

    def to_dataframe(self) -> pd.DataFrame:
        """Convert OHLCV data to pandas DataFrame"""
        if not self.candles:
            return pd.DataFrame(
                columns=["timestamp", "open", "high", "low", "close", "volume"]
            )

        data = {
            "timestamp": [c.timestamp for c in self.candles],
            "open": [c.open for c in self.candles],
            "high": [c.high for c in self.candles],
            "low": [c.low for c in self.candles],
            "close": [c.close for c in self.candles],
            "volume": [c.volume for c in self.candles],
        }
        df = pd.DataFrame(data)
        df.set_index("timestamp", inplace=True)
        return df

    @classmethod
    def from_dataframe(
        cls, df: pd.DataFrame, symbol: str, timeframe: Timeframe
    ) -> "OHLCV":
        """Create OHLCV from pandas DataFrame"""
        candles = []
        df_reset = df.reset_index()

        for _, row in df_reset.iterrows():
            candle = Candle(
                timestamp=row["timestamp"],
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=float(row["volume"]),
                timeframe=timeframe,
            )
            candles.append(candle)

        return cls(symbol=symbol, timeframe=timeframe, candles=candles)

    def __len__(self) -> int:
        """Get number of candles"""
        return len(self.candles)

    def __getitem__(self, index: int) -> Candle:
        """Get candle by index"""
        return self.candles[index]
