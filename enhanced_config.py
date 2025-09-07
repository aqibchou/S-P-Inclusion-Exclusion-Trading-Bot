"""
Enhanced Configuration for Improved News Detection System
"""

import os
from typing import Dict, List

# Environment variable configuration
def get_env_var(key: str, default: str = None) -> str:
    """Get environment variable with fallback"""
    return os.getenv(key, default)

# API Configuration
API_CONFIG = {
    # Financial Modeling Prep (Premium)
    'fmp_api_key': get_env_var('FMP_API_KEY', 'demo'),
    'fmp_base_url': 'https://financialmodelingprep.com/api/v3',
    'fmp_rate_limit': 250,  # Requests per month (free tier)
    
    # Alpha Vantage (Premium)
    'alpha_vantage_key': get_env_var('ALPHA_VANTAGE_KEY', 'demo'),
    'alpha_vantage_base_url': 'https://www.alphavantage.co/query',
    'alpha_vantage_rate_limit': 500,  # Requests per day (free tier)
    
    # Polygon.io (Premium)
    'polygon_key': get_env_var('POLYGON_KEY', 'demo'),
    'polygon_base_url': 'https://api.polygon.io',
    'polygon_rate_limit': 1000,  # Requests per day (free tier)
    
    # Finnhub (Premium)
    'finnhub_key': get_env_var('FINNHUB_KEY', 'demo'),
    'finnhub_base_url': 'https://finnhub.io/api/v1',
    'finnhub_rate_limit': 60,  # Requests per minute (free tier)
    
    # Reddit API (Free with registration)
    'reddit_client_id': get_env_var('REDDIT_CLIENT_ID', ''),
    'reddit_client_secret': get_env_var('REDDIT_CLIENT_SECRET', ''),
    'reddit_user_agent': 'S&P500_News_Bot/1.0',
    
    # Twitter API v2 (Premium)
    'twitter_bearer_token': get_env_var('TWITTER_BEARER_TOKEN', ''),
    'twitter_api_key': get_env_var('TWITTER_API_KEY', ''),
    'twitter_api_secret': get_env_var('TWITTER_API_SECRET', ''),
    
    # Discord Webhooks
    'discord_webhook_urls': get_env_var('DISCORD_WEBHOOK_URLS', '').split(',') if get_env_var('DISCORD_WEBHOOK_URLS') else [],
}

# Anti-Bot Bypass Configuration
ANTI_BOT_CONFIG = {
    'max_retries': 3,
    'retry_delays': [1, 2, 5],  # Progressive delays in seconds
    'request_timeout': 10,
    'max_concurrent_requests': 5,
    
    # User agent rotation
    'user_agent_rotation': True,
    'user_agent_pool_size': 50,
    
    # Proxy configuration
    'use_proxies': False,  # Set to True if you have proxy list
    'proxy_pool': [
        # Add your proxy list here
        # 'http://proxy1:port',
        # 'http://proxy2:port',
    ],
    
    # Request delays
    'scraping_delays': [2, 5, 8],  # Random delays between requests
    'min_delay': 1,  # Minimum delay between requests
    'max_delay': 10,  # Maximum delay between requests
    
    # Rate limiting
    'requests_per_minute': 30,
    'requests_per_hour': 1000,
}

# News Source Configuration
NEWS_SOURCE_CONFIG = {
    # Primary sources (Premium APIs)
    'primary_sources': [
        'financial_modeling_prep',
        'alpha_vantage',
        'polygon',
        'finnhub'
    ],
    
    # Secondary sources (Free APIs)
    'secondary_sources': [
        'yfinance',
        'reddit',
        'twitter'
    ],
    
    # Fallback sources
    'fallback_sources': [
        'sample_data',
        'manual_verification'
    ],
    
    # Source weights for confidence scoring
    'source_weights': {
        'financial_modeling_prep': 0.9,
        'alpha_vantage': 0.85,
        'polygon': 0.8,
        'finnhub': 0.8,
        'yfinance': 0.7,
        'reddit': 0.6,
        'twitter': 0.6,
        'sample_data': 0.5,
        'manual_verification': 0.8
    },
    
    # Health check intervals (seconds)
    'health_check_intervals': {
        'primary': 300,    # 5 minutes
        'secondary': 600,  # 10 minutes
        'fallback': 1800   # 30 minutes
    },
    
    # Failure thresholds
    'failure_thresholds': {
        'primary': 2,      # Mark as failed after 2 consecutive failures
        'secondary': 3,    # Mark as failed after 3 consecutive failures
        'fallback': 5      # Mark as failed after 5 consecutive failures
    }
}

