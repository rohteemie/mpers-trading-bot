"""
Example demonstrating the Core Data Management module

This example shows how to:
1. Fetch market data
2. Validate OHLCV data
3. Cache data for performance
4. Perform time series operations
5. Work with multiple timeframes
"""

import logging
from datetime import datetime, timedelta
from mpers_bot.data import (
    MarketDataFetcher,
    DataCache,
    DataValidator,
    TimeSeriesHandler,
    Timeframe,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main example function"""
    
    logger.info("=== Forex Trading Bot - Data Management Example ===\n")
    
    # 1. Initialize components
    logger.info("1. Initializing data management components...")
    fetcher = MarketDataFetcher()
    cache = DataCache(cache_dir="examples/cache")
    validator = DataValidator(strict_mode=False)
    ts_handler = TimeSeriesHandler()
    
    # 2. Fetch market data
    logger.info("\n2. Fetching market data...")
    symbol = "EURUSD"
    timeframe = Timeframe.M5
    
    # Check cache first
    cached_data = cache.get(symbol, timeframe)
    if cached_data:
        logger.info(f"Found cached data for {symbol} {timeframe.value}")
        ohlcv = cached_data
    else:
        logger.info(f"Fetching fresh data for {symbol} {timeframe.value}")
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=2)
        ohlcv = fetcher.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date
        )
        # Cache for future use
        cache.set(ohlcv)
    
    logger.info(f"Fetched {len(ohlcv)} candles")
    
    # 3. Validate data
    logger.info("\n3. Validating data...")
    is_valid = validator.validate_ohlcv(ohlcv)
    logger.info(f"Data validation result: {'PASSED' if is_valid else 'FAILED'}")
    
    # Check for data gaps
    gaps = validator.check_data_gaps(ohlcv)
    if gaps:
        logger.warning(f"Found {len(gaps)} data gaps")
    else:
        logger.info("No data gaps detected")
    
    # 4. Display latest candles
    logger.info("\n4. Latest candles:")
    latest_candles = ohlcv.get_latest(5)
    for i, candle in enumerate(latest_candles, 1):
        logger.info(
            f"  {i}. {candle.timestamp} - "
            f"O: {candle.open:.5f}, H: {candle.high:.5f}, "
            f"L: {candle.low:.5f}, C: {candle.close:.5f}, "
            f"V: {candle.volume:.0f} - "
            f"{'Bullish' if candle.is_bullish else 'Bearish'}"
        )
    
    # 5. Time series operations
    logger.info("\n5. Time series operations...")
    
    # Get summary statistics
    stats = ts_handler.get_summary_statistics(ohlcv)
    logger.info(f"Summary statistics:")
    logger.info(f"  Period: {stats['start_date']} to {stats['end_date']}")
    logger.info(f"  Price change: {stats['price_change']:.5f} ({stats['price_change_pct']:.2f}%)")
    logger.info(f"  High: {stats['high_max']:.5f}, Low: {stats['low_min']:.5f}")
    logger.info(f"  Average volume: {stats['volume_mean']:.0f}")
    
    # Calculate returns
    returns = ts_handler.calculate_returns(ohlcv)
    avg_return = returns.mean() * 100
    logger.info(f"  Average return: {avg_return:.4f}%")
    
    # Calculate volatility
    volatility = ts_handler.calculate_volatility(ohlcv, window=20, method='std')
    avg_volatility = volatility.mean() * 100
    logger.info(f"  Average volatility (20-period): {avg_volatility:.4f}%")
    
    # 6. Resample to higher timeframe
    logger.info("\n6. Resampling data...")
    if len(ohlcv) >= 12:  # Need at least 12 M5 candles for 1 H1 candle
        logger.info(f"Resampling from {timeframe.value} to H1...")
        resampled = ts_handler.resample(ohlcv, Timeframe.H1)
        logger.info(f"Resampled to {len(resampled)} H1 candles")
        
        if len(resampled) > 0:
            latest_h1 = resampled.get_latest(1)[0]
            logger.info(
                f"Latest H1 candle: {latest_h1.timestamp} - "
                f"O: {latest_h1.open:.5f}, H: {latest_h1.high:.5f}, "
                f"L: {latest_h1.low:.5f}, C: {latest_h1.close:.5f}"
            )
    else:
        logger.info("Not enough data for resampling")
    
    # 7. Work with multiple timeframes
    logger.info("\n7. Working with multiple timeframes...")
    timeframes = [Timeframe.M1, Timeframe.M5, Timeframe.M15, Timeframe.H1]
    logger.info("Available timeframes:")
    for tf in timeframes:
        logger.info(f"  {tf.value} ({tf.minutes} minutes)")
    
    # 8. Cache statistics
    logger.info("\n8. Cache statistics:")
    cache_stats = cache.get_cache_stats()
    logger.info(f"  Memory cache items: {cache_stats['memory_cache_items']}")
    logger.info(f"  File cache items: {cache_stats['file_cache_items']}")
    logger.info(f"  Cache directory: {cache_stats['cache_dir']}")
    
    logger.info("\n=== Example completed successfully! ===")


if __name__ == "__main__":
    main()
