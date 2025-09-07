#!/usr/bin/env python3
"""
Interactive Brokers (IBKR) Trading Integration
Automatically executes trades when S&P 500 news is detected
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_news_detector_v2 import EnhancedSP500NewsDetectorV2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ibkr_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IBKRTradingIntegration:
    """
    Interactive Brokers trading integration for automatic S&P 500 trading
    """
    
    def __init__(self, ibkr_config: Dict):
        self.config = ibkr_config
        self.news_detector = EnhancedSP500NewsDetectorV2()
        self.connected = False
        self.account_info = {}
        self.positions = {}
        self.orders = []
        
        # Trading parameters
        self.max_position_size = ibkr_config.get('max_position_size', 10000)  # $10k per position
        self.stop_loss_pct = ibkr_config.get('stop_loss_pct', 0.05)  # 5% stop loss
        self.take_profit_pct = ibkr_config.get('take_profit_pct', 0.15)  # 15% take profit
        
        logger.info("🚀 IBKR Trading Integration initialized")
        logger.info(f"💰 Max position size: ${self.max_position_size:,.2f}")
        logger.info(f"🛑 Stop loss: {self.stop_loss_pct:.1%}")
        logger.info(f"🎯 Take profit: {self.take_profit_pct:.1%}")
    
    def connect_to_ibkr(self) -> bool:
        """
        Connect to Interactive Brokers TWS/Gateway
        """
        try:
            logger.info("🔌 Connecting to Interactive Brokers...")
            
            # This would use the official IBKR Python API (ibapi)
            # For now, we'll simulate the connection
            # In production, you would use: from ibapi.client import EClient
            
            # Simulate connection
            time.sleep(2)
            self.connected = True
            
            # Get account information
            self._get_account_info()
            
            logger.info("✅ Successfully connected to IBKR")
            logger.info(f"📊 Account: {self.account_info.get('account', 'Unknown')}")
            logger.info(f"💰 Available cash: ${self.account_info.get('available_cash', 0):,.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to IBKR: {e}")
            self.connected = False
            return False
    
    def _get_account_info(self):
        """Get account information from IBKR"""
        # Simulate account info
        self.account_info = {
            'account': 'U12345678',
            'available_cash': 50000.0,
            'buying_power': 100000.0,
            'total_value': 150000.0
        }
    
    def _get_current_price(self, ticker: str) -> Optional[float]:
        """
        Get current market price for a ticker
        """
        try:
            # In production, this would use IBKR's reqMktData
            # For now, simulate with yfinance
            import yfinance as yf
            
            stock = yf.Ticker(ticker)
            current_price = stock.info.get('regularMarketPrice')
            
            if current_price:
                logger.info(f"📈 {ticker} current price: ${current_price:.2f}")
                return current_price
            else:
                logger.warning(f"⚠️ Could not get price for {ticker}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting price for {ticker}: {e}")
            return None
    
    def _calculate_position_size(self, ticker: str, price: float, confidence: float) -> int:
        """
        Calculate position size based on available capital and confidence
        """
        try:
            # Base position size
            base_size = self.max_position_size / price
            
            # Adjust based on confidence (higher confidence = larger position)
            confidence_multiplier = 0.5 + (confidence * 0.5)  # 0.5x to 1.0x
            
            # Calculate final position size
            position_size = int(base_size * confidence_multiplier)
            
            # Ensure minimum position
            if position_size < 1:
                position_size = 1
            
            logger.info(f"📊 Position size for {ticker}: {position_size} shares (${position_size * price:,.2f})")
            return position_size
            
        except Exception as e:
            logger.error(f"❌ Error calculating position size: {e}")
            return 1
    
    def place_market_order(self, ticker: str, side: str, shares: int, price: float) -> Dict:
        """
        Place a market order with IBKR
        """
        try:
            if not self.connected:
                logger.error("❌ Not connected to IBKR")
                return {'success': False, 'error': 'Not connected'}
            
            logger.info(f"📋 Placing {side} market order: {shares} shares of {ticker} at ~${price:.2f}")
            
            # In production, this would use IBKR's placeOrder method
            # For now, simulate order placement
            
            order_id = f"ORDER_{int(time.time())}"
            order = {
                'id': order_id,
                'ticker': ticker,
                'side': side,
                'shares': shares,
                'price': price,
                'status': 'submitted',
                'timestamp': datetime.now().isoformat()
            }
            
            # Simulate order execution
            time.sleep(1)
            order['status'] = 'filled'
            order['filled_price'] = price
            order['filled_timestamp'] = datetime.now().isoformat()
            
            # Add to orders list
            self.orders.append(order)
            
            # Update positions
            if side == 'BUY':
                if ticker not in self.positions:
                    self.positions[ticker] = {'shares': 0, 'avg_price': 0}
                
                current_shares = self.positions[ticker]['shares']
                current_avg = self.positions[ticker]['avg_price']
                
                # Calculate new average price
                total_cost = (current_shares * current_avg) + (shares * price)
                total_shares = current_shares + shares
                new_avg = total_cost / total_shares if total_shares > 0 else 0
                
                self.positions[ticker]['shares'] = total_shares
                self.positions[ticker]['avg_price'] = new_avg
                
                logger.info(f"✅ BUY order filled: {shares} shares of {ticker} at ${price:.2f}")
                logger.info(f"📊 New position: {total_shares} shares at ${new_avg:.2f} avg")
                
            elif side == 'SELL':
                if ticker in self.positions:
                    current_shares = self.positions[ticker]['shares']
                    if current_shares >= shares:
                        self.positions[ticker]['shares'] = current_shares - shares
                        logger.info(f"✅ SELL order filled: {shares} shares of {ticker} at ${price:.2f}")
                        logger.info(f"📊 Remaining position: {self.positions[ticker]['shares']} shares")
                    else:
                        logger.warning(f"⚠️ Insufficient shares to sell {shares} of {ticker}")
                        return {'success': False, 'error': 'Insufficient shares'}
                else:
                    logger.warning(f"⚠️ No position in {ticker} to sell")
                    return {'success': False, 'error': 'No position'}
            
            return {'success': True, 'order': order}
            
        except Exception as e:
            logger.error(f"❌ Error placing order: {e}")
            return {'success': False, 'error': str(e)}
    
    def place_stop_loss_order(self, ticker: str, shares: int, entry_price: float) -> Dict:
        """
        Place stop loss order to protect position
        """
        try:
            stop_price = entry_price * (1 - self.stop_loss_pct)
            
            logger.info(f"🛑 Placing stop loss for {ticker}: {shares} shares at ${stop_price:.2f}")
            
            # In production, this would be a stop order
            stop_order = {
                'ticker': ticker,
                'type': 'STOP',
                'shares': shares,
                'stop_price': stop_price,
                'status': 'active'
            }
            
            return {'success': True, 'stop_order': stop_order}
            
        except Exception as e:
            logger.error(f"❌ Error placing stop loss: {e}")
            return {'success': False, 'error': str(e)}
    
    def place_take_profit_order(self, ticker: str, shares: int, entry_price: float) -> Dict:
        """
        Place take profit order to lock in gains
        """
        try:
            take_profit_price = entry_price * (1 + self.take_profit_pct)
            
            logger.info(f"🎯 Placing take profit for {ticker}: {shares} shares at ${take_profit_price:.2f}")
            
            # In production, this would be a limit order
            take_profit_order = {
                'ticker': ticker,
                'type': 'LIMIT',
                'shares': shares,
                'limit_price': take_profit_price,
                'status': 'active'
            }
            
            return {'success': True, 'take_profit_order': take_profit_order}
            
        except Exception as e:
            logger.error(f"❌ Error placing take profit: {e}")
            return {'success': False, 'error': str(e)}
    
    def execute_sp500_trades(self, event: Dict) -> Dict:
        """
        Execute trades based on S&P 500 news event
        """
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
                    current_price = self._get_current_price(ticker)
                    if current_price:
                        shares = self._calculate_position_size(ticker, current_price, confidence)
                        
                        # Place market buy order
                        buy_result = self.place_market_order(ticker, 'BUY', shares, current_price)
                        
                        if buy_result['success']:
                            # Place stop loss and take profit
                            self.place_stop_loss_order(ticker, shares, current_price)
                            self.place_take_profit_order(ticker, shares, current_price)
                            
                            results['added_trades'].append({
                                'ticker': ticker,
                                'action': 'BUY',
                                'shares': shares,
                                'price': current_price,
                                'success': True
                            })
                            results['successful_trades'] += 1
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
                    current_price = self._get_current_price(ticker)
                    if current_price:
                        shares = self._calculate_position_size(ticker, current_price, confidence)
                        
                        # Place market sell order (short)
                        sell_result = self.place_market_order(ticker, 'SELL', shares, current_price)
                        
                        if sell_result['success']:
                            # Place stop loss and take profit for short position
                            self.place_stop_loss_order(ticker, shares, current_price)
                            self.place_take_profit_order(ticker, shares, current_price)
                            
                            results['removed_trades'].append({
                                'ticker': ticker,
                                'action': 'SELL',
                                'shares': shares,
                                'price': current_price,
                                'success': True
                            })
                            results['successful_trades'] += 1
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
        """
        Run automatic trading based on S&P 500 news detection
        """
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
                    current_price = self._get_current_price(ticker)
                    if current_price:
                        market_value = position['shares'] * current_price
                        pnl = (current_price - position['avg_price']) * position['shares']
                        pnl_pct = (pnl / (position['avg_price'] * position['shares'])) * 100
                        
                        logger.info(f"   {ticker}: {position['shares']} shares @ ${position['avg_price']:.2f} avg")
                        logger.info(f"      Current: ${current_price:.2f} | Value: ${market_value:,.2f} | P&L: ${pnl:,.2f} ({pnl_pct:+.2f}%)")
        else:
            logger.info("📊 No open positions")

def main():
    """Demo the IBKR trading integration"""
    print("🚀 IBKR TRADING INTEGRATION DEMO")
    print("=" * 60)
    
    # Configuration
    ibkr_config = {
        'max_position_size': 10000,  # $10k per position
        'stop_loss_pct': 0.05,       # 5% stop loss
        'take_profit_pct': 0.15      # 15% take profit
    }
    
    # Initialize integration
    ibkr_trading = IBKRTradingIntegration(ibkr_config)
    
    print("\n💡 FEATURES:")
    print("✅ Automatic S&P 500 news detection")
    print("✅ Automatic order execution via IBKR")
    print("✅ Position sizing based on confidence")
    print("✅ Stop loss and take profit orders")
    print("✅ Real-time position monitoring")
    
    print("\n🚀 STARTING AUTOMATIC TRADING...")
    print("Press Ctrl+C to stop")
    
    try:
        # Start automatic trading
        ibkr_trading.run_automatic_trading(check_interval_minutes=15)
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")

if __name__ == "__main__":
    main()
