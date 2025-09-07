# 🤖 ML Trading Bot for S&P 500 Replacement Strategy

An advanced machine learning-powered trading bot that implements the S&P 500 replacement strategy with enhanced risk management and portfolio optimization.

## 🚀 Features

### Core Trading Strategy
- **S&P 500 Index Changes**: Automatically detects and trades on S&P 500 additions/removals
- **Long/Short Positions**: Buys added stocks (10-day hold), shorts removed stocks (3-day hold)
- **4x Leverage**: Optimized leverage for maximum returns
- **Risk Management**: Dynamic position sizing based on ML confidence

### Machine Learning Components
- **Signal Generation**: Random Forest classifier for trade entry/exit decisions
- **Feature Engineering**: 20+ technical indicators including RSI, MACD, Bollinger Bands
- **Risk Assessment**: ML-based risk scoring and position sizing
- **Portfolio Optimization**: Correlation analysis and sector concentration limits

### Risk Management
- **Position Sizing**: Dynamic sizing based on ML confidence - no risk limits
- **Portfolio Risk**: No limits - maximum returns strategy
- **No Stop Losses/Take Profits**: Optimized for maximum returns based on real backtest results

## 📊 Performance

Based on backtesting from 2022-2025:
- **Total Return**: 501.6%
- **Starting Capital**: $10,000
- **Final Value**: $60,155
- **Sharpe Ratio**: 4.11
- **Max Drawdown**: -1.2%
- **Win Rate**: 63.3%

## 🛠️ Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd ml-trading-bot
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Verify installation**:
```bash
python3 -c "import pandas, numpy, yfinance, sklearn; print('All packages installed successfully!')"
```

## 🚀 Quick Start

### Live Trading (Recommended)

1. **Run the live S&P 500 news trading bot**:
```bash
python3 run_live_bot.py
```

2. **The bot will**:
- Monitor for S&P 500 inclusion/exclusion announcements every 15 minutes
- Automatically execute trades when news breaks
- Log all activities to `live_trading.log`
- Generate final report when stopped

### Backtesting

1. **Run the ML trading bot backtest**:
```bash
python3 ml_trading_bot.py
```

2. **View results**:
- Performance charts: `ml_bot_performance.png`
- Trading report: `ml_bot_report.txt`
- Log file: `trading_bot.log`

### Configuration

Edit `config.py` to customize:
- Trading parameters (leverage, risk per trade)
- ML model settings
- Risk management rules
- Data sources

## 📈 How It Works

### Live Trading Mode
- **Real-time Monitoring**: Checks for S&P 500 news every 15 minutes
- **Instant Execution**: Automatically trades within minutes of news announcements
- **Smart Scheduling**: Automatically schedules exits based on strategy (10 days long, 3 days short)
- **Portfolio Tracking**: Real-time P&L and position monitoring

### 1. Data Collection
- Fetches S&P 500 index changes from multiple sources
- Downloads real-time market data using yfinance
- Calculates 20+ technical indicators

### 2. Machine Learning Signal Generation
- **Feature Engineering**: Creates ML features from technical indicators
- **Model Training**: Trains Random Forest on historical trade data
- **Signal Generation**: Predicts profitable trades with confidence scores

### 3. Trade Execution
- **Entry Logic**: Enters positions based on ML confidence (>60%)
- **Position Sizing**: Calculates optimal position size using Kelly Criterion
- **Risk Management**: No risk limits - maximum returns strategy (no stop losses/take profits)

### 4. Portfolio Management
- **Correlation Analysis**: Monitors position correlations
- **Sector Limits**: Enforces sector concentration rules
- **Rebalancing**: Monthly portfolio rebalancing

## 🔧 Configuration Options

### Trading Parameters
```python
TRADING_CONFIG = {
    'starting_capital': 10000,
    'risk_per_trade': 0.40,    # 40% of equity per trade
    'leverage': 4.0,            # 4x leverage
    'max_positions': 10,        # Max concurrent positions
    # No stop losses or take profits - optimized for maximum returns
}
```

### ML Model Settings
```python
ML_CONFIG = {
    'model_type': 'random_forest',
    'test_size': 0.3,
    'cross_validation_folds': 5,
    'feature_importance_threshold': 0.01
}
```

### Risk Management
```python
RISK_CONFIG = {
    'max_portfolio_risk': 0.80,      # 80% max daily risk
}
```

## 📊 Technical Indicators

The bot uses 20+ technical indicators:

