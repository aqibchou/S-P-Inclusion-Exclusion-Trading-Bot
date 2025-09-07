#!/usr/bin/env python3
"""
Enhanced Risk-Aware Trading Bot V2 with Historical Risk Analysis and Enhanced Gold Hedging
Implements trend-based position sizing and advanced gold hedging logic
"""

import sys
import os
import time
import asyncio
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from enhanced_news_detector_v2 import EnhancedSP500NewsDetectorV2
from systemic_risk.systemic_risk_detector import SystemicRiskDetector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_risk_aware_bot_v2.log'),
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

class EnhancedRiskAwareBotV2:
    """Enhanced trading bot with historical risk analysis and advanced gold hedging"""
    
    def __init__(self, starting_capital: float = 100000):
        self.ib = None
        self.connected = False
        self.news_detector = EnhancedSP500NewsDetectorV2()
        self.systemic_risk_detector = SystemicRiskDetector()
        self.account_info = {}
        self.positions = {}
        self.running = False
        self.starting_capital = starting_capital
        self.current_capital = starting_capital
        
        # Base trading parameters (original strategy)
        self.base_risk_per_trade = 0.40  # 40% of current equity per trade
        self.base_leverage = 4.0         # 4x leverage
        self.base_long_hold_days = 10    # Hold added stocks for 10 days
        self.base_short_hold_days = 3    # Hold short positions for 3 days
        
        # Risk-based position sizing rules
        self.risk_sizing_rules = {
            'MINIMAL': {
                'long_multiplier': 1.35,    # 135% of original size
                'short_multiplier': 0.25,   # 25% of original size
                'long_equity_pct': 0.54,    # 54% of current equity
                'short_equity_pct': 0.10,   # 10% of current equity
                'long_leverage': 4.0,       # 4x leverage for long
                'short_leverage': 4.0,      # 4x leverage for short
                'long_hold_days': 10,
                'short_hold_days': 3
            },
            'LOW': {
                'long_multiplier': 1.10,    # 110% of original size
                'short_multiplier': 0.50,   # 50% of original size
                'long_equity_pct': 0.44,    # 44% of current equity
                'short_equity_pct': 0.20,   # 20% of current equity
                'long_leverage': 4.0,       # 4x leverage for long
                'short_leverage': 4.0,      # 4x leverage for short
                'long_hold_days': 10,
                'short_hold_days': 3
            },
            'MEDIUM': {
                'long_multiplier': 0.35,    # 35% of original size
                'short_multiplier': 1.15,   # 115% of original size
                'long_equity_pct': 0.14,    # 14% of current equity
                'short_equity_pct': 0.46,   # 46% of current equity
                'long_leverage': 2.5,       # 2.5x leverage for long
                'short_leverage': 4.0,      # 4x leverage for short
                'long_hold_days': 6,
                'short_hold_days': 5
            },
            'HIGH': {
                'long_multiplier': 0.20,    # 20% of original size
                'short_multiplier': 1.25,   # 125% of original size
                'long_equity_pct': 0.08,    # 8% of current equity
                'short_equity_pct': 0.50,   # 50% of current equity
                'long_leverage': 1.5,       # 1.5x leverage for long
                'short_leverage': 4.0,      # 4x leverage for short
                'long_hold_days': 4,
                'short_hold_days': 6
            },
            'EXTREME': {
                'long_multiplier': 0.0,     # No long positions
                'short_multiplier': 1.25,   # 125% of original size
                'long_equity_pct': 0.0,     # 0% of current equity
                'short_equity_pct': 0.50,   # 50% of current equity
                'long_leverage': 0.0,       # No long leverage
                'short_leverage': 4.0,      # 4x leverage for short
                'long_hold_days': 0,
                'short_hold_days': 6
            }
        }
        
        # Trend-based sizing rules (for improving trends)
        self.trend_sizing_rules = {
            'long_multiplier': 1.25,    # 125% of original size
            'short_multiplier': 0.50,   # 50% of original size
            'long_equity_pct': 0.50,    # 50% of current equity
            'short_equity_pct': 0.20,   # 20% of current equity
            'long_hold_days': 10,
            'short_hold_days': 3
        }
        
        # Gold hedging configuration with risk-based percentages
        self.gold_hedging_config = {
            'symbol': 'GC=F',                   # Gold Spot Futures symbol
            'leverage': 3.2,                    # 3.2x leverage for gold
            'hold_days': 20,                    # Hold gold for 20 days
            'min_risk_threshold': 0.41,         # Risk < 0.41 no hedging
            'auto_risk_threshold': 0.48,        # Risk >= 0.48 automatic hedging
            'risk_based_percentages': {
                'EXTREME': 0.50,                # 50% of equity
                'HIGH': 0.42,                   # 42% of equity
                'MEDIUM': 0.40,                 # 40% of equity
                'LOW': 0.40,                    # 40% of equity (default)
                'MINIMAL': 0.40                 # 40% of equity (default)
            }
        }
        
        # Real-time monitoring settings
        self.news_check_interval = 30  # Check news every 30 seconds
        self.price_update_interval = 10  # Update prices every 10 seconds
        self.connection_check_interval = 60  # Check connection every minute
        
        logger.info("🚀 Enhanced Risk-Aware Trading Bot V2 initialized")
        logger.info(f"💰 Starting capital: ${self.starting_capital:,.2f}")
        logger.info(f"📊 Historical risk analysis enabled")
        logger.info(f"🥇 Enhanced gold hedging enabled")
        logger.info(f"📰 News check interval: {self.news_check_interval} seconds")
    
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
            
            # Update current capital
            self.current_capital = self.account_info.get('net_liquidation', self.starting_capital)
            
            # Log account info
            logger.info("📊 ACCOUNT INFORMATION:")
            logger.info(f"   Net Liquidation: ${self.account_info.get('net_liquidation', 0):,.2f}")
            logger.info(f"   Total Cash: ${self.account_info.get('total_cash', 0):,.2f}")
            logger.info(f"   Buying Power: ${self.account_info.get('buying_power', 0):,.2f}")
            logger.info(f"   Current Capital: ${self.current_capital:,.2f}")
            
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
    
    def run_historical_risk_analysis(self, event_date: datetime = None) -> Dict:
        """Run historical risk analysis comparing current vs 2 months ago"""
        try:
            if event_date is None:
                event_date = datetime.now()
            
            logger.info(f"📊 Running historical risk analysis for {event_date.strftime('%Y-%m-%d')}")
            
            # Calculate current risk
            current_risk = self.systemic_risk_detector.calculate_systemic_risk_score(event_date)
            if not current_risk:
                logger.warning("⚠️ Could not calculate current risk")
                return None
            
            # Calculate risk 2 months ago
            two_months_ago = event_date - timedelta(days=60)
            historical_risk = self.systemic_risk_detector.calculate_systemic_risk_score(two_months_ago)
            if not historical_risk:
                logger.warning("⚠️ Could not calculate historical risk")
                return None
            
            # Compare risk levels
            current_score = current_risk['systemic_risk_score']
            historical_score = historical_risk['systemic_risk_score']
            current_level = current_risk['risk_level']
            historical_level = historical_risk['risk_level']
            
            # Determine trend
            risk_improving = current_score < historical_score
            risk_deteriorating = current_score > historical_score
            risk_same = abs(current_score - historical_score) < 0.05  # Within 5% is considered same
            
            trend_analysis = {
                'current_risk': current_risk,
                'historical_risk': historical_risk,
                'current_score': current_score,
                'historical_score': historical_score,
                'current_level': current_level,
                'historical_level': historical_level,
                'risk_improving': risk_improving,
                'risk_deteriorating': risk_deteriorating,
                'risk_same': risk_same,
                'analysis_date': event_date,
                'historical_date': two_months_ago
            }
            
            logger.info(f"📊 HISTORICAL RISK COMPARISON:")
            logger.info(f"   Current: {current_level} (Score: {current_score:.3f})")
            logger.info(f"   2 Months Ago: {historical_level} (Score: {historical_score:.3f})")
            logger.info(f"   Trend: {'IMPROVING' if risk_improving else 'DETERIORATING' if risk_deteriorating else 'SAME'}")
            
            return trend_analysis
            
        except Exception as e:
            logger.error(f"❌ Error in historical risk analysis: {e}")
            return None
    
    def run_systemic_risk_analysis(self, event_date: datetime = None) -> Dict:
        """Run systemic risk analysis for current or specified date"""
        try:
            if event_date is None:
                event_date = datetime.now()
            
            logger.info(f"🚨 Running systemic risk analysis for {event_date.strftime('%Y-%m-%d')}")
            
            # Calculate systemic risk score
            risk_analysis = self.systemic_risk_detector.calculate_systemic_risk_score(event_date)
            
            if not risk_analysis:
                logger.warning("⚠️ Could not calculate systemic risk, using LOW risk as fallback")
                return {
                    'risk_score': 0.3,
                    'risk_level': 'LOW',
                    'risk_components': {},
                    'analysis_date': event_date
                }
            
            logger.info(f"📊 Risk Analysis Results:")
            logger.info(f"   Risk Score: {risk_analysis['systemic_risk_score']:.3f}")
            logger.info(f"   Risk Level: {risk_analysis['risk_level']}")
            
            return risk_analysis
            
        except Exception as e:
            logger.error(f"❌ Error in systemic risk analysis: {e}")
            return {
                'risk_score': 0.3,
                'risk_level': 'LOW',
                'risk_components': {},
                'analysis_date': event_date
            }
    
    def calculate_enhanced_position_sizing(self, risk_level: str, ticker: str, side: str, trend_analysis: Dict = None) -> Dict:
        """Calculate enhanced position sizing with trend analysis"""
        try:
            # Check if we should use trend-based sizing
            use_trend_sizing = False
            if trend_analysis and risk_level in ['MEDIUM', 'HIGH']:
                if trend_analysis['risk_improving']:
                    use_trend_sizing = True
                    logger.info(f"🎯 Using trend-based sizing for {ticker} - Risk improving")
            
            if use_trend_sizing:
                # Use trend-based sizing (125% long, 50% short)
                rules = self.trend_sizing_rules
                sizing_type = "TREND_BASED"
            else:
                # Use standard risk-based sizing
                if risk_level not in self.risk_sizing_rules:
                    logger.warning(f"⚠️ Unknown risk level: {risk_level}, using LOW as fallback")
                    risk_level = 'LOW'
                rules = self.risk_sizing_rules[risk_level]
                sizing_type = "RISK_BASED"
            
            # Calculate position size based on risk level
            if side.upper() == 'LONG':
                equity_pct = rules['long_equity_pct']
                multiplier = rules['long_multiplier']
                hold_days = rules['long_hold_days']
            else:  # SHORT
                equity_pct = rules['short_equity_pct']
                multiplier = rules['short_multiplier']
                hold_days = rules['short_hold_days']
            
            # Calculate position value
            position_value = self.current_capital * equity_pct
            
            # Apply multiplier to base position size
            base_position_size = self.current_capital * self.base_risk_per_trade
            adjusted_position_size = base_position_size * multiplier
            
            # Use the smaller of the two (equity percentage vs multiplier approach)
            final_position_size = min(position_value, adjusted_position_size)
            
            # Calculate leverage based on risk level and side
            if side.upper() == 'LONG':
                leverage = rules.get('long_leverage', self.base_leverage)
            else:  # SHORT
                leverage = rules.get('short_leverage', self.base_leverage)
            
            sizing_info = {
                'position_size': final_position_size,
                'equity_pct': equity_pct,
                'multiplier': multiplier,
                'hold_days': hold_days,
                'leverage': leverage,
                'risk_level': risk_level,
                'side': side.upper(),
                'sizing_type': sizing_type,
                'trend_improving': trend_analysis['risk_improving'] if trend_analysis else False
            }
            
            logger.info(f"📊 Enhanced Position Sizing for {ticker} ({side}):")
            logger.info(f"   Sizing Type: {sizing_type}")
            logger.info(f"   Risk Level: {risk_level}")
            logger.info(f"   Position Size: ${final_position_size:,.2f}")
            logger.info(f"   Equity %: {equity_pct:.1%}")
            logger.info(f"   Multiplier: {multiplier:.2f}x")
            logger.info(f"   Hold Days: {hold_days}")
            logger.info(f"   Leverage: {leverage:.1f}x")
            if trend_analysis:
                logger.info(f"   Trend Improving: {trend_analysis['risk_improving']}")
            
            return sizing_info
            
        except Exception as e:
            logger.error(f"❌ Error calculating enhanced position sizing: {e}")
            return {
                'position_size': 0,
                'equity_pct': 0,
                'multiplier': 0,
                'hold_days': 0,
                'leverage': 1.0,
                'risk_level': 'LOW',
                'side': side.upper(),
                'sizing_type': 'ERROR',
                'trend_improving': False
            }
    
    def calculate_gold_hedging_decision(self, risk_analysis: Dict, trend_analysis: Dict = None) -> Dict:
        """Calculate gold hedging decision based on enhanced logic"""
        try:
            risk_score = risk_analysis['systemic_risk_score']
            risk_level = risk_analysis['risk_level']
            
            # Initialize hedging decision
            hedging_decision = {
                'recommended': False,
                'reason': '',
                'position_size': 0,
                'leverage': self.gold_hedging_config['leverage'],
                'hold_days': self.gold_hedging_config['hold_days'],
                'symbol': self.gold_hedging_config['symbol']
            }
            
            # Rule 1: Risk < 0.41 - No hedging regardless of trend
            if risk_score < self.gold_hedging_config['min_risk_threshold']:
                hedging_decision['recommended'] = False
                hedging_decision['reason'] = f"Risk score ({risk_score:.3f}) < {self.gold_hedging_config['min_risk_threshold']} - No gold hedging"
                logger.info(f"📊 NO GOLD HEDGING: {hedging_decision['reason']}")
            
            # Rule 2: Risk >= 0.48 - Always hedge regardless of trend
            elif risk_score >= self.gold_hedging_config['auto_risk_threshold']:
                hedging_decision['recommended'] = True
                hedging_decision['reason'] = f"Risk score ({risk_score:.3f}) >= {self.gold_hedging_config['auto_risk_threshold']} - Automatic gold hedging"
                logger.info(f"🥇 GOLD HEDGING RECOMMENDED: {hedging_decision['reason']}")
            
            # Rule 3: Risk >= 0.41 and < 0.48 - Trend-based hedging
            elif risk_score >= self.gold_hedging_config['min_risk_threshold']:
                # Medium risk + deteriorating trend -> Hedge
                if risk_level == 'MEDIUM' and trend_analysis is not None and trend_analysis.get('risk_deteriorating', False):
                    hedging_decision['recommended'] = True
                    hedging_decision['reason'] = f"MEDIUM risk with deteriorating trend: {trend_analysis['current_score']:.3f} > {trend_analysis['historical_score']:.3f}"
                    logger.info(f"🥇 GOLD HEDGING RECOMMENDED: {hedging_decision['reason']}")
                
                # High risk + same/deteriorating trend -> Hedge
                elif risk_level == 'HIGH' and trend_analysis is not None and (trend_analysis.get('risk_deteriorating', False) or trend_analysis.get('risk_same', False)):
                    hedging_decision['recommended'] = True
                    hedging_decision['reason'] = f"HIGH risk with deteriorating/same trend: {trend_analysis['current_score']:.3f} >= {trend_analysis['historical_score']:.3f}"
                    logger.info(f"🥇 GOLD HEDGING RECOMMENDED: {hedging_decision['reason']}")
                
                # No hedging for improving trends in this range
                else:
                    hedging_decision['recommended'] = False
                    hedging_decision['reason'] = f"Risk score ({risk_score:.3f}) in trend-based range but trend conditions not met"
                    logger.info(f"📊 NO GOLD HEDGING: {hedging_decision['reason']}")
            
            # Rule 4: EXTREME risk - Always hedge regardless of trend (fallback)
            elif risk_level == "EXTREME":
                hedging_decision['recommended'] = True
                hedging_decision['reason'] = f"EXTREME risk level - automatic hedging"
                logger.info(f"🥇 GOLD HEDGING RECOMMENDED: {hedging_decision['reason']}")
            
            # Rule 5: No hedging for other cases
            else:
                hedging_decision['recommended'] = False
                hedging_decision['reason'] = f"Risk level {risk_level} does not meet hedging criteria"
                logger.info(f"📊 NO GOLD HEDGING: {hedging_decision['reason']}")
            
            # Calculate position size if hedging is recommended
            if hedging_decision['recommended']:
                # Use risk-based percentage of current equity for gold hedging
                equity_pct = self.gold_hedging_config['risk_based_percentages'].get(risk_level, 0.40)
                gold_position_size = self.current_capital * equity_pct
                hedging_decision['position_size'] = gold_position_size
                
                logger.info(f"🥇 Gold Hedging Details:")
                logger.info(f"   Risk Level: {risk_level}")
                logger.info(f"   Equity %: {equity_pct:.1%}")
                logger.info(f"   Position Size: ${gold_position_size:,.2f}")
                logger.info(f"   Leverage: {hedging_decision['leverage']:.1f}x")
                logger.info(f"   Hold Days: {hedging_decision['hold_days']}")
                logger.info(f"   Symbol: {hedging_decision['symbol']}")
            
            return hedging_decision
            
        except Exception as e:
            logger.error(f"❌ Error calculating gold hedging decision: {e}")
            return {
                'recommended': False,
                'reason': f"Error: {str(e)}",
                'position_size': 0,
                'leverage': 1.0,
                'hold_days': 0,
                'symbol': 'GLD'
            }
    
    def get_market_price(self, ticker: str) -> Optional[float]:
        """Get real-time market price for a ticker"""
        try:
            if not self.connected:
                logger.error("❌ Not connected to TWS")
                return None
            
            # Create contract
            contract = Stock(ticker, 'SMART', 'USD')
            
            # Request market data
            self.ib.qualifyContracts(contract)
            ticker_obj = self.ib.reqMktData(contract)
            
            # Wait for data
            self.ib.sleep(1)
            
            if ticker_obj.marketPrice():
                price = ticker_obj.marketPrice()
                return price
            else:
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
            self.ib.sleep(3)
            
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
    
    def execute_enhanced_risk_aware_trades(self, event: Dict) -> Dict:
        """Execute trades with enhanced risk-aware position sizing and gold hedging"""
        try:
            logger.info(f"🚀 Executing enhanced risk-aware trades for event: {event.get('title', 'Unknown')}")
            
            # Extract tickers
            added_tickers = event.get('added_tickers', [])
            removed_tickers = event.get('removed_tickers', [])
            confidence = event.get('confidence', 0.5)
            
            if not added_tickers and not removed_tickers:
                logger.warning("⚠️ No tickers found in event")
                return {'success': False, 'error': 'No tickers found'}
            
            # Run systemic risk analysis
            risk_analysis = self.run_systemic_risk_analysis()
            risk_level = risk_analysis.get('risk_level', 'LOW')
            risk_score = risk_analysis.get('systemic_risk_score', 0.0)
            
            logger.info(f"🎯 Risk Level: {risk_level} (Score: {risk_score:.3f})")
            
            # Run historical risk analysis for medium/high risk
            trend_analysis = None
            if risk_level in ['MEDIUM', 'HIGH', 'EXTREME']:
                trend_analysis = self.run_historical_risk_analysis()
            
            # Calculate gold hedging decision
            gold_hedging = self.calculate_gold_hedging_decision(risk_analysis, trend_analysis)
            
            results = {
                'added_trades': [],
                'removed_trades': [],
                'gold_hedging': gold_hedging,
                'total_trades': 0,
                'successful_trades': 0,
                'risk_level': risk_level,
                'risk_score': risk_score,
                'trend_analysis': trend_analysis
            }
            
            # Execute LONG trades for added stocks
            for ticker in added_tickers:
                try:
                    # Calculate enhanced position sizing
                    sizing_info = self.calculate_enhanced_position_sizing(risk_level, ticker, 'LONG', trend_analysis)
                    
                    # Skip if no position size allowed
                    if sizing_info['position_size'] <= 0:
                        logger.info(f"🚫 Skipping {ticker} - No long positions allowed for {risk_level} risk")
                        continue
                    
                    current_price = self.get_market_price(ticker)
                    if current_price:
                        # Calculate shares based on position size
                        shares = int(sizing_info['position_size'] / current_price)
                        
                        if shares > 0:
                            # Place market buy order
                            buy_result = self.place_market_order(ticker, 'BUY', shares, current_price)
                            
                            if buy_result['success']:
                                results['added_trades'].append({
                                    'ticker': ticker,
                                    'action': 'BUY',
                                    'shares': shares,
                                    'price': current_price,
                                    'position_size': sizing_info['position_size'],
                                    'equity_pct': sizing_info['equity_pct'],
                                    'multiplier': sizing_info['multiplier'],
                                    'hold_days': sizing_info['hold_days'],
                                    'leverage': sizing_info['leverage'],
                                    'risk_level': risk_level,
                                    'sizing_type': sizing_info['sizing_type'],
                                    'trend_improving': sizing_info['trend_improving'],
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
                    # Calculate enhanced position sizing
                    sizing_info = self.calculate_enhanced_position_sizing(risk_level, ticker, 'SHORT', trend_analysis)
                    
                    # Skip if no position size allowed
                    if sizing_info['position_size'] <= 0:
                        logger.info(f"🚫 Skipping {ticker} - No short positions allowed for {risk_level} risk")
                        continue
                    
                    current_price = self.get_market_price(ticker)
                    if current_price:
                        # Calculate shares based on position size
                        shares = int(sizing_info['position_size'] / current_price)
                        
                        if shares > 0:
                            # Place market sell order (short)
                            sell_result = self.place_market_order(ticker, 'SELL', shares, current_price)
                            
                            if sell_result['success']:
                                results['removed_trades'].append({
                                    'ticker': ticker,
                                    'action': 'SELL',
                                    'shares': shares,
                                    'price': current_price,
                                    'position_size': sizing_info['position_size'],
                                    'equity_pct': sizing_info['equity_pct'],
                                    'multiplier': sizing_info['multiplier'],
                                    'hold_days': sizing_info['hold_days'],
                                    'leverage': sizing_info['leverage'],
                                    'risk_level': risk_level,
                                    'sizing_type': sizing_info['sizing_type'],
                                    'trend_improving': sizing_info['trend_improving'],
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
            
            # Execute gold hedging if recommended
            if gold_hedging['recommended']:
                try:
                    logger.info(f"🥇 Executing gold hedging: {gold_hedging['reason']}")
                    
                    # Get gold price
                    gold_price = self.get_market_price(gold_hedging['symbol'])
                    if gold_price:
                        # Calculate shares for gold position
                        gold_shares = int(gold_hedging['position_size'] / gold_price)
                        
                        if gold_shares > 0:
                            # Place gold buy order
                            gold_result = self.place_market_order(gold_hedging['symbol'], 'BUY', gold_shares, gold_price)
                            
                            if gold_result['success']:
                                results['gold_hedging']['executed'] = True
                                results['gold_hedging']['shares'] = gold_shares
                                results['gold_hedging']['price'] = gold_price
                                results['gold_hedging']['order_id'] = gold_result.get('order_id')
                                logger.info(f"✅ Gold hedging executed successfully: {gold_shares} shares of {gold_hedging['symbol']}")
                            else:
                                results['gold_hedging']['executed'] = False
                                results['gold_hedging']['error'] = gold_result.get('error', 'Unknown error')
                                logger.error(f"❌ Gold hedging failed: {gold_result.get('error')}")
                        else:
                            logger.warning("⚠️ Gold position size too small")
                    else:
                        logger.error("❌ Could not get gold price")
                        results['gold_hedging']['executed'] = False
                        results['gold_hedging']['error'] = 'Could not get gold price'
                except Exception as e:
                    logger.error(f"❌ Error executing gold hedging: {e}")
                    results['gold_hedging']['executed'] = False
                    results['gold_hedging']['error'] = str(e)
            
            logger.info(f"✅ Enhanced risk-aware trade execution complete: {results['successful_trades']}/{results['total_trades']} successful")
            logger.info(f"📊 Risk Level: {risk_level}, Risk Score: {results['risk_score']:.3f}")
            if gold_hedging['recommended']:
                logger.info(f"🥇 Gold Hedging: {'Executed' if results['gold_hedging'].get('executed') else 'Failed'}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error executing enhanced risk-aware trades: {e}")
            return {'success': False, 'error': str(e)}
    
    def _continuous_news_monitoring(self):
        """Continuously monitor for news with enhanced risk-aware trading"""
        logger.info("📰 Starting continuous enhanced risk-aware news monitoring...")
        
        while self.running:
            try:
                current_time = datetime.now()
                logger.info(f"⏰ {current_time.strftime('%H:%M:%S')} - Checking for S&P 500 news...")
                
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
                            
                            # Execute enhanced risk-aware trades
                            trade_results = self.execute_enhanced_risk_aware_trades(event)
                            
                            if trade_results['successful_trades'] > 0:
                                logger.info(f"💰 Successfully executed {trade_results['successful_trades']} enhanced risk-aware trades")
                            else:
                                logger.warning("⚠️ No trades were executed successfully")
                else:
                    logger.info("📰 No S&P 500 news events detected")
                
                # Wait for next check
                time.sleep(self.news_check_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in news monitoring: {e}")
                time.sleep(10)  # Brief pause on error, then continue
    
    def start_enhanced_risk_aware_trading(self):
        """Start enhanced risk-aware trading with historical analysis and gold hedging"""
        logger.info("🚀 Starting Enhanced Risk-Aware S&P 500 Trading V2")
        logger.info("=" * 80)
        logger.info("🎯 ENHANCED FEATURES ENABLED!")
        logger.info("📊 Historical risk analysis (2 months comparison)")
        logger.info("📈 Trend-based position sizing (125% long, 50% short for improving trends)")
        logger.info("🥇 Enhanced gold hedging with specific risk thresholds")
        logger.info("📰 Continuous news monitoring every 30 seconds")
        logger.info("🔌 Automatic connection monitoring")
        
        # Connect to IBKR
        if not self.connect_to_ibkr():
            logger.error("❌ Cannot start trading without IBKR connection")
            return
        
        self.running = True
        
        try:
            # Start news monitoring thread
            news_thread = threading.Thread(target=self._continuous_news_monitoring, daemon=True)
            news_thread.start()
            
            logger.info("✅ Enhanced risk-aware trading started successfully")
            logger.info("🎯 Bot is now running with historical analysis and gold hedging!")
            
            # Keep main thread alive
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("🛑 Enhanced risk-aware trading stopped by user")
        except Exception as e:
            logger.error(f"❌ Error in enhanced risk-aware trading: {e}")
        finally:
            self.running = False
            self.disconnect()
    
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
    """Main function to start the enhanced risk-aware trading bot V2"""
    print("🚀 ENHANCED RISK-AWARE IBKR TRADING BOT V2")
    print("=" * 80)
    print("🎯 ENHANCED FEATURES ENABLED!")
    print("📊 Historical risk analysis (2 months comparison)")
    print("📈 Trend-based position sizing (125% long, 50% short for improving trends)")
    print("🥇 Enhanced gold hedging with specific risk thresholds")
    print("📰 Continuous news monitoring every 30 seconds")
    print("🔌 Automatic connection monitoring")
    
    # Initialize bot
    bot = EnhancedRiskAwareBotV2(starting_capital=100000)
    
    try:
        # Start enhanced risk-aware trading
        bot.start_enhanced_risk_aware_trading()
    except KeyboardInterrupt:
        print("\n🛑 Enhanced risk-aware trading stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Disconnect
        bot.disconnect()
        print("\n🔌 Disconnected from TWS")

if __name__ == "__main__":
    main()
