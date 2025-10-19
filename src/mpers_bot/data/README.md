# Data Management Module

Core data management module for the Mpers Trading Bot, implementing comprehensive OHLCV data handling, validation, caching, and time series operations.

## Features

### ✨ Core Components

1. **OHLCV Data Structures** (`structures.py`)
   - `Timeframe` enum with support for M1, M5, M15, H1, H4, D1
   - `Candle` dataclass with validation and helper properties
   - `OHLCV` dataclass for managing collections of candles
   - Automatic sorting and data integrity checks
   - Pandas DataFrame conversion support

2. **Market Data Fetcher** (`fetcher.py`)
   - Abstract interface for data source integration
   - Mock implementation for testing and development
   - Support for historical data fetching with date ranges
   - Latest candle fetching
   - Error handling and logging
   - Easily extensible for real data sources (MT5, Binance, etc.)

3. **Data Validation** (`validator.py`)
   - Comprehensive candle validation (price relationships, NaN checks)
   - OHLCV data validation (duplicate timestamps, gaps)
   - DataFrame validation
   - Strict and non-strict modes
   - Price range validation
   - Timeframe consistency checks

4. **Data Caching** (`cache.py`)
   - Two-tier caching system (memory + file)
   - LRU eviction for memory cache
   - Configurable TTL per timeframe
   - Cache invalidation and clearing
   - Statistics and monitoring

5. **Time Series Handler** (`timeseries.py`)
   - Timeframe resampling (M5 → H1, etc.)
   - Forward fill for missing data
   - Time-based slicing
   - Rolling window operations
   - Multiple series alignment
   - Returns and volatility calculations
   - Summary statistics

## Installation

The data module is part of the mpers-trading-bot package:

```bash
pip install -e .
```

## Quick Start

```python
from mpers_bot.data import (
    MarketDataFetcher,
    DataCache,
    DataValidator,
    TimeSeriesHandler,
    Timeframe,
)
from datetime import datetime, timedelta

# Initialize components
fetcher = MarketDataFetcher()
cache = DataCache()
validator = DataValidator()
ts_handler = TimeSeriesHandler()

# Fetch data
ohlcv = fetcher.fetch_ohlcv(
    symbol="EURUSD",
    timeframe=Timeframe.M5,
    limit=100
)

# Validate data
if validator.validate_ohlcv(ohlcv):
    print(f"✓ Data validation passed")

# Cache for future use
cache.set(ohlcv)

# Get latest candles
latest = ohlcv.get_latest(5)
for candle in latest:
    print(f"{candle.timestamp}: {candle.close}")

# Resample to higher timeframe
h1_data = ts_handler.resample(ohlcv, Timeframe.H1)
print(f"Resampled to {len(h1_data)} H1 candles")
```

## Usage Examples

### Working with Candles

```python
from mpers_bot.data import Candle, Timeframe
from datetime import datetime

# Create a candle
candle = Candle(
    timestamp=datetime(2024, 1, 1, 12, 0),
    open=1.0850,
    high=1.0875,
    low=1.0840,
    close=1.0865,
    volume=1000.0,
    timeframe=Timeframe.M5
)

# Access properties
print(f"Bullish: {candle.is_bullish}")
print(f"Body size: {candle.body_size}")
print(f"Upper wick: {candle.upper_wick}")
print(f"Lower wick: {candle.lower_wick}")
print(f"Range: {candle.range}")
```

### Data Fetching with Caching

```python
from mpers_bot.data import MarketDataFetcher, DataCache, Timeframe

fetcher = MarketDataFetcher()
cache = DataCache(cache_dir="./data/cache")

symbol = "EURUSD"
timeframe = Timeframe.H1

# Check cache first
cached = cache.get(symbol, timeframe)
if cached:
    ohlcv = cached
else:
    # Fetch fresh data
    ohlcv = fetcher.fetch_ohlcv(symbol, timeframe, limit=100)
    cache.set(ohlcv)
```

### Data Validation

```python
from mpers_bot.data import DataValidator

# Non-strict mode (logs warnings)
validator = DataValidator(strict_mode=False)

if validator.validate_ohlcv(ohlcv):
    print("Data is valid")

# Check for gaps
gaps = validator.check_data_gaps(ohlcv, max_gap_multiple=2)
if gaps:
    print(f"Found {len(gaps)} data gaps")

# Validate price ranges
for candle in ohlcv.candles:
    validator.validate_price_range(candle, min_price=0.1, max_price=10000)
```

### Time Series Operations

