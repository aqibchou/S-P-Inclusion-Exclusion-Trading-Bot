"""
Configuration file for ML Trading Bot
"""

# Trading Strategy Configuration
TRADING_CONFIG = {
    'starting_capital': 10000,
    'risk_per_trade': 0.40,  # 40% of current equity per trade
    'leverage': 4.0,          # 4x leverage
    'max_positions': 10,      # Maximum concurrent positions
    # No stop losses or take profits - optimized for maximum returns
    # Based on real backtest results showing no risk management = best performance
    'min_confidence': 0.6,    # Minimum ML confidence for trade execution
}

# S&P 500 Strategy Parameters
SP500_CONFIG = {
    'long_hold_days': 10,     # Hold added stocks for 10 days
    'short_hold_days': 3,     # Hold short positions for 3 days
    'entry_delay': 1,         # Enter on next trading day after announcement
    'slippage_bps': 5,        # 5 basis points slippage
    'commission_bps': 1,      # 1 basis point commission
}

# Machine Learning Configuration
ML_CONFIG = {
    'model_type': 'random_forest',  # 'random_forest' or 'gradient_boosting'
    'random_forest_params': {
        'n_estimators': 100,
        'max_depth': 10,
        'random_state': 42,
        'class_weight': 'balanced'
    },
    'gradient_boosting_params': {
        'n_estimators': 100,
        'learning_rate': 0.1,
        'max_depth': 6,
        'random_state': 42
    },
    'test_size': 0.3,
    'cross_validation_folds': 5,
    'feature_importance_threshold': 0.01
}

# Technical Indicators Configuration
TECHNICAL_CONFIG = {
    'sma_periods': [20, 50],
    'ema_periods': [12, 26],
    'rsi_period': 14,
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,
    'bollinger_period': 20,
    'bollinger_std': 2,
    'atr_period': 14,
    'volume_sma_period': 20
}

# Risk Management Configuration
RISK_CONFIG = {
    'max_portfolio_risk': 1.0,       # No portfolio risk limits - maximum returns
    'volatility_threshold': 1.0,     # No volatility limits
    'liquidity_threshold': 0,        # No liquidity requirements
}

# Data Configuration
DATA_CONFIG = {
    'lookback_days': 60,
    'update_frequency': '1d',        # '1d', '1h', '5m'
    'data_sources': ['yfinance'],    # 'yfinance', 'alpha_vantage', 'polygon'
    'cache_duration': 3600,          # Cache data for 1 hour
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'file_handler': True,
    'console_handler': True,
    'log_file': 'trading_bot.log',
    'max_file_size': 10485760,       # 10MB
    'backup_count': 5
}

# Performance Tracking Configuration
PERFORMANCE_CONFIG = {
    'metrics': ['sharpe_ratio', 'sortino_ratio', 'max_drawdown', 'calmar_ratio'],
    'benchmark': 'SPY',              # Benchmark for comparison
    'risk_free_rate': 0.02,          # 2% risk-free rate
    'rebalance_frequency': 'monthly'
}

# API Configuration (for external data sources)
API_CONFIG = {
    'alpha_vantage_key': '',         # Alpha Vantage API key
    'polygon_key': '',               # Polygon API key
    'finnhub_key': '',               # Finnhub API key
    'rate_limit_delay': 0.1,         # Delay between API calls
}

# Notification Configuration
NOTIFICATION_CONFIG = {
    'email_notifications': False,
    'email_smtp_server': 'smtp.gmail.com',
    'email_port': 587,
    'email_username': '',
    'email_password': '',
    'telegram_notifications': False,
    'telegram_bot_token': '',
    'telegram_chat_id': '',
}

# Backtesting Configuration
BACKTEST_CONFIG = {
    'start_date': '2022-10-01',
    'end_date': '2025-08-30',
    'initial_capital': 10000,
    'transaction_costs': True,
    'slippage_model': 'fixed',       # 'fixed', 'proportional', 'adaptive'
    'rebalance_costs': True,
    'tax_consideration': False
}
