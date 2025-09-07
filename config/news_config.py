#!/usr/bin/env python3
"""
Configuration for S&P 500 News Detection System
"""

# News Detection Configuration
NEWS_CONFIG = {
    # Confidence thresholds
    'confidence_threshold': 0.6,  # Minimum confidence to consider an event
    'high_confidence_threshold': 0.8,  # High confidence events get priority
    
    # Check intervals
    'check_interval_minutes': 15,  # How often to check for news
    'cache_duration_hours': 1,  # How long to cache events
    
    # Source weights (higher = more reliable)
    'source_weights': {
        'yahoo_finance': 0.4,
        'market_watch': 0.3,
        'reuters': 0.2,
        'bloomberg': 0.1,
        'financial_modeling_prep': 0.5,  # High weight for API data
        'alpha_vantage': 0.4,  # High weight for API data
        'manual_verification': 0.3,
        'sample_data': 0.9,  # Highest weight for verified sample data
        'synthetic_data': 0.1  # Lowest weight for synthetic data
    },
    
    # Keywords for S&P 500 change detection
    'sp500_keywords': [
        's&p 500', 'sp500', 's&p500', 'standard & poor',
        'index addition', 'index removal', 'index change',
        'added to', 'removed from', 'joins', 'leaves',
        'constituent', 'rebalance', 'rebalancing',
        'index rebalancing', 'constituent change'
    ],
    
    # Anomaly detection thresholds
    'anomaly_thresholds': {
        'volume_spike_multiplier': 2.0,  # 2x average volume
        'price_move_percentage': 2.0,  # 2% price move
        'major_stock_price_move': 5.0,  # 5% move in major stocks
        'major_stock_volume_increase': 200.0  # 200% volume increase
    }
}

# API Configuration (add your keys here)
API_CONFIG = {
    'financial_modeling_prep': {
        'enabled': False,  # Set to True if you have an API key
        'api_key': 'YOUR_FMP_API_KEY_HERE',
        'base_url': 'https://financialmodelingprep.com/api/v3',
        'endpoints': {
            'sp500_changes': '/sp500_constituent',
            'company_profile': '/profile'
        }
    },
    
    'alpha_vantage': {
        'enabled': False,  # Set to True if you have an API key
        'api_key': 'YOUR_ALPHA_VANTAGE_API_KEY_HERE',
        'base_url': 'https://www.alphavantage.co/query',
        'endpoints': {
            'news_sentiment': '/news_sentiment',
            'company_overview': '/company-overview'
        }
    },
    
    'yahoo_finance': {
        'enabled': True,  # Always enabled (free)
        'max_news_items': 20,
        'tickers': ['SPY', '^GSPC', 'VOO', 'IVV']  # S&P 500 related tickers
    }
}

# Web Scraping Configuration
SCRAPING_CONFIG = {
    'enabled': True,
    'timeout_seconds': 10,
    'max_retries': 3,
    'user_agents': [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    ],
    
    'sources': {
        'market_watch': {
            'enabled': True,
            'url': 'https://www.marketwatch.com/investing/index/spx',
            'keywords': ['s&p 500', 'sp500', 'index']
        },
        'reuters': {
            'enabled': True,
            'url': 'https://www.reuters.com/markets/',
            'keywords': ['s&p 500', 'sp500', 'index']
        },
        'bloomberg': {
            'enabled': True,
            'url': 'https://www.bloomberg.com/markets',
            'keywords': ['s&p 500', 'sp500', 'index']
        }
    }
}

# Fallback Configuration
FALLBACK_CONFIG = {
    'use_sample_data': True,
    'use_synthetic_data': True,
    'sample_data_file': 'events_sample.csv',
    'synthetic_data': {
        'start_date': '2022-01-01',
        'end_date': '2025-12-31',
        'frequency': 'M',  # Monthly
        'change_probability': 0.3  # 30% chance of index change per period
    }
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'news_detection.log',
    'max_file_size_mb': 10,
    'backup_count': 5
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    'max_concurrent_requests': 5,
    'request_delay_seconds': 1,  # Delay between requests to avoid rate limiting
    'cache_enabled': True,
    'cache_size_mb': 100
}

def get_config():
    """
    Get the complete configuration
    """
    return {
        'news': NEWS_CONFIG,
        'api': API_CONFIG,
        'scraping': SCRAPING_CONFIG,
        'fallback': FALLBACK_CONFIG,
        'logging': LOGGING_CONFIG,
        'performance': PERFORMANCE_CONFIG
    }

def validate_config():
    """
    Validate the configuration
    """
    config = get_config()
    
    # Check required fields
    required_fields = [
        'news.confidence_threshold',
        'news.source_weights',
        'api.yahoo_finance.enabled'
    ]
    
    for field in required_fields:
        keys = field.split('.')
        value = config
        for key in keys:
            if key not in value:
                print(f"❌ Missing required config: {field}")
                return False
            value = value[key]
    
    print("✅ Configuration validation passed")
    return True

if __name__ == "__main__":
    # Test configuration
    print("🔧 Testing News Detection Configuration")
    print("=" * 50)
    
    config = get_config()
    
    print(f"📊 Confidence Threshold: {config['news']['confidence_threshold']}")
    print(f"⏰ Check Interval: {config['news']['check_interval_minutes']} minutes")
    print(f"🔑 FMP API Enabled: {config['api']['financial_modeling_prep']['enabled']}")
    print(f"🔑 Alpha Vantage Enabled: {config['api']['alpha_vantage']['enabled']}")
    print(f"📡 Yahoo Finance Enabled: {config['api']['yahoo_finance']['enabled']}")
    print(f"🕷️ Web Scraping Enabled: {config['scraping']['enabled']}")
    
    print("\n💡 To enable premium APIs:")
    print("   1. Get API keys from Financial Modeling Prep or Alpha Vantage")
    print("   2. Update the API_CONFIG section in this file")
    print("   3. Set 'enabled' to True for the desired API")
    
    validate_config()