```python
from mpers_bot.data import TimeSeriesHandler

handler = TimeSeriesHandler()

# Resample to higher timeframe
h1_data = handler.resample(ohlcv, Timeframe.H1)

# Calculate returns
returns = handler.calculate_returns(ohlcv, period=1)
print(f"Average return: {returns.mean():.4f}%")

# Calculate volatility
volatility = handler.calculate_volatility(ohlcv, window=20, method='std')

# Get summary statistics
stats = handler.get_summary_statistics(ohlcv)
print(f"Price change: {stats['price_change_pct']:.2f}%")

# Get rolling windows
windows = handler.get_rolling_window(ohlcv, window_size=20, step=5)
```

### Working with Multiple Timeframes

```python
from mpers_bot.data import Timeframe

# All supported timeframes
timeframes = [
    Timeframe.M1,   # 1 minute
    Timeframe.M5,   # 5 minutes
    Timeframe.M15,  # 15 minutes
    Timeframe.H1,   # 1 hour
    Timeframe.H4,   # 4 hours
    Timeframe.D1,   # 1 day
]

# Get timeframe duration
print(f"{Timeframe.H1.value} = {Timeframe.H1.minutes} minutes")

# Create from string
tf = Timeframe.from_string("5m")
```

## Architecture

### Data Flow

```
MarketDataFetcher → OHLCV → DataValidator → DataCache
                      ↓
              TimeSeriesHandler
```

### Class Hierarchy

```
DataFetcherInterface (ABC)
    └── MarketDataFetcher

OHLCV
    └── List[Candle]
         └── Timeframe

DataCache
    ├── Memory Cache (LRU)
    └── File Cache (Pickle)

TimeSeriesHandler
    └── Pandas operations
```

## Testing

Run the comprehensive test suite:

```bash
# Run all data module tests
pytest tests/data/ -v

# Run specific test file
pytest tests/data/test_structures.py -v

# Run with coverage
pytest tests/data/ --cov=mpers_bot.data --cov-report=html
```

Test coverage: **93%**

## Performance

- **Memory cache**: O(1) lookup with LRU eviction
- **File cache**: Persistent storage with TTL-based invalidation
- **Data validation**: O(n) where n is number of candles
- **Resampling**: Efficient pandas-based aggregation
- **Typical fetch time**: < 100ms for 1000 candles (mock data)

## Extending the Module

### Adding New Data Sources

Implement the `DataFetcherInterface`:

```python
from mpers_bot.data.fetcher import DataFetcherInterface
from mpers_bot.data import OHLCV, Candle, Timeframe

class MyCustomFetcher(DataFetcherInterface):
    def fetch_ohlcv(self, symbol, timeframe, start_date=None,
                    end_date=None, limit=None) -> OHLCV:
        # Your implementation here
        pass

    def fetch_latest_candle(self, symbol, timeframe) -> Candle:
        # Your implementation here
        pass

    def get_available_symbols(self) -> list:
        # Your implementation here
        pass
```

### Custom Validators

Extend `DataValidator` for custom validation rules:

```python
from mpers_bot.data import DataValidator

class CustomValidator(DataValidator):
    def validate_custom_rule(self, ohlcv):
        # Your custom validation logic
        pass
```

## Configuration

### Cache Configuration

```python
from mpers_bot.data import DataCache

cache = DataCache(
    cache_dir="./data/cache",
    ttl_minutes={
        "1m": 5,
        "5m": 10,
        "15m": 30,
        "1h": 120,
        "4h": 480,
        "1d": 1440,
    },
    max_memory_items=100
)
```

### Validator Configuration

```python
from mpers_bot.data import DataValidator

# Strict mode raises exceptions
validator = DataValidator(strict_mode=True)

# Non-strict mode logs warnings
validator = DataValidator(strict_mode=False)
```

## API Reference

See the module docstrings for complete API documentation:

```python
# View documentation
import mpers_bot.data
help(mpers_bot.data.OHLCV)
help(mpers_bot.data.MarketDataFetcher)
help(mpers_bot.data.DataValidator)
help(mpers_bot.data.DataCache)
help(mpers_bot.data.TimeSeriesHandler)
```

## Examples

Complete working examples are available in the `examples/` directory:

- `data_management_example.py` - Comprehensive data module demo

Run the example:

```bash
python examples/data_management_example.py
```

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure the package is installed: `pip install -e .`
2. **Cache issues**: Clear cache with `cache.clear()` or delete cache directory
3. **Validation errors**: Check data for NaN values and invalid price relationships
4. **Resampling errors**: Ensure source timeframe < target timeframe

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- Real data source integrations (MT5, Binance, Interactive Brokers)
- Database backend for large datasets
- Asynchronous data fetching
- Data compression for cache
- WebSocket support for real-time data
- Advanced gap filling algorithms

## Contributing

Contributions are welcome! Please:

1. Add tests for new features
2. Maintain code coverage > 90%
3. Follow the existing code style
4. Update documentation

## License

MIT License - see LICENSE file for details
