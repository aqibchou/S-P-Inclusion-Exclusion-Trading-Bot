#!/usr/bin/env python3
"""
Risk-Aware Trading Configuration
Implements dynamic position sizing based on systemic risk levels
"""

# Risk-Based Position Sizing Rules
RISK_SIZING_RULES = {
    'MINIMAL': {
        'long_multiplier': 1.35,    # 135% of original size
        'short_multiplier': 0.25,   # 25% of original size
        'long_equity_pct': 0.54,    # 54% of current equity
        'short_equity_pct': 0.10,   # 10% of current equity
        'long_hold_days': 10,       # Hold added stocks for 10 days
        'short_hold_days': 3,       # Hold short positions for 3 days
        'leverage': 4.0,            # Full leverage
        'description': 'Minimal risk - aggressive long exposure, conservative short exposure'
    },
    'LOW': {
        'long_multiplier': 1.10,    # 110% of original size
        'short_multiplier': 0.50,   # 50% of original size
        'long_equity_pct': 0.44,    # 44% of current equity
        'short_equity_pct': 0.20,   # 20% of current equity
        'long_hold_days': 10,       # Hold added stocks for 10 days
        'short_hold_days': 3,       # Hold short positions for 3 days
        'leverage': 4.0,            # Full leverage
        'description': 'Low risk - moderate long exposure, balanced short exposure'
    },
    'MEDIUM': {
        'long_multiplier': 0.35,    # 35% of original size
        'short_multiplier': 1.15,   # 115% of original size
        'long_equity_pct': 0.14,    # 14% of current equity
        'short_equity_pct': 0.46,   # 46% of current equity
        'long_hold_days': 6,        # Hold added stocks for 6 days
        'short_hold_days': 5,       # Hold short positions for 5 days
        'leverage': 3.0,            # Reduced leverage
        'description': 'Medium risk - conservative long exposure, aggressive short exposure'
    },
    'HIGH': {
        'long_multiplier': 0.20,    # 20% of original size
        'short_multiplier': 1.25,   # 125% of original size
        'long_equity_pct': 0.08,    # 8% of current equity
        'short_equity_pct': 0.50,   # 50% of current equity
        'long_hold_days': 4,        # Hold added stocks for 4 days
        'short_hold_days': 6,       # Hold short positions for 6 days
        'leverage': 2.0,            # Reduced leverage
        'description': 'High risk - very conservative long exposure, maximum short exposure'
    },
    'EXTREME': {
        'long_multiplier': 0.0,     # No long positions
        'short_multiplier': 1.25,   # 125% of original size
        'long_equity_pct': 0.0,     # 0% of current equity
        'short_equity_pct': 0.50,   # 50% of current equity
        'long_hold_days': 0,        # No long positions
        'short_hold_days': 6,       # Hold short positions for 6 days
        'leverage': 2.0,            # Reduced leverage
        'description': 'Extreme risk - no long positions, maximum short exposure only'
    }
}

# Base Trading Parameters (Original Strategy)
BASE_TRADING_CONFIG = {
    'starting_capital': 100000,
    'base_risk_per_trade': 0.40,    # 40% of current equity per trade
    'base_leverage': 4.0,           # 4x leverage
    'base_long_hold_days': 10,      # Hold added stocks for 10 days
    'base_short_hold_days': 3,      # Hold short positions for 3 days
    'slippage_bps': 5,              # 5 basis points slippage
    'commission_bps': 1,            # 1 basis point commission
}

# Risk Analysis Configuration
RISK_ANALYSIS_CONFIG = {
    'risk_thresholds': {
        'MINIMAL': 0.27,    # Risk score <= 0.27
        'LOW': 0.41,        # Risk score <= 0.41
        'MEDIUM': 0.55,     # Risk score <= 0.55
        'HIGH': 0.68,       # Risk score <= 0.68
        'EXTREME': 1.0      # Risk score > 0.68
    },
    'analysis_components': {
        'correlation_risk_weight': 0.30,
        'leverage_risk_weight': 0.25,
        'liquidity_risk_weight': 0.25,
        'regulatory_risk_weight': 0.20
    },
    'historical_analysis_days': [14, 30, 60],  # Days to look back for trend analysis
}

# Trading Execution Configuration
TRADING_EXECUTION_CONFIG = {
    'news_check_interval': 30,      # Check news every 30 seconds
    'price_update_interval': 10,    # Update prices every 10 seconds
    'connection_check_interval': 60, # Check connection every minute
    'max_position_size': 100000,    # Maximum position size
    'min_position_size': 1000,      # Minimum position size
    'max_concurrent_positions': 20, # Maximum concurrent positions
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'file_handler': True,
    'console_handler': True,
    'log_file': 'enhanced_risk_aware_bot.log',
    'max_file_size': 10485760,      # 10MB
    'backup_count': 5,
    'format': '%(asctime)s - %(levelname)s - %(message)s'
}

# IBKR Configuration
IBKR_CONFIG = {
    'host': '127.0.0.1',
    'port': 7497,                   # Paper trading port
    'client_id': 1,
    'timeout': 20,
    'paper_trading': True,
    'live_trading_port': 7496,
}

def get_risk_sizing_rules():
    """Get the risk-based position sizing rules"""
    return RISK_SIZING_RULES

def get_base_trading_config():
    """Get the base trading configuration"""
    return BASE_TRADING_CONFIG

def get_risk_analysis_config():
    """Get the risk analysis configuration"""
    return RISK_ANALYSIS_CONFIG

def get_trading_execution_config():
    """Get the trading execution configuration"""
    return TRADING_EXECUTION_CONFIG

def get_logging_config():
    """Get the logging configuration"""
    return LOGGING_CONFIG

def get_ibkr_config():
    """Get the IBKR configuration"""
    return IBKR_CONFIG

def print_risk_sizing_summary():
    """Print a summary of the risk sizing rules"""
    print("🎯 RISK-AWARE POSITION SIZING RULES")
    print("=" * 50)
    
    for risk_level, rules in RISK_SIZING_RULES.items():
        print(f"\n📊 {risk_level} RISK:")
        print(f"   Long Exposure: {rules['long_multiplier']:.0%} of original size ({rules['long_equity_pct']:.0%} of equity)")
        print(f"   Short Exposure: {rules['short_multiplier']:.0%} of original size ({rules['short_equity_pct']:.0%} of equity)")
        print(f"   Hold Periods: Long {rules['long_hold_days']} days, Short {rules['short_hold_days']} days")
        print(f"   Leverage: {rules['leverage']:.1f}x")
        print(f"   Description: {rules['description']}")
    
    print(f"\n💰 BASE STRATEGY:")
    print(f"   Starting Capital: ${BASE_TRADING_CONFIG['starting_capital']:,}")
    print(f"   Base Risk per Trade: {BASE_TRADING_CONFIG['base_risk_per_trade']:.0%}")
    print(f"   Base Leverage: {BASE_TRADING_CONFIG['base_leverage']:.1f}x")
    print(f"   Base Hold Periods: Long {BASE_TRADING_CONFIG['base_long_hold_days']} days, Short {BASE_TRADING_CONFIG['base_short_hold_days']} days")

if __name__ == "__main__":
    print_risk_sizing_summary()
