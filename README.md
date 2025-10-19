# Mpers Trading Bot 🤖📈

An intelligent automated trading bot designed to execute trades based on advanced technical analysis strategies. The bot continuously monitors financial markets and automatically enters and exits trades when specific chart patterns and trading rules are satisfied.

## 🎯 Overview

Mpers Trading Bot is a sophisticated algorithmic trading system that leverages multiple technical analysis methodologies to identify high-probability trading opportunities. The bot operates autonomously, scanning markets 24/7 and executing trades based on predefined strategies while managing risk automatically.

### Key Capabilities

- **Automated Trading**: Executes trades without manual intervention when conditions are met
- **Multi-Strategy Analysis**: Combines multiple technical indicators for robust decision-making
- **Risk Management**: Automatic position sizing and stop-loss/take-profit management
- **Real-time Monitoring**: Continuous market surveillance and position tracking
- **Quick Exit Mechanism**: Automatically closes positions when strategy conditions are no longer valid
- **Multi-Broker Support**: Compatible with most popular trading platforms

## ✨ Features

### Technical Analysis Strategies

The bot implements the following technical analysis methodologies:

#### 📊 Trendline Analysis

- Identifies ascending and descending trendlines
- Detects trendline breakouts and bounces
- Confirms trend direction before entry

#### 🎯 Supply and Demand Zones

- Identifies key supply (resistance) zones
- Locates demand (support) zones
- Monitors price reactions at these zones
- Enters trades on zone rejections or breakouts

#### 📍 Support and Resistance Levels

- Calculates horizontal support and resistance levels
- Tracks price interactions with key levels
- Identifies level breaks and retests

#### 🌀 Fibonacci Retracements

- Calculates Fibonacci levels (23.6%, 38.2%, 50%, 61.8%, 78.6%)
- Identifies potential reversal points
- Combines with other indicators for confirmation

### Trading Features

- **Entry Signal Generation**: Multiple confirmation signals before trade entry
- **Position Management**: Automatic lot size calculation based on account balance and risk
- **Stop Loss & Take Profit**: Dynamic SL/TP placement based on market structure
- **Trade Monitoring**: Continuous evaluation of open positions
- **Quick Exit Strategy**: Closes trades immediately when conditions reverse
- **Trade Logging**: Comprehensive trade history and performance tracking

## 🏗️ Architecture

```bash
mpers-trading-bot/
├── src/
│   ├── core/
│   │   ├── bot.py              # Main bot orchestrator
│   │   ├── strategy_manager.py # Strategy execution engine
│   │   └── risk_manager.py     # Risk and position management
│   ├── strategies/
│   │   ├── trendline.py        # Trendline analysis
│   │   ├── supply_demand.py    # Supply and demand zones
│   │   ├── support_resistance.py # S&R level detection
│   │   └── fibonacci.py        # Fibonacci retracement calculations
│   ├── brokers/
│   │   ├── base_broker.py      # Base broker interface
│   │   ├── metatrader.py       # MetaTrader 4/5 integration
│   │   ├── interactive_brokers.py # Interactive Brokers
│   │   └── binance.py          # Binance (crypto)
│   ├── indicators/
│   │   ├── moving_averages.py  # MA calculations
│   │   ├── rsi.py              # RSI indicator
│   │   └── macd.py             # MACD indicator
│   ├── utils/
│   │   ├── data_manager.py     # Market data fetching
│   │   ├── logger.py           # Logging system
│   │   └── notifications.py    # Alert system (email, SMS, Telegram)
│   └── config/
│       ├── config.yaml         # Configuration file
│       └── strategies.yaml     # Strategy parameters
├── tests/
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── backtesting/            # Backtesting framework
├── docs/
│   ├── setup.md               # Setup guide
│   ├── strategies.md          # Strategy documentation
│   └── api.md                 # API documentation
├── requirements.txt
├── README.md
└── ROADMAP.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- Trading account with a supported broker
- API credentials from your broker
- Sufficient capital for trading (recommended minimum varies by broker)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/rohteemie/mpers-trading-bot.git
   cd mpers-trading-bot
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the bot**

   ```bash
   cp config/config.example.yaml config/config.yaml
   # Edit config.yaml with your settings
   ```

### Configuration

Edit `config/config.yaml` to customize your bot:

```yaml
# Trading Configuration
trading:
  broker: "metatrader5"  # metatrader4, metatrader5, interactive_brokers, binance
  account_id: "your_account_id"
  api_key: "your_api_key"
  api_secret: "your_api_secret"

# Risk Management
risk:
  max_risk_per_trade: 1.0  # Maximum % of account per trade
  max_daily_loss: 3.0      # Maximum % daily loss
  max_open_trades: 5       # Maximum simultaneous positions