# Alternative News Sources Configuration
ALTERNATIVE_SOURCES_CONFIG = {
    # Reddit subreddits to monitor
    'reddit_subreddits': [
        'wallstreetbets',
        'investing',
        'stocks',
        'SPACs',
        'options',
        'daytrading',
        'investing',
        'stockmarket'
    ],
    
    # Twitter accounts to monitor
    'twitter_accounts': [
        'SPGlobal',
        'S&P500',
        'MarketWatch',
        'ReutersBiz',
        'Bloomberg',
        'CNBC',
        'YahooFinance',
        'WSJmarkets'
    ],
    
    # Discord channels to monitor
    'discord_channels': [
        # Add your Discord channel IDs here
    ],
    
    # Telegram channels to monitor
    'telegram_channels': [
        # Add your Telegram channel usernames here
    ],
    
    # RSS feeds to monitor
    'rss_feeds': [
        'https://www.spglobal.com/spdji/en/rss-feed/',
        'https://www.marketwatch.com/rss/topstories',
        'https://feeds.reuters.com/reuters/businessNews'
    ]
}

# Event Detection Configuration
EVENT_DETECTION_CONFIG = {
    # Confidence thresholds
    'min_confidence': 0.7,
    'high_confidence': 0.9,
    'critical_confidence': 0.95,
    
    # Keywords for S&P 500 events
    'sp500_keywords': [
        's&p 500', 's&p500', 'sp500', 'sp 500',
        'standard & poor', 'standard and poor',
        'index addition', 'index removal', 'index change',
        'added to s&p', 'removed from s&p',
        's&p inclusion', 's&p exclusion',
        'index rebalancing', 'index reconstitution',
        'constituent change', 'index composition'
    ],
    
    # Company-specific keywords
    'company_keywords': [
        'market cap', 'market capitalization',
        'index eligibility', 'index criteria',
        'float adjustment', 'public float',
        'listing requirements', 'index weight'
    ],
    
    # Event patterns
    'addition_patterns': [
        r'(\w+) added to s&p 500',
        r'(\w+) joins s&p 500',
        r'(\w+) enters s&p 500',
        r's&p 500 adds (\w+)',
        r'(\w+) to be added to s&p 500',
        r'(\w+) included in s&p 500'
    ],
    
    'removal_patterns': [
        r'(\w+) removed from s&p 500',
        r'(\w+) exits s&p 500',
        r'(\w+) leaves s&p 500',
        r's&p 500 removes (\w+)',
        r'(\w+) to be removed from s&p 500',
        r'(\w+) excluded from s&p 500'
    ]
}

# Machine Learning Configuration
ML_CONFIG = {
    # Model settings
    'model_type': 'ensemble',  # 'ensemble', 'random_forest', 'gradient_boosting'
    'confidence_calibration': True,
    'feature_importance_threshold': 0.01,
    
    # Training settings
    'retrain_interval': 86400,  # 24 hours
    'min_training_samples': 100,
    'validation_split': 0.2,
    
    # Feature engineering
    'use_sentiment_analysis': True,
    'use_entity_recognition': True,
    'use_topic_modeling': True,
    
    # Anomaly detection
    'anomaly_detection': True,
    'anomaly_threshold': 0.8,
    'anomaly_window_size': 24  # hours
}

# Monitoring and Alerting Configuration
MONITORING_CONFIG = {
    # Health monitoring
    'health_check_interval': 300,  # 5 minutes
    'source_monitoring': True,
    'performance_monitoring': True,
    
    # Alerting
    'enable_alerts': True,
    'alert_channels': ['log', 'email', 'discord'],
    
    # Alert thresholds
    'alert_thresholds': {
        'source_failure_rate': 0.5,  # Alert if 50% of sources fail
        'detection_accuracy': 0.7,   # Alert if accuracy drops below 70%
        'response_time': 5.0,        # Alert if response time exceeds 5 seconds
        'error_rate': 0.1            # Alert if error rate exceeds 10%
    },
    
    # Logging
    'log_level': 'INFO',
    'log_file': 'enhanced_news_detector.log',
    'max_log_size': 10485760,  # 10MB
    'backup_count': 5
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    # Caching
    'enable_caching': True,
    'cache_ttl': 3600,  # 1 hour
    'max_cache_size': 1000,
    
    # Rate limiting
    'global_rate_limit': 100,  # Requests per minute
    'per_source_rate_limit': 20,  # Requests per minute per source
    
    # Timeouts
    'connection_timeout': 5,
    'read_timeout': 10,
    'total_timeout': 30,
    
    # Retry logic
    'max_retries': 3,
    'backoff_factor': 2,
    'max_backoff': 60
}

