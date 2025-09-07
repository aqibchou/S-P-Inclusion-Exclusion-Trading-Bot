#!/usr/bin/env python3
"""
REAL IBKR Trading Bot
Actually connects to Interactive Brokers and trades automatically
"""

import sys
import os
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_news_detector_v2 import EnhancedSP500NewsDetectorV2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('real_ibkr_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    from ib_insync import *
    IB_AVAILABLE = True
    logger.info("✅ IB Insync API imported successfully")
except ImportError as e:
    IB_AVAILABLE = False
    logger.error(f"❌ IB Insync API not available: {e}")

class RealIBKRTradingBot:
    """Real IBKR trading bot that actually connects and trades"""
    
    def __init__(self):
        self.ib = None
        self.connected = False
        self.news_detector = EnhancedSP500NewsDetectorV2()
        self.account_info = {}
        self.positions = {}
        
        # Trading parameters
        self.max_position_size = 10000  # $10k per position
        self.stop_loss_pct = 0.05      # 5% stop loss
        self.take_profit_pct = 0.15    # 15% take profit
        
        logger.info("🚀 Real IBKR Trading Bot initialized")
        logger.info(f"💰 Max position size: ${self.max_position_size:,.2f}")
        logger.info(f"🛑 Stop loss: {self.stop_loss_pct:.1%}")
        logger.info(f"🎯 Take profit: {self.take_profit_pct:.1%}")
    
    def connect_to_ibkr(self) -> bool:
        """Connect to Interactive Brokers TWS"""
        try:
            if not IB_AVAILABLE:
                logger.error("❌ IB Insync API not available")
                return False
            
            logger.info("🔌 Connecting to IBKR TWS...")
            logger.info("📋 Make sure TWS is running and API is enabled!")
            
            # Create IB connection
            self.ib = IB()
            
            # Connect to TWS
            self.ib.connect(
                host='127.0.0.1',
                port=7497,  # Paper trading port
                clientId=1,
                timeout=20
            )
            
            # Wait for connection
            if self.ib.isConnected():
                self.connected = True
                logger.info("✅ Successfully connected to IBKR TWS!")
                
                # Get account information
                self._get_account_info()
                
                # Get current positions
                self._get_positions()
                
                return True
            else:
                logger.error("❌ Failed to connect to TWS")
                return False
                
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            self.connected = False
            return False
    
    def _get_account_info(self):
        """Get account information from TWS"""
        try:
            logger.info("📊 Getting account information...")
            
            # Request account summary
            account_summary = self.ib.reqAccountSummary()
            
            # Wait for data
            self.ib.sleep(2)
            
            # Parse account info
            for summary in account_summary:
                if summary.tag == 'NetLiquidation':
                    self.account_info['net_liquidation'] = float(summary.value)
                elif summary.tag == 'TotalCashValue':
                    self.account_info['total_cash'] = float(summary.value)
                elif summary.tag == 'BuyingPower':
                    self.account_info['buying_power'] = float(summary.value)
            
            # Log account info
            logger.info("📊 ACCOUNT INFORMATION:")
            logger.info(f"   Net Liquidation: ${self.account_info.get('net_liquidation', 0):,.2f}")
            logger.info(f"   Total Cash: ${self.account_info.get('total_cash', 0):,.2f}")
            logger.info(f"   Buying Power: ${self.account_info.get('buying_power', 0):,.2f}")
            
        except Exception as e:
            logger.error(f"❌ Error getting account info: {e}")
    
    def _get_positions(self):
        """Get current positions from TWS"""
        try:
            logger.info("📈 Getting current positions...")
            
            # Get positions
            positions = self.ib.positions()
            
            if positions:
                logger.info(f"📊 Found {len(positions)} positions:")
                for pos in positions:
                    ticker = pos.contract.symbol
                    shares = pos.position
                    avg_cost = pos.avgCost
                    
                    self.positions[ticker] = {
                        'shares': shares,
                        'avg_cost': avg_cost,
                        'contract': pos.contract
                    }
                    
                    logger.info(f"   {ticker}: {shares} shares @ ${avg_cost:.2f} avg")
            else:
                logger.info("📊 No open positions found")
                
        except Exception as e:
            logger.error(f"❌ Error getting positions: {e}")
    
    def get_market_price(self, ticker: str) -> Optional[float]:
        """Get real-time market price for a ticker"""
        try:
            if not self.connected:
                logger.error("❌ Not connected to TWS")
                return None
            
            logger.info(f"📈 Getting market price for {ticker}...")
            
            # Create contract
            contract = Stock(ticker, 'SMART', 'USD')
            
            # Request market data
            self.ib.qualifyContracts(contract)
            ticker_obj = self.ib.reqMktData(contract)
            
            # Wait for data
            self.ib.sleep(3)
            
            if ticker_obj.marketPrice():
                price = ticker_obj.marketPrice()
                logger.info(f"✅ {ticker} current price: ${price:.2f}")
                return price
            else:
                logger.warning(f"⚠️ No market price available for {ticker}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting price for {ticker}: {e}")
            return None
    
    def place_market_order(self, ticker: str, side: str, shares: int, price: float) -> Dict:
        """Place a real market order with IBKR"""
        try:
            if not self.connected:
                return {'success': False, 'error': 'Not connected'}
            
            logger.info(f"📋 Placing {side} market order: {shares} shares of {ticker} at ~${price:.2f}")
            
            # Create contract
            contract = Stock(ticker, 'SMART', 'USD')
            self.ib.qualifyContracts(contract)
            
            # Create order
            if side.upper() == 'BUY':
                order = MarketOrder('BUY', shares)
            else:
                order = MarketOrder('SELL', shares)
            
            # Submit order
            trade = self.ib.placeOrder(contract, order)
            
            # Wait for order status
            self.ib.sleep(5)
            
            # Check order status
            if trade.orderStatus.status == 'Filled':
                logger.info(f"✅ {side} order filled successfully!")
                return {
                    'success': True,
                    'order_id': trade.order.orderId,
                    'status': trade.orderStatus.status,
                    'filled_price': trade.orderStatus.avgFillPrice
                }
            else:
                logger.warning(f"⚠️ Order status: {trade.orderStatus.status}")
                return {
                    'success': False,
                    'status': trade.orderStatus.status,
                    'error': 'Order not filled'
                }
                
        except Exception as e:
            logger.error(f"❌ Error placing order: {e}")
            return {'success': False, 'error': str(e)}
    
    def execute_sp500_trades(self, event: Dict) -> Dict:
        """Execute trades based on S&P 500 news event"""
        try:
            logger.info(f"🚀 Executing S&P 500 trades for event: {event.get('title', 'Unknown')}")
            
            # Extract tickers
            added_tickers = event.get('added_tickers', [])
            removed_tickers = event.get('removed_tickers', [])
            confidence = event.get('confidence', 0.5)
            
            if not added_tickers and not removed_tickers:
                logger.warning("⚠️ No tickers found in event")
                return {'success': False, 'error': 'No tickers found'}
            
            results = {
                'added_trades': [],
                'removed_trades': [],
                'total_trades': 0,
                'successful_trades': 0
            }
            
            # Execute LONG trades for added stocks
            for ticker in added_tickers:
                try:
                    current_price = self.get_market_price(ticker)
                    if current_price:
                        # Calculate position size
                        position_value = self.max_position_size * confidence
                        shares = int(position_value / current_price)
                        
                        if shares > 0:
                            # Place market buy order
                            buy_result = self.place_market_order(ticker, 'BUY', shares, current_price)
                            
                            if buy_result['success']:
                                results['added_trades'].append({
                                    'ticker': ticker,
                                    'action': 'BUY',
                                    'shares': shares,
                                    'price': current_price,
                                    'success': True
                                })
                                results['successful_trades'] += 1
                                logger.info(f"✅ BUY order successful for {ticker}")
                            else:
                                results['added_trades'].append({
                                    'ticker': ticker,
                                    'action': 'BUY',
                                    'error': buy_result.get('error', 'Unknown error')
                                })
                            
                            results['total_trades'] += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error executing BUY trade for {ticker}: {e}")
                    results['added_trades'].append({
                        'ticker': ticker,
                        'action': 'BUY',
                        'error': str(e)
                    })
                    results['total_trades'] += 1
            
            # Execute SHORT trades for removed stocks
            for ticker in removed_tickers:
                try:
                    current_price = self.get_market_price(ticker)
                    if current_price:
                        # Calculate position size
                        position_value = self.max_position_size * confidence
                        shares = int(position_value / current_price)
                        
                        if shares > 0:
                            # Place market sell order (short)
                            sell_result = self.place_market_order(ticker, 'SELL', shares, current_price)
                            
                            if sell_result['success']:
                                results['removed_trades'].append({
                                    'ticker': ticker,
                                    'action': 'SELL',
                                    'shares': shares,
                                    'price': current_price,
                                    'success': True
                                })
                                results['successful_trades'] += 1
                                logger.info(f"✅ SELL order successful for {ticker}")
                            else:
                                results['removed_trades'].append({
                                    'ticker': ticker,
                                    'action': 'SELL',
                                    'error': sell_result.get('error', 'Unknown error')
                                })
                            
                            results['total_trades'] += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error executing SELL trade for {ticker}: {e}")
                    results['removed_trades'].append({
                        'ticker': ticker,
                        'action': 'SELL',
                        'error': str(e)
                    })
                    results['total_trades'] += 1
            
            logger.info(f"✅ Trade execution complete: {results['successful_trades']}/{results['total_trades']} successful")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error executing S&P 500 trades: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_automatic_trading(self, check_interval_minutes: int = 15):
        """Run automatic trading based on S&P 500 news detection"""
        logger.info("🚀 Starting Automatic S&P 500 Trading with IBKR")
        logger.info("=" * 60)
        
        # Connect to IBKR
        if not self.connect_to_ibkr():
            logger.error("❌ Cannot start trading without IBKR connection")
            return
        
        try:
            while True:
                current_time = datetime.now()
                logger.info(f"\n⏰ {current_time.strftime('%Y-%m-%d %H:%M:%S')} - Checking for S&P 500 news...")
                
                # Check for news events
                news_events = self.news_detector.run_detection_cycle()
                
                if news_events:
                    logger.info(f"📰 Found {len(news_events)} news events")
                    
                    for event in news_events:
                        # Check if it's S&P 500 specific
                        if self.news_detector._is_sp500_specific_event(event):
                            logger.info(f"🎯 S&P 500 event detected: {event.get('title', 'Unknown')}")
                            
                            # Extract tickers
                            all_tickers = self.news_detector._extract_sp500_tickers(event)
                            added_tickers, removed_tickers = self.news_detector._classify_tickers_by_context(event, all_tickers)
                            
                            # Add ticker information to event
                            event['added_tickers'] = added_tickers
                            event['removed_tickers'] = removed_tickers
                            
                            # Execute trades
                            trade_results = self.execute_sp500_trades(event)
                            
                            if trade_results['successful_trades'] > 0:
                                logger.info(f"💰 Successfully executed {trade_results['successful_trades']} trades")
                            else:
                                logger.warning("⚠️ No trades were executed successfully")
                else:
                    logger.info("📰 No S&P 500 news events detected")
                
                # Log current positions
                self._log_positions()
                
                # Wait for next check
                logger.info(f"⏳ Waiting {check_interval_minutes} minutes until next check...")
                time.sleep(check_interval_minutes * 60)
                
        except KeyboardInterrupt:
            logger.info("🛑 Automatic trading stopped by user")
        except Exception as e:
            logger.error(f"❌ Error in automatic trading: {e}")
    
    def _log_positions(self):
        """Log current positions"""
        if self.positions:
            logger.info("📊 CURRENT POSITIONS:")
            for ticker, position in self.positions.items():
                if position['shares'] > 0:
                    current_price = self.get_market_price(ticker)
                    if current_price:
                        market_value = position['shares'] * current_price
                        pnl = (current_price - position['avg_cost']) * position['shares']
                        pnl_pct = (pnl / (position['avg_cost'] * position['shares'])) * 100
                        
                        logger.info(f"   {ticker}: {position['shares']} shares @ ${position['avg_cost']:.2f} avg")
                        logger.info(f"      Current: ${current_price:.2f} | Value: ${market_value:,.2f} | P&L: ${pnl:,.2f} ({pnl_pct:+.2f}%)")
        else:
            logger.info("📊 No open positions")
    
    def disconnect(self):
        """Disconnect from TWS"""
        try:
            if self.ib and self.ib.isConnected():
                logger.info("🔌 Disconnecting from TWS...")
                self.ib.disconnect()
                self.connected = False
                logger.info("✅ Disconnected from TWS")
        except Exception as e:
            logger.error(f"❌ Error disconnecting: {e}")

def main():
    """Main function to start the real IBKR trading bot"""
    print("🚀 REAL IBKR TRADING BOT")
    print("=" * 60)
    print("🎯 This will connect to your actual IBKR TWS and trade automatically!")
    print("📋 Make sure TWS is running and API is enabled")
    
    # Initialize bot
    bot = RealIBKRTradingBot()
    
    try:
        # Start automatic trading
        bot.run_automatic_trading(check_interval_minutes=15)
    except KeyboardInterrupt:
        print("\n🛑 Trading stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Disconnect
        bot.disconnect()
        print("\n🔌 Disconnected from TWS")

if __name__ == "__main__":
    main()