# Strategy Parameters
strategies:
  enabled:
    - trendline
    - supply_demand
    - support_resistance
    - fibonacci

  trendline:
    min_touches: 3         # Minimum touches to validate trendline
    breakout_threshold: 0.2 # % move for breakout confirmation

  supply_demand:
    zone_strength: "medium" # weak, medium, strong
    lookback_periods: 100   # Candles to analyze

  support_resistance:
    touch_tolerance: 0.1    # % tolerance for level touch
    min_bounces: 2          # Minimum bounces to confirm level

  fibonacci:
    key_levels: [0.236, 0.382, 0.5, 0.618, 0.786]
    confluence_range: 0.5   # % range for level confluence

# Markets to Trade
markets:
  - symbol: "EURUSD"
    timeframe: "H1"
  - symbol: "GBPUSD"
    timeframe: "H1"
  - symbol: "XAUUSD"
    timeframe: "H4"

# Notifications
notifications:
  telegram:
    enabled: true
    bot_token: "your_telegram_bot_token"
    chat_id: "your_chat_id"
  email:
    enabled: false
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
```

### Usage

#### Running the Bot

```bash
# Start the trading bot
python -m src.main

# Run in dry-run mode (paper trading)
python -m src.main --dry-run

# Run with specific strategy
python -m src.main --strategy trendline

# Backtest a strategy
python -m src.main --backtest --start-date 2023-01-01 --end-date 2023-12-31
```

#### Monitoring

```bash
# View real-time logs
tail -f logs/trading.log

# Check bot status
python -m src.cli status

# View open positions
python -m src.cli positions

# View trade history
python -m src.cli history --days 7
```

## 🔌 Supported Brokers

The bot is designed to work with multiple broker platforms:

### Currently Planned

- **MetaTrader 4** - Full support planned
- **MetaTrader 5** - Full support planned
- **Interactive Brokers** - Via TWS API
- **Binance** - For cryptocurrency trading
- **Alpaca** - Commission-free stock trading
- **OANDA** - Forex trading via REST API

### Broker Integration Status

| Broker | Status | Priority | Notes |
|--------|--------|----------|-------|
| MetaTrader 5 | 🔄 Planned | High | Most popular forex platform |
| Binance | 🔄 Planned | High | Crypto trading |
| Interactive Brokers | 🔄 Planned | Medium | Stocks, options, futures |
| OANDA | 🔄 Planned | Medium | Forex via REST API |
| MetaTrader 4 | 🔄 Planned | Low | Legacy platform |
| Alpaca | 🔄 Planned | Low | Commission-free stocks |

*Legend: ✅ Completed | 🔄 Planned | ⏸️ On Hold*

## 📊 Strategy Details

### How the Bot Makes Decisions

1. **Market Scanning**: Continuously monitors configured markets
2. **Signal Generation**: Each strategy analyzes price action independently
3. **Confluence Check**: Looks for agreement between multiple strategies
4. **Risk Assessment**: Calculates position size and stop loss
5. **Trade Execution**: Places order with broker
6. **Active Monitoring**: Tracks position and market conditions
7. **Exit Management**: Closes trade when conditions change or targets hit

### Entry Conditions Example

A typical trade entry requires:

- Valid trendline in place (direction confirmed)
- Price at key Fibonacci level (38.2% or 61.8%)
- Support/Resistance level nearby for confirmation
- Supply/Demand zone alignment
- Risk-reward ratio minimum 1:2

### Exit Conditions

Trades are closed when:

- Take profit target is reached
- Stop loss is hit
- Strategy conditions reverse (quick exit)
- Maximum time in trade exceeded
- End of trading session

## ⚠️ Risk Disclaimer

**IMPORTANT**: Trading financial instruments carries significant risk. You can lose more than your initial investment. This bot is provided for educational purposes and should not be considered financial advice.

- Always test strategies in a demo account first
- Never risk money you cannot afford to lose
- Past performance does not guarantee future results
- Use proper risk management at all times
- Understand the markets you are trading

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run unit tests only
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run with coverage
pytest --cov=src tests/

# Backtest a strategy
python -m src.backtest --config config/backtest.yaml
```

## 📚 Documentation

- [Setup Guide](docs/setup.md) - Detailed installation and configuration
- [Strategy Documentation](docs/strategies.md) - In-depth strategy explanations
- [API Reference](docs/api.md) - Code API documentation
- [Contributing Guide](CONTRIBUTING.md) - How to contribute
- [Roadmap](ROADMAP.md) - Project roadmap and future plans

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and development process.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Technical analysis concepts from classical trading theory
- Open source trading libraries and communities
- Contributors and testers who help improve the bot

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/rohteemie/mpers-trading-bot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/rohteemie/mpers-trading-bot/discussions)
- **Email**: <rotimijournal@outlook.com>

## 📈 Project Status

This project is currently in **active development**. See [ROADMAP.md](ROADMAP.md) for detailed development plans and timelines.

---

**⚡ Built with passion by the Mpers Trading Bot team**

*Remember: Trade responsibly and never risk more than you can afford to lose.*