# Integration Configuration
INTEGRATION_CONFIG = {
    # Trading bot integration
    'trading_bot_enabled': True,
    'auto_trade': False,  # Set to True for automatic trading
    'trade_confirmation_required': True,
    
    # Database integration
    'database_enabled': False,
    'database_url': get_env_var('DATABASE_URL', ''),
    
    # External APIs
    'enable_webhooks': True,
    'webhook_urls': get_env_var('WEBHOOK_URLS', '').split(',') if get_env_var('WEBHOOK_URLS') else [],
    
    # File storage
    'enable_file_storage': True,
    'storage_path': './data/news_events/',
    'backup_enabled': True,
    'backup_interval': 86400  # 24 hours
}

# Security Configuration
SECURITY_CONFIG = {
    # API key rotation
    'enable_key_rotation': False,
    'key_rotation_interval': 86400,  # 24 hours
    
    # Request validation
    'validate_requests': True,
    'sanitize_inputs': True,
    'rate_limit_by_ip': True,
    
    # Data privacy
    'log_sensitive_data': False,
    'encrypt_stored_data': False,
    'anonymize_user_data': True
}

# Development Configuration
DEV_CONFIG = {
    # Debug mode
    'debug_mode': False,
    'verbose_logging': False,
    'test_mode': False,
    
    # Development features
    'enable_mock_data': False,
    'mock_data_path': './test_data/',
    'enable_profiling': False,
    
    # Testing
    'test_historical_data': True,
    'test_historical_file': 'events_full_csv__S_P_500_Adds_Removes___3_years_.csv',
    'test_accuracy_threshold': 0.8
}

# Combine all configurations
ENHANCED_CONFIG = {
    'api': API_CONFIG,
    'anti_bot': ANTI_BOT_CONFIG,
    'news_sources': NEWS_SOURCE_CONFIG,
    'alternative_sources': ALTERNATIVE_SOURCES_CONFIG,
    'event_detection': EVENT_DETECTION_CONFIG,
    'ml': ML_CONFIG,
    'monitoring': MONITORING_CONFIG,
    'performance': PERFORMANCE_CONFIG,
    'integration': INTEGRATION_CONFIG,
    'security': SECURITY_CONFIG,
    'development': DEV_CONFIG
}

def get_config() -> Dict:
    """Get the complete enhanced configuration"""
    return ENHANCED_CONFIG

def get_api_config() -> Dict:
    """Get API configuration"""
    return API_CONFIG

def get_anti_bot_config() -> Dict:
    """Get anti-bot configuration"""
    return ANTI_BOT_CONFIG

def get_news_source_config() -> Dict:
    """Get news source configuration"""
    return NEWS_SOURCE_CONFIG

def get_event_detection_config() -> Dict:
    """Get event detection configuration"""
    return EVENT_DETECTION_CONFIG

if __name__ == "__main__":
    # Print configuration summary
    config = get_config()
    print("🚀 Enhanced News Detection Configuration")
    print("=" * 50)
    print(f"API Sources: {len(config['api'])} configured")
    print(f"Anti-Bot Features: {len(config['anti_bot'])} configured")
    print(f"News Sources: {len(config['news_sources']['primary_sources'])} primary, {len(config['news_sources']['secondary_sources'])} secondary")
    print(f"Alternative Sources: {len(config['alternative_sources']['reddit_subreddits'])} Reddit, {len(config['alternative_sources']['twitter_accounts'])} Twitter")
    print(f"Event Detection: {len(config['event_detection']['sp500_keywords'])} keywords, {len(config['event_detection']['addition_patterns'])} patterns")
    print(f"ML Features: {config['ml']['model_type']} model, {config['ml']['use_sentiment_analysis']} sentiment analysis")
    print(f"Monitoring: {config['monitoring']['health_check_interval']}s health checks, {config['monitoring']['enable_alerts']} alerts")
    print("✅ Configuration loaded successfully!")
