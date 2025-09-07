#!/usr/bin/env python3
"""
Live S&P 500 News Trading Bot Runner
Automatically trades based on S&P 500 inclusion/exclusion announcements
"""

import logging
from ml_trading_bot import MLTradingBot

def main():
    """
    Main function to run the live trading bot
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('live_trading.log'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize the ML trading bot
        logger.info("🚀 Initializing Live S&P 500 News Trading Bot...")
        
        bot = MLTradingBot(
            starting_capital=10000,
            risk_per_trade=0.40,
            leverage=4.0,
            max_positions=10
        )
        
        logger.info("✅ Bot initialized successfully!")
        logger.info("📊 Starting Capital: $10,000")
        logger.info("🎯 Strategy: S&P 500 Addition/Removal Trading")
        logger.info("⏰ Check Interval: Every 15 minutes")
        logger.info("📈 Expected Returns: 500%+ based on backtest")
        
        print("\n" + "="*60)
        print("🚀 LIVE S&P 500 NEWS TRADING BOT")
        print("="*60)
        print("✅ Bot is running and monitoring for S&P 500 news...")
        print("📰 Will automatically trade on inclusion/exclusion announcements")
        print("⏰ Checking every 15 minutes for new events")
        print("🛑 Press Ctrl+C to stop the bot")
        print("="*60)
        
        # Start live trading
        bot.run_live_trading(check_interval_minutes=15)
        
    except KeyboardInterrupt:
        logger.info("🛑 Live trading stopped by user")
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Error running live bot: {e}")
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