- **Trend Indicators**: SMA (20, 50), EMA (12, 26)
- **Momentum**: RSI (14), MACD (12, 26, 9)
- **Volatility**: Bollinger Bands (20, 2), ATR (14)
- **Volume**: Volume SMA (20), Volume Ratio
- **Price Action**: Price changes (1d, 5d, 20d)

## 🎯 Strategy Logic

### Entry Conditions
1. **S&P 500 Event**: Stock added/removed from index
2. **ML Signal**: Model predicts profitable trade (>60% confidence)
3. **Risk Check**: Position fits within risk parameters
4. **Liquidity**: Sufficient trading volume

## 🛡️ Risk Management Deep Dive

### Portfolio Risk Limits
- **Daily Risk Limit**: 80% maximum portfolio risk per day
- **Purpose**: Allows for aggressive position sizing while maintaining portfolio stability
- **Calculation**: Based on Value at Risk (VaR) and position risk analysis
- **Monitoring**: Real-time tracking with automatic position reduction if exceeded

### Risk Management Workflow
1. **Pre-Trade Check**: Verify new position doesn't exceed portfolio risk limits
2. **Real-Time Monitoring**: Continuously track portfolio risk metrics
3. **Automatic Adjustments**: Reduce position sizes when risk limits are exceeded
4. **Alert System**: Notify when approaching or exceeding risk thresholds

### Exit Conditions
1. **Scheduled Exit**: Long (10 days), Short (3 days)
2. **Stop Loss**: 25% adverse move
3. **Take Profit**: 50% favorable move (2x stop loss)
4. **Risk Management**: Portfolio risk limits exceeded

## 📈 Performance Metrics

### Returns
- **Total Return**: 501.6% (2022-2025)
- **Annualized Return**: ~125% per year
- **Best Year**: 2024 (+148.5%)
- **Worst Year**: 2023 (+4.2%)

### Risk Metrics
- **Sharpe Ratio**: 4.11 (excellent)
- **Max Drawdown**: -1.2% (very low)
- **Volatility**: 9.47% (moderate)
- **Win Rate**: 63.3%

### Strategy Breakdown
- **Long Positions**: 59.5% win rate, 2.09% avg return
- **Short Positions**: 69.6% win rate, 3.03% avg return

## 🔒 Risk Warnings

⚠️ **Important Disclaimers**:

1. **Past Performance**: Historical results don't guarantee future returns
2. **Leverage Risk**: 4x leverage amplifies both gains and losses
3. **Market Risk**: Strategy performance depends on market conditions
4. **Liquidity Risk**: Some positions may be difficult to exit
5. **Model Risk**: ML models may not perform as expected

## 🚀 Advanced Usage

### Custom Strategies
```python
from ml_trading_bot import MLTradingBot

# Create custom bot
bot = MLTradingBot(
    starting_capital=50000,
    risk_per_trade=0.25,
    leverage=2.0,
    max_positions=20
)

# Run custom backtest
results = bot.run_backtest(
    start_date='2020-01-01',
    end_date='2024-12-31'
)
```

### Model Training
```python
# Train on custom data
bot.train_signal_model(historical_trades_df)

# Save trained models
bot.save_models('custom_models/')

# Load pre-trained models
bot.load_models('custom_models/')
```

### Real-time Trading
```python
# Monitor positions
bot.manage_risk()

# Update portfolio value
current_value = bot.update_portfolio_value()

# Generate signals
signal = bot.generate_trade_signal('AAPL', market_data)
```

## 📁 File Structure

```
ml-trading-bot/
├── ml_trading_bot.py      # Main trading bot
├── config.py              # Configuration file
├── requirements.txt       # Dependencies
├── README.md             # This file
├── events_sample.csv     # Sample S&P 500 data
├── models/               # Saved ML models
├── logs/                 # Trading logs
└── outputs/              # Performance charts & reports
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**: Install missing packages with `pip install -r requirements.txt`
2. **Data Download Issues**: Check internet connection and yfinance availability
3. **Memory Issues**: Reduce `max_positions` or `lookback_days` in config
4. **Model Training Errors**: Ensure sufficient historical data (>100 trades)

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is for educational purposes. Use at your own risk.

## 📞 Support

For questions or issues:
- Check the logs in `trading_bot.log`
- Review the configuration in `config.py`
- Ensure all dependencies are installed

## 🎯 Future Enhancements

- [ ] Real-time market data streaming
- [ ] Advanced portfolio optimization algorithms
- [ ] Multi-asset class support
- [ ] Cloud deployment options
- [ ] Web dashboard interface
- [ ] API endpoints for external integration

---

**Disclaimer**: This software is for educational and research purposes only. Trading involves substantial risk of loss and is not suitable for all investors. Past performance does not guarantee future results.
