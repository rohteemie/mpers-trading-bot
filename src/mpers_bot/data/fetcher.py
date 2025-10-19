"""Market data fetcher module"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from mpers_bot.data.structures import OHLCV, Candle, Timeframe


logger = logging.getLogger(__name__)


class DataFetcherError(Exception):
    """Base exception for data fetcher errors"""

    pass


class DataFetcherConnectionError(DataFetcherError):
    """Exception for connection errors"""

    pass


class DataFetcherRateLimitError(DataFetcherError):
    """Exception for rate limit errors"""

    pass


class DataFetcherInterface(ABC):
    """Abstract interface for market data fetchers"""

    @abstractmethod
    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: Timeframe,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> OHLCV:
        """Fetch OHLCV data for a symbol and timeframe"""
        pass

    @abstractmethod
    def fetch_latest_candle(self, symbol: str, timeframe: Timeframe) -> Candle:
        """Fetch the latest candle for a symbol and timeframe"""
        pass

    @abstractmethod
    def get_available_symbols(self) -> list:
        """Get list of available trading symbols"""
        pass


class MarketDataFetcher(DataFetcherInterface):
    """
    Market data fetcher implementation

    This is a mock implementation that generates sample data.
    In production, this would connect to real data sources like:
    - MetaTrader 5
    - Binance API
    - Interactive Brokers
    - Alpha Vantage
    - Yahoo Finance
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize market data fetcher

        Args:
            config: Configuration dictionary with data source settings
        """
        self.config = config or {}
        self.available_symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]
        logger.info("MarketDataFetcher initialized")

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: Timeframe,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> OHLCV:
        """
        Fetch OHLCV data for a symbol and timeframe

        Args:
            symbol: Trading symbol (e.g., 'EURUSD')
            timeframe: Timeframe for the data
            start_date: Start date for data fetch
            end_date: End date for data fetch
            limit: Maximum number of candles to fetch

        Returns:
            OHLCV object with fetched data

        Raises:
            DataFetcherError: If fetching fails
        """
        try:
            if symbol not in self.available_symbols:
                raise DataFetcherError(f"Symbol {symbol} not available")

            # Set default dates if not provided
            if end_date is None:
                end_date = datetime.now()
            if start_date is None:
                if limit:
                    # Calculate start date based on limit and timeframe
                    minutes_back = limit * timeframe.minutes
                    start_date = end_date - timedelta(minutes=minutes_back)
                else:
                    # Default to 100 candles
                    start_date = end_date - timedelta(minutes=100 * timeframe.minutes)

            logger.info(
                f"Fetching OHLCV data for {symbol} {timeframe.value} "
                f"from {start_date} to {end_date}"
            )

            # Generate sample data
            candles = self._generate_sample_data(
                symbol, timeframe, start_date, end_date
            )

            ohlcv = OHLCV(symbol=symbol, timeframe=timeframe, candles=candles)

            logger.info(f"Fetched {len(ohlcv)} candles for {symbol}")
            return ohlcv

        except Exception as e:
            logger.error(f"Error fetching OHLCV data: {e}")
            raise DataFetcherError(f"Failed to fetch OHLCV data: {e}") from e

    def fetch_latest_candle(self, symbol: str, timeframe: Timeframe) -> Candle:
        """
        Fetch the latest candle for a symbol and timeframe

        Args:
            symbol: Trading symbol
            timeframe: Timeframe for the candle

        Returns:
            Latest Candle object

        Raises:
            DataFetcherError: If fetching fails
        """
        try:
            if symbol not in self.available_symbols:
                raise DataFetcherError(f"Symbol {symbol} not available")

            logger.info(f"Fetching latest candle for {symbol} {timeframe.value}")

            # Get the latest candle timestamp
            now = datetime.now()
            # Round down to nearest timeframe interval
            minutes_offset = now.minute % timeframe.minutes
            candle_time = now - timedelta(
                minutes=minutes_offset, seconds=now.second, microseconds=now.microsecond
            )

            # Generate a sample candle
            base_price = self._get_base_price(symbol)
            candle = self._generate_candle(candle_time, base_price, timeframe)

            logger.info(f"Fetched latest candle for {symbol} at {candle_time}")
            return candle

        except Exception as e:
            logger.error(f"Error fetching latest candle: {e}")
            raise DataFetcherError(f"Failed to fetch latest candle: {e}") from e

    def get_available_symbols(self) -> list:
        """
        Get list of available trading symbols

        Returns:
            List of available symbol strings
        """
        return self.available_symbols.copy()

    def _generate_sample_data(
        self, symbol: str, timeframe: Timeframe, start_date: datetime, end_date: datetime
    ) -> list:
        """Generate sample OHLCV data"""
        candles = []
        base_price = self._get_base_price(symbol)
        current_price = base_price

        # Generate candles
        current_time = start_date
        while current_time <= end_date:
            candle = self._generate_candle(current_time, current_price, timeframe)
            candles.append(candle)
            current_price = candle.close
            current_time += timedelta(minutes=timeframe.minutes)

        return candles

    def _generate_candle(
        self, timestamp: datetime, base_price: float, timeframe: Timeframe
    ) -> Candle:
        """Generate a single sample candle"""
        import random

        # Generate realistic price movement
        volatility = base_price * 0.001  # 0.1% volatility
        open_price = base_price
        close_price = base_price + random.uniform(-volatility, volatility)

        high = max(open_price, close_price) + random.uniform(0, volatility / 2)
        low = min(open_price, close_price) - random.uniform(0, volatility / 2)
        volume = random.uniform(1000, 10000)

        return Candle(
            timestamp=timestamp,
            open=open_price,
            high=high,
            low=low,
            close=close_price,
            volume=volume,
            timeframe=timeframe,
        )

    def _get_base_price(self, symbol: str) -> float:
        """Get base price for a symbol"""
        base_prices = {
            "EURUSD": 1.0850,
            "GBPUSD": 1.2650,
            "USDJPY": 148.50,
            "XAUUSD": 2050.00,
        }
        return base_prices.get(symbol, 1.0000)
