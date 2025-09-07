#!/usr/bin/env python3
"""
IBKR Trading Configuration
Settings for Interactive Brokers integration
"""

import os
from typing import Dict

def get_ibkr_config() -> Dict:
    """Get IBKR trading configuration"""
    
    # Default configuration
    config = {
        # Connection settings
        'host': '127.0.0.1',  # Localhost for TWS/Gateway
        'port': 7497,          # 7497 for TWS, 4001 for Gateway (paper trading)
        'client_id': 1,        # Unique client ID
        
        # Trading parameters
        'max_position_size': 10000,    # Maximum $ per position
        'stop_loss_pct': 0.05,         # 5% stop loss
        'take_profit_pct': 0.15,       # 15% take profit
        'max_positions': 10,            # Maximum concurrent positions
        
        # Risk management
        'max_daily_loss': 5000,        # Maximum daily loss
        'max_portfolio_risk': 0.20,    # Maximum portfolio risk (20%)
        'position_sizing_method': 'kelly',  # 'fixed', 'kelly', 'volatility'
        
        # Order settings
        'order_type': 'market',        # 'market', 'limit', 'stop'
        'time_in_force': 'DAY',        # 'DAY', 'GTC', 'IOC'
        'use_stop_loss': True,         # Enable stop loss orders
        'use_take_profit': True,       # Enable take profit orders
        
        # News detection
        'check_interval_minutes': 15,  # How often to check for news
        'confidence_threshold': 0.7,   # Minimum confidence to trade
        'source_weights': {            # News source reliability weights
            'Bloomberg': 0.95,
            'Reuters': 0.95,
            'S&P Global': 0.98,
            'MarketWatch': 0.90,
            'Reddit': 0.70
        },
        
        # Logging and monitoring
        'log_level': 'INFO',
        'log_file': 'ibkr_trading.log',
        'enable_notifications': True,
        'notification_email': os.getenv('NOTIFICATION_EMAIL', ''),
        
        # Paper trading (for testing)
        'paper_trading': True,         # Set to False for live trading
        'paper_account': 'DU1234567',  # Paper trading account
        
        # Live trading (when ready)
        'live_account': os.getenv('IBKR_LIVE_ACCOUNT', ''),
        'live_port': 7496,             # 7496 for live TWS, 4000 for live Gateway
    }
    
    # Override with environment variables
    if os.getenv('IBKR_HOST'):
        config['host'] = os.getenv('IBKR_HOST')
    
    if os.getenv('IBKR_PORT'):
        config['port'] = int(os.getenv('IBKR_PORT'))
    
    if os.getenv('IBKR_CLIENT_ID'):
        config['client_id'] = int(os.getenv('IBKR_CLIENT_ID'))
    
    if os.getenv('IBKR_MAX_POSITION_SIZE'):
        config['max_position_size'] = float(os.getenv('IBKR_MAX_POSITION_SIZE'))
    
    if os.getenv('IBKR_STOP_LOSS_PCT'):
        config['stop_loss_pct'] = float(os.getenv('IBKR_STOP_LOSS_PCT'))
    
    if os.getenv('IBKR_TAKE_PROFIT_PCT'):
        config['take_profit_pct'] = float(os.getenv('IBKR_TAKE_PROFIT_PCT'))
    
    if os.getenv('IBKR_PAPER_TRADING'):
        config['paper_trading'] = os.getenv('IBKR_PAPER_TRADING').lower() == 'true'
    
    return config

def get_ibkr_connection_config() -> Dict:
    """Get IBKR connection configuration"""
    config = get_ibkr_config()
    
    return {
        'host': config['host'],
        'port': config['port'],
        'client_id': config['client_id'],
        'paper_trading': config['paper_trading']
    }

def get_ibkr_trading_config() -> Dict:
    """Get IBKR trading configuration"""
    config = get_ibkr_config()
    
    return {
        'max_position_size': config['max_position_size'],
        'stop_loss_pct': config['stop_loss_pct'],
        'take_profit_pct': config['take_profit_pct'],
        'max_positions': config['max_positions'],
        'max_daily_loss': config['max_daily_loss'],
        'max_portfolio_risk': config['max_portfolio_risk'],
        'position_sizing_method': config['position_sizing_method'],
        'order_type': config['order_type'],
        'time_in_force': config['time_in_force'],
        'use_stop_loss': config['use_stop_loss'],
        'use_take_profit': config['use_take_profit']
    }

def get_ibkr_news_config() -> Dict:
    """Get IBKR news detection configuration"""
    config = get_ibkr_config()
    
    return {
        'check_interval_minutes': config['check_interval_minutes'],
        'confidence_threshold': config['confidence_threshold'],
        'source_weights': config['source_weights']
    }

# Environment variable template
ENV_TEMPLATE = """
# IBKR Trading Configuration
# Copy these to your .env file and fill in your values

# Connection Settings
IBKR_HOST=127.0.0.1
IBKR_PORT=7497
IBKR_CLIENT_ID=1

# Trading Parameters
IBKR_MAX_POSITION_SIZE=10000
IBKR_STOP_LOSS_PCT=0.05
IBKR_TAKE_PROFIT_PCT=0.15

# Account Settings
IBKR_PAPER_TRADING=true
IBKR_LIVE_ACCOUNT=your_live_account_number

# Notifications
NOTIFICATION_EMAIL=your_email@example.com
"""

if __name__ == "__main__":
    print("🔧 IBKR Configuration")
    print("=" * 40)
    
    config = get_ibkr_config()
    
    print("📡 Connection Settings:")
    print(f"   Host: {config['host']}")
    print(f"   Port: {config['port']}")
    print(f"   Client ID: {config['client_id']}")
    print(f"   Paper Trading: {config['paper_trading']}")
    
    print("\n💰 Trading Parameters:")
    print(f"   Max Position Size: ${config['max_position_size']:,.2f}")
    print(f"   Stop Loss: {config['stop_loss_pct']:.1%}")
    print(f"   Take Profit: {config['take_profit_pct']:.1%}")
    
    print("\n📰 News Detection:")
    print(f"   Check Interval: {config['check_interval_minutes']} minutes")
    print(f"   Confidence Threshold: {config['confidence_threshold']:.1%}")
    
    print("\n💡 To customize, create a .env file with the variables above")
