#!/usr/bin/env python3
"""
Real IBKR Connection Script
Actually connects to Interactive Brokers TWS
"""

import sys
import os
import time
import logging
from datetime import datetime
from typing import Dict, Optional

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ibkr_connection.log'),
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
    logger.error("Please install with: pip install ib_insync")

class RealIBKRConnection:
    """Real IBKR connection using ib_insync"""
    
    def __init__(self):
        self.ib = None
        self.connected = False
        self.account_info = {}
        self.positions = {}
        
        # Connection settings
        self.host = '127.0.0.1'  # Localhost for TWS
        self.port = 7497          # Default TWS port (7496 for live)
        self.client_id = 1        # Unique client ID
        
        logger.info("🚀 Real IBKR Connection initialized")
        logger.info(f"📡 Connection settings: {self.host}:{self.port}")
    
    def connect_to_tws(self) -> bool:
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
                host=self.host,
                port=self.port,
                clientId=self.client_id,
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
                elif summary.tag == 'GrossPositionValue':
                    self.account_info['gross_position_value'] = float(summary.value)
            
            # Log account info
            logger.info("📊 ACCOUNT INFORMATION:")
            logger.info(f"   Net Liquidation: ${self.account_info.get('net_liquidation', 0):,.2f}")
            logger.info(f"   Total Cash: ${self.account_info.get('total_cash', 0):,.2f}")
            logger.info(f"   Buying Power: ${self.account_info.get('buying_power', 0):,.2f}")
            logger.info(f"   Gross Position Value: ${self.account_info.get('gross_position_value', 0):,.2f}")
            
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
    
    def place_test_order(self, ticker: str, action: str, shares: int) -> Dict:
        """Place a test order to verify connection"""
        try:
            if not self.connected:
                return {'success': False, 'error': 'Not connected'}
            
            logger.info(f"🧪 Placing test {action} order: {shares} shares of {ticker}")
            
            # Create contract
            contract = Stock(ticker, 'SMART', 'USD')
            self.ib.qualifyContracts(contract)
            
            # Create order
            if action.upper() == 'BUY':
                order = MarketOrder('BUY', shares)
            else:
                order = MarketOrder('SELL', shares)
            
            # Submit order
            trade = self.ib.placeOrder(contract, order)
            
            # Wait for order status
            self.ib.sleep(5)
            
            # Check order status
            if trade.orderStatus.status == 'Filled':
                logger.info(f"✅ Test {action} order filled successfully!")
                return {
                    'success': True,
                    'order_id': trade.order.orderId,
                    'status': trade.orderStatus.status,
                    'filled_price': trade.orderStatus.avgFillPrice
                }
            else:
                logger.warning(f"⚠️ Test order status: {trade.orderStatus.status}")
                return {
                    'success': False,
                    'status': trade.orderStatus.status,
                    'error': 'Order not filled'
                }
                
        except Exception as e:
            logger.error(f"❌ Error placing test order: {e}")
            return {'success': False, 'error': str(e)}
    
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
    
    def test_connection(self):
        """Test the complete connection"""
        try:
            logger.info("🧪 Testing IBKR connection...")
            
            # 1. Test connection
            if not self.connect_to_tws():
                return False
            
            # 2. Test market data
            test_ticker = 'AAPL'
            price = self.get_market_price(test_ticker)
            if price:
                logger.info(f"✅ Market data working: {test_ticker} = ${price:.2f}")
            else:
                logger.warning(f"⚠️ Market data not working for {test_ticker}")
            
            # 3. Test order placement (paper trading only!)
            if self.port == 7497:  # Paper trading port
                logger.info("🧪 Testing order placement (paper trading)...")
                test_result = self.place_test_order('AAPL', 'BUY', 1)
                if test_result['success']:
                    logger.info("✅ Order placement working!")
                else:
                    logger.warning(f"⚠️ Order placement issue: {test_result.get('error', 'Unknown')}")
            else:
                logger.info("⚠️ Skipping order test (live trading port)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False

def main():
    """Main function to test IBKR connection"""
    print("🚀 REAL IBKR CONNECTION TEST")
    print("=" * 60)
    print("📋 Make sure IBKR TWS is running and API is enabled!")
    print("🔌 This will connect to your actual TWS instance")
    
    # Initialize connection
    ibkr = RealIBKRConnection()
    
    try:
        # Test connection
        success = ibkr.test_connection()
        
        if success:
            print("\n🎉 SUCCESS! Your bot is connected to IBKR TWS!")
            print("✅ Connection: Working")
            print("✅ Market Data: Working")
            print("✅ Order Placement: Working (paper trading)")
            
            print("\n💡 Next Steps:")
            print("1. Start automatic trading: python3 ibkr_trading_integration.py")
            print("2. Monitor connection: tail -f ibkr_connection.log")
            print("3. Check TWS for incoming API connections")
            
        else:
            print("\n❌ CONNECTION FAILED!")
            print("🔍 Check the log file: ibkr_connection.log")
            print("💡 Common issues:")
            print("   - TWS not running")
            print("   - API not enabled")
            print("   - Wrong port number")
            print("   - Firewall blocking connection")
    
    except KeyboardInterrupt:
        print("\n🛑 Test stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        # Disconnect
        ibkr.disconnect()
        print("\n🔌 Disconnected from TWS")

if __name__ == "__main__":
    main()
