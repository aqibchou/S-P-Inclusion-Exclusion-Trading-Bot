#!/usr/bin/env python3
"""
Systemic Risk Detector
Advanced framework for detecting systemic market crises driven by:
- Interconnected financial institutions
- Leverage and derivatives exposure  
- Regulatory and structural vulnerabilities
- Market-wide liquidity crises
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import warnings
import requests
import json
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import networkx as nx

warnings.filterwarnings("ignore")

class SystemicRiskDetector:
    """Advanced systemic risk detection framework"""
    
    def __init__(self):
        self.financial_tickers = [
            'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'AXP', 'USB', 'PNC', 'TFC',
            'COF', 'SCHW', 'BLK', 'CB', 'AON', 'MMC', 'AIG', 'MET', 'PRU', 'ALL',
            'TRV', 'PGR', 'HIG', 'PFG', 'LNC', 'BEN', 'NTRS', 'STT', 'BK', 'STI'
        ]
        
        self.systemic_risk_indicators = {}
        self.correlation_matrix = None
        self.leverage_metrics = {}
        self.liquidity_metrics = {}
        self.regulatory_metrics = {}
        
    def calculate_correlation_network_risk(self, analysis_date, lookback_days=252):
        """Calculate interconnectedness risk through correlation networks"""
        print(f"🔗 Analyzing correlation network risk...")
        
        try:
            # Get data for all financial stocks
            end_date = datetime.strptime(analysis_date, '%Y-%m-%d')
            start_date = end_date - timedelta(days=lookback_days)
            
            # Fetch data for all financial stocks
            financial_data = {}
            for ticker in self.financial_tickers:
                try:
                    stock = yf.Ticker(ticker)
                    data = stock.history(start=start_date, end=end_date)
                    if not data.empty and len(data) > 50:
                        financial_data[ticker] = data['Close'].pct_change().dropna()
                except:
                    continue
            
            if len(financial_data) < 5:
                return None
            
            # Create correlation matrix
            df = pd.DataFrame(financial_data)
            correlation_matrix = df.corr()
            
            # Calculate network metrics
            network_metrics = self._calculate_network_metrics(correlation_matrix)
            
            # Calculate systemic risk indicators
            systemic_indicators = {
                'avg_correlation': correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean(),
                'max_correlation': correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].max(),
                'correlation_std': correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].std(),
                'network_density': network_metrics['density'],
                'network_clustering': network_metrics['clustering'],
                'network_centralization': network_metrics['centralization'],
                'connected_components': network_metrics['connected_components']
            }
            
            self.correlation_matrix = correlation_matrix
            return systemic_indicators
            
        except Exception as e:
            print(f"❌ Error in correlation network analysis: {e}")
            return None
    
    def _calculate_network_metrics(self, correlation_matrix, threshold=0.7):
        """Calculate network topology metrics"""
        try:
            # Create adjacency matrix based on correlation threshold
            adj_matrix = (correlation_matrix.abs() > threshold).astype(int)
            np.fill_diagonal(adj_matrix.values, 0)
            
            # Create network graph
            G = nx.from_pandas_adjacency(adj_matrix)
            
            # Calculate network metrics
            metrics = {
                'density': nx.density(G),
                'clustering': nx.average_clustering(G),
                'centralization': nx.degree_centralization(G),
                'connected_components': nx.number_connected_components(G)
            }
            
            return metrics
            
        except Exception as e:
            return {'density': 0, 'clustering': 0, 'centralization': 0, 'connected_components': 0}
    
    def calculate_leverage_risk_indicators(self, analysis_date):
        """Calculate leverage and derivatives exposure risk"""
        print(f"⚖️ Analyzing leverage and derivatives risk...")
        
        leverage_indicators = {}
        
        # Key leverage metrics to analyze
        leverage_metrics = [
            'debt_to_equity', 'debt_to_assets', 'interest_coverage',
            'current_ratio', 'quick_ratio', 'leverage_ratio'
        ]
        
        for ticker in self.financial_tickers[:10]:  # Analyze top 10 for speed
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                # Extract leverage metrics
                ticker_metrics = {}
                if 'debtToEquity' in info:
                    ticker_metrics['debt_to_equity'] = info['debtToEquity']
                if 'debtToAssets' in info:
                    ticker_metrics['debt_to_assets'] = info['debtToAssets']
                if 'interestCoverage' in info:
                    ticker_metrics['interest_coverage'] = info['interestCoverage']
                if 'currentRatio' in info:
                    ticker_metrics['current_ratio'] = info['currentRatio']
                if 'quickRatio' in info:
                    ticker_metrics['quick_ratio'] = info['quickRatio']
                
                leverage_indicators[ticker] = ticker_metrics
                
            except Exception as e:
                continue
        
        # Calculate aggregate leverage risk
        if leverage_indicators:
            aggregate_metrics = self._calculate_aggregate_leverage_risk(leverage_indicators)
            return aggregate_metrics
        
        return None
    
    def _calculate_aggregate_leverage_risk(self, leverage_data):
        """Calculate aggregate leverage risk metrics"""
        try:
            # Collect all metrics
            debt_to_equity = [data.get('debt_to_equity', 0) for data in leverage_data.values() if data.get('debt_to_equity')]
            debt_to_assets = [data.get('debt_to_assets', 0) for data in leverage_data.values() if data.get('debt_to_assets')]
            interest_coverage = [data.get('interest_coverage', 0) for data in leverage_data.values() if data.get('interest_coverage')]
            current_ratio = [data.get('current_ratio', 0) for data in leverage_data.values() if data.get('current_ratio')]
            
            aggregate_metrics = {
                'avg_debt_to_equity': np.mean(debt_to_equity) if debt_to_equity else 0,
                'max_debt_to_equity': np.max(debt_to_equity) if debt_to_equity else 0,
                'avg_debt_to_assets': np.mean(debt_to_assets) if debt_to_assets else 0,
                'max_debt_to_assets': np.max(debt_to_assets) if debt_to_assets else 0,
                'avg_interest_coverage': np.mean(interest_coverage) if interest_coverage else 0,
                'min_interest_coverage': np.min(interest_coverage) if interest_coverage else 0,
                'avg_current_ratio': np.mean(current_ratio) if current_ratio else 0,
                'min_current_ratio': np.min(current_ratio) if current_ratio else 0,
                'high_leverage_count': len([x for x in debt_to_equity if x > 2.0]),
                'low_coverage_count': len([x for x in interest_coverage if x < 2.5])
            }
            
            return aggregate_metrics
            
        except Exception as e:
            return None
    
    def calculate_liquidity_risk_indicators(self, analysis_date, lookback_days=60):
        """Calculate market-wide liquidity risk"""
        print(f"💧 Analyzing liquidity risk...")
        
        try:
            end_date = datetime.strptime(analysis_date, '%Y-%m-%d')
            start_date = end_date - timedelta(days=lookback_days)
            
            # Key liquidity indicators
            liquidity_indicators = {}
            
            # 1. VIX (Volatility Index) - Market fear indicator
            try:
                vix = yf.Ticker("^VIX")
                vix_data = vix.history(start=start_date, end=end_date)
                if not vix_data.empty:
                    liquidity_indicators['vix_mean'] = vix_data['Close'].mean()
                    liquidity_indicators['vix_max'] = vix_data['Close'].max()
                    liquidity_indicators['vix_volatility'] = vix_data['Close'].std()
            except:
                pass
            
            # 2. Treasury spreads (10Y-2Y, 10Y-3M)
            try:
                tnx = yf.Ticker("^TNX")  # 10-year
                irx = yf.Ticker("^IRX")  # 3-month
                tyx = yf.Ticker("^TYX")  # 30-year
                
                tnx_data = tnx.history(start=start_date, end=end_date)
                irx_data = irx.history(start=start_date, end=end_date)
                
                if not tnx_data.empty and not irx_data.empty:
                    # Align dates
                    common_dates = tnx_data.index.intersection(irx_data.index)
                    if len(common_dates) > 0:
                        spread_10y_3m = tnx_data.loc[common_dates, 'Close'] - irx_data.loc[common_dates, 'Close']
                        liquidity_indicators['yield_spread_mean'] = spread_10y_3m.mean()
                        liquidity_indicators['yield_spread_min'] = spread_10y_3m.min()
                        liquidity_indicators['yield_curve_inversion'] = 1 if spread_10y_3m.min() < 0 else 0
            except:
                pass
            
            # 3. Financial sector volatility
            try:
                xlf = yf.Ticker("XLF")  # Financial sector ETF
                xlf_data = xlf.history(start=start_date, end=end_date)
                if not xlf_data.empty:
                    xlf_returns = xlf_data['Close'].pct_change().dropna()
                    liquidity_indicators['financial_volatility'] = xlf_returns.std() * np.sqrt(252)
                    liquidity_indicators['financial_max_drawdown'] = self._calculate_max_drawdown(xlf_data['Close'])
            except:
                pass
            
            # 4. Credit spreads (if available)
            # This would require additional data sources for corporate bond spreads
            
            return liquidity_indicators
            
        except Exception as e:
            print(f"❌ Error in liquidity analysis: {e}")
            return None
    
    def _calculate_max_drawdown(self, prices):
        """Calculate maximum drawdown"""
        try:
            peak = prices.expanding().max()
            drawdown = (prices - peak) / peak
            return drawdown.min()
        except:
            return 0
    
    def calculate_regulatory_risk_indicators(self, analysis_date):
        """Calculate regulatory and structural vulnerability risk"""
        print(f"🏛️ Analyzing regulatory and structural risk...")
        
        # This would typically involve:
        # 1. Regulatory capital ratios
        # 2. Stress test results
        # 3. Regulatory changes
        # 4. Political risk indicators
        
        # For now, we'll use proxy indicators
        regulatory_indicators = {
            'regulatory_uncertainty': 0.5,  # Placeholder
            'capital_adequacy_risk': 0.3,   # Placeholder
            'political_risk': 0.4,          # Placeholder
            'regulatory_changes': 0.2       # Placeholder
        }
        
        return regulatory_indicators
    
    def calculate_systemic_risk_score(self, analysis_date):
        """Calculate comprehensive systemic risk score"""
        print(f"🚨 Calculating comprehensive systemic risk score...")
        
        # Get all risk indicators
        correlation_risk = self.calculate_correlation_network_risk(analysis_date)
        leverage_risk = self.calculate_leverage_risk_indicators(analysis_date)
        liquidity_risk = self.calculate_liquidity_risk_indicators(analysis_date)
        regulatory_risk = self.calculate_regulatory_risk_indicators(analysis_date)
        
        # Combine into systemic risk score
        systemic_risk_score = 0
        risk_components = {}
        
        # Correlation risk (30% weight)
        if correlation_risk:
            correlation_score = self._score_correlation_risk(correlation_risk)
            systemic_risk_score += correlation_score * 0.3
            risk_components['correlation_risk'] = correlation_score
        
        # Leverage risk (25% weight)
        if leverage_risk:
            leverage_score = self._score_leverage_risk(leverage_risk)
            systemic_risk_score += leverage_score * 0.25
            risk_components['leverage_risk'] = leverage_score
        
        # Liquidity risk (25% weight)
        if liquidity_risk:
            liquidity_score = self._score_liquidity_risk(liquidity_risk)
            systemic_risk_score += liquidity_score * 0.25
            risk_components['liquidity_risk'] = liquidity_score
        
        # Regulatory risk (20% weight)
        if regulatory_risk:
            regulatory_score = self._score_regulatory_risk(regulatory_risk)
            systemic_risk_score += regulatory_score * 0.2
            risk_components['regulatory_risk'] = regulatory_score
        
        # Determine risk level (adjusted thresholds for realistic calibration)
        if systemic_risk_score > 0.5:
            risk_level = "CRITICAL"
        elif systemic_risk_score > 0.42:
            risk_level = "HIGH"
        elif systemic_risk_score > 0.37:
            risk_level = "MEDIUM"
        elif systemic_risk_score > 0.2:
            risk_level = "LOW"
        else:
            risk_level = "MINIMAL"
        
        return {
            'systemic_risk_score': systemic_risk_score,
            'risk_level': risk_level,
            'risk_components': risk_components,
            'correlation_risk': correlation_risk,
            'leverage_risk': leverage_risk,
            'liquidity_risk': liquidity_risk,
            'regulatory_risk': regulatory_risk
        }
    
    def _score_correlation_risk(self, correlation_risk):
        """Score correlation network risk (0-1 scale)"""
        try:
            score = 0
            
            # High average correlation increases risk
            if correlation_risk['avg_correlation'] > 0.8:
                score += 0.4
            elif correlation_risk['avg_correlation'] > 0.6:
                score += 0.3
            elif correlation_risk['avg_correlation'] > 0.4:
                score += 0.2
            
            # High network density increases risk
            if correlation_risk['network_density'] > 0.7:
                score += 0.3
            elif correlation_risk['network_density'] > 0.5:
                score += 0.2
            
            # High centralization increases risk
            if correlation_risk['network_centralization'] > 0.8:
                score += 0.3
            elif correlation_risk['network_centralization'] > 0.6:
                score += 0.2
            
            return min(score, 1.0)
        except:
            return 0
    
    def _score_leverage_risk(self, leverage_risk):
        """Score leverage risk (0-1 scale)"""
        try:
            score = 0
            
            # High debt-to-equity increases risk
            if leverage_risk['avg_debt_to_equity'] > 3.0:
                score += 0.3
            elif leverage_risk['avg_debt_to_equity'] > 2.0:
                score += 0.2
            
            # Low interest coverage increases risk
            if leverage_risk['avg_interest_coverage'] < 2.0:
                score += 0.3
            elif leverage_risk['avg_interest_coverage'] < 3.0:
                score += 0.2
            
            # High leverage count increases risk
            if leverage_risk['high_leverage_count'] > 5:
                score += 0.2
            elif leverage_risk['high_leverage_count'] > 3:
                score += 0.1
            
            # Low coverage count increases risk
            if leverage_risk['low_coverage_count'] > 5:
                score += 0.2
            elif leverage_risk['low_coverage_count'] > 3:
                score += 0.1
            
            return min(score, 1.0)
        except:
            return 0
    
    def _score_liquidity_risk(self, liquidity_risk):
        """Score liquidity risk (0-1 scale)"""
        try:
            score = 0
            
            # High VIX increases risk
            if liquidity_risk.get('vix_mean', 0) > 30:
                score += 0.3
            elif liquidity_risk.get('vix_mean', 0) > 20:
                score += 0.2
            
            # Yield curve inversion increases risk
            if liquidity_risk.get('yield_curve_inversion', 0) == 1:
                score += 0.3
            
            # High financial volatility increases risk
            if liquidity_risk.get('financial_volatility', 0) > 0.4:
                score += 0.2
            elif liquidity_risk.get('financial_volatility', 0) > 0.3:
                score += 0.1
            
            # Large drawdown increases risk
            if liquidity_risk.get('financial_max_drawdown', 0) < -0.2:
                score += 0.2
            elif liquidity_risk.get('financial_max_drawdown', 0) < -0.1:
                score += 0.1
            
            return min(score, 1.0)
        except:
            return 0
    
    def _score_regulatory_risk(self, regulatory_risk):
        """Score regulatory risk (0-1 scale)"""
        try:
            # Simple scoring based on regulatory indicators
            score = sum(regulatory_risk.values()) / len(regulatory_risk)
            return min(score, 1.0)
        except:
            return 0

def run_systemic_risk_analysis(analysis_date="2007-12-15"):
    """Run comprehensive systemic risk analysis"""
    print("🚀 SYSTEMIC RISK DETECTOR")
    print("=" * 70)
    print("📊 Advanced framework for detecting systemic market crises")
    print(f"📅 Analysis Date: {analysis_date}")
    
    detector = SystemicRiskDetector()
    
    # Calculate systemic risk score
    systemic_risk = detector.calculate_systemic_risk_score(analysis_date)
    
    print(f"\n📊 SYSTEMIC RISK ANALYSIS RESULTS")
    print("=" * 50)
    print(f"Systemic Risk Score: {systemic_risk['systemic_risk_score']:.3f}")
    print(f"Risk Level: {systemic_risk['risk_level']}")
    
    print(f"\n📊 RISK COMPONENTS:")
    for component, score in systemic_risk['risk_components'].items():
        print(f"  {component.replace('_', ' ').title()}: {score:.3f}")
    
    # Detailed analysis
    if systemic_risk['correlation_risk']:
        print(f"\n🔗 CORRELATION NETWORK RISK:")
        corr_risk = systemic_risk['correlation_risk']
        print(f"  Average Correlation: {corr_risk['avg_correlation']:.3f}")
        print(f"  Max Correlation: {corr_risk['max_correlation']:.3f}")
        print(f"  Network Density: {corr_risk['network_density']:.3f}")
        print(f"  Network Centralization: {corr_risk['network_centralization']:.3f}")
    
    if systemic_risk['leverage_risk']:
        print(f"\n⚖️ LEVERAGE RISK:")
        lev_risk = systemic_risk['leverage_risk']
        print(f"  Avg Debt-to-Equity: {lev_risk['avg_debt_to_equity']:.2f}")
        print(f"  Max Debt-to-Equity: {lev_risk['max_debt_to_equity']:.2f}")
        print(f"  Avg Interest Coverage: {lev_risk['avg_interest_coverage']:.2f}")
        print(f"  High Leverage Count: {lev_risk['high_leverage_count']}")
        print(f"  Low Coverage Count: {lev_risk['low_coverage_count']}")
    
    if systemic_risk['liquidity_risk']:
        print(f"\n💧 LIQUIDITY RISK:")
        liq_risk = systemic_risk['liquidity_risk']
        if 'vix_mean' in liq_risk:
            print(f"  VIX Mean: {liq_risk['vix_mean']:.2f}")
        if 'yield_spread_mean' in liq_risk:
            print(f"  Yield Spread: {liq_risk['yield_spread_mean']:.2f}")
        if 'yield_curve_inversion' in liq_risk:
            print(f"  Yield Curve Inversion: {'Yes' if liq_risk['yield_curve_inversion'] else 'No'}")
        if 'financial_volatility' in liq_risk:
            print(f"  Financial Volatility: {liq_risk['financial_volatility']:.3f}")
    
    # Risk assessment
    print(f"\n🎯 SYSTEMIC RISK ASSESSMENT:")
    if systemic_risk['risk_level'] in ['CRITICAL', 'HIGH']:
        print(f"  🚨 {systemic_risk['risk_level']} SYSTEMIC RISK DETECTED")
        print(f"  ⚠️  Recommend reducing position sizes and increasing diversification")
        print(f"  📊 Consider hedging strategies and liquidity management")
    elif systemic_risk['risk_level'] == 'MEDIUM':
        print(f"  ⚠️  {systemic_risk['risk_level']} systemic risk - monitor closely")
    else:
        print(f"  ✅ {systemic_risk['risk_level']} systemic risk - normal market conditions")
    
    return systemic_risk

if __name__ == "__main__":
    # Test with December 2007 (pre-crisis)
    run_systemic_risk_analysis("2007-12-15")
