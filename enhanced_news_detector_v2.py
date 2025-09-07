#!/usr/bin/env python3
"""
Enhanced S&P 500 News Detector V2
Real-time detection of S&P 500 additions and removals with multiple news sources
"""

import requests
import json
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import re
from bs4 import BeautifulSoup
import feedparser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedSP500NewsDetectorV2:
    """Enhanced S&P 500 news detector with multiple sources and reliability scoring"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # News sources configuration - Focused on S&P 500 specific sources
        self.news_sources = {
            'reuters_business': {
                'url': 'https://feeds.reuters.com/reuters/businessNews',
                'reliability': 0.95,
                'keywords': ['S&P 500', 'S&P500', 'Standard & Poor', 'index addition', 'index removal', 'index changes']
            },
            'bloomberg_markets': {
                'url': 'https://feeds.bloomberg.com/markets/news.rss',
                'reliability': 0.98,
                'keywords': ['S&P 500', 'S&P500', 'index changes', 'addition', 'removal']
            },
            'marketwatch_markets': {
                'url': 'https://feeds.marketwatch.com/marketwatch/marketpulse/',
                'reliability': 0.90,
                'keywords': ['S&P 500', 'S&P500', 'index', 'addition', 'removal']
            },
            'yahoo_finance': {
                'url': 'https://feeds.finance.yahoo.com/rss/2.0/headline',
                'reliability': 0.85,
                'keywords': ['S&P 500', 'S&P500', 'index changes']
            }
        }
        
        # S&P 500 ticker patterns - More specific patterns
        self.sp500_patterns = [
            r'\b[A-Z]{2,5}\b',  # Basic ticker pattern (2-5 chars)
            r'\$[A-Z]{2,5}\b',  # Ticker with $ prefix
            r'\([A-Z]{2,5}\)',  # Ticker in parentheses
        ]
        
        # Enhanced context keywords for S&P 500 specific classification
        self.addition_keywords = [
            'added to s&p 500', 'added to s&p500', 'joins s&p 500', 'joins s&p500',
            'enters s&p 500', 'enters s&p500', 'included in s&p 500', 'included in s&p500',
            's&p 500 addition', 's&p500 addition', 'new s&p 500 member', 'new s&p500 member',
            'added to the s&p 500', 'added to the s&p500', 'joins the s&p 500', 'joins the s&p500',
            's&p 500 index addition', 's&p500 index addition', 'index addition', 'index inclusion'
        ]
        
        self.removal_keywords = [
            'removed from s&p 500', 'removed from s&p500', 'leaves s&p 500', 'leaves s&p500',
            'exits s&p 500', 'exits s&p500', 'excluded from s&p 500', 'excluded from s&p500',
            's&p 500 removal', 's&p500 removal', 'dropped from s&p 500', 'dropped from s&p500',
            'removed from the s&p 500', 'removed from the s&p500', 'leaves the s&p 500', 'leaves the s&p500',
            's&p 500 index removal', 's&p500 index removal', 'index removal', 'index exclusion'
        ]
        
        # False positive prevention patterns
        self.false_positive_patterns = [
            's&p 500 futures', 's&p500 futures', 's&p 500 etf', 's&p500 etf',
            's&p 500 options', 's&p500 options', 's&p 500 index fund', 's&p500 index fund',
            's&p 500 correlation', 's&p500 correlation', 's&p 500 performance', 's&p500 performance',
            's&p 500 analysis', 's&p500 analysis', 's&p 500 forecast', 's&p500 forecast',
            's&p 500 prediction', 's&p500 prediction', 's&p 500 outlook', 's&p500 outlook'
        ]
        
        # Cache for recent events to avoid duplicates
        self.recent_events = []
        self.cache_duration = 3600  # 1 hour
        
    def run_detection_cycle(self) -> List[Dict]:
        """Run a complete news detection cycle across all sources"""
        logger.info("🔍 Starting news detection cycle...")
        
        all_events = []
        
        for source_name, source_config in self.news_sources.items():
            try:
                logger.info(f"📰 Checking {source_name}...")
                events = self._detect_from_source(source_name, source_config)
                all_events.extend(events)
                logger.info(f"✅ Found {len(events)} events from {source_name}")
                
            except Exception as e:
                logger.error(f"❌ Error checking {source_name}: {e}")
                continue
        
        # Filter and deduplicate events
        filtered_events = self._filter_and_deduplicate(all_events)
        
        # Enhanced validation for S&P 500 specificity
        validated_events = []
        for event in filtered_events:
            if self.validate_sp500_event(event):
                validated_events.append(event)
            else:
                logger.info(f"🚫 Filtered out non-S&P 500 event: {event['title'][:50]}...")
        
        # Update cache
        self._update_cache(validated_events)
        
        logger.info(f"📊 Total events found: {len(filtered_events)}")
        logger.info(f"✅ Validated S&P 500 events: {len(validated_events)}")
        return validated_events
    
    def _detect_from_source(self, source_name: str, source_config: Dict) -> List[Dict]:
        """Detect S&P 500 events from a specific news source"""
        try:
            # Parse RSS feed
            feed = feedparser.parse(source_config['url'])
            
            events = []
            for entry in feed.entries[:20]:  # Check last 20 entries
                # Check if entry is recent (within last 2 hours)
                if self._is_recent_entry(entry):
                    # Check for S&P 500 keywords
                    if self._contains_sp500_keywords(entry, source_config['keywords']):
                        event = self._extract_event_data(entry, source_name, source_config['reliability'])
                        if event:
                            events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"❌ Error parsing {source_name}: {e}")
            return []
    
    def _is_recent_entry(self, entry) -> bool:
        """Check if entry is recent (within last 2 hours)"""
        try:
            # Parse entry date
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                entry_time = datetime(*entry.published_parsed[:6])
                time_diff = datetime.now() - entry_time
                return time_diff.total_seconds() < 7200  # 2 hours
            return False
        except:
            return False
    
    def _contains_sp500_keywords(self, entry, keywords: List[str]) -> bool:
        """Check if entry contains S&P 500 related keywords with enhanced filtering"""
        text = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
        
        # First check for false positives
        if any(pattern in text for pattern in self.false_positive_patterns):
            return False
        
        # Then check for S&P 500 specific keywords
        return any(keyword.lower() in text for keyword in keywords)
    
    def _extract_event_data(self, entry, source_name: str, reliability: float) -> Optional[Dict]:
        """Extract structured event data from news entry"""
        try:
            title = entry.get('title', '')
            summary = entry.get('summary', '')
            link = entry.get('link', '')
            
            # Parse date
            published_time = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_time = datetime(*entry.published_parsed[:6])
            
            event = {
                'title': title,
                'summary': summary,
                'link': link,
                'source': source_name,
                'reliability': reliability,
                'published_time': published_time,
                'detected_time': datetime.now(),
                'raw_text': f"{title} {summary}"
            }
            
            return event
            
        except Exception as e:
            logger.error(f"❌ Error extracting event data: {e}")
            return None
    
    def _filter_and_deduplicate(self, events: List[Dict]) -> List[Dict]:
        """Filter and deduplicate events"""
        if not events:
            return []
        
        # Sort by reliability and recency
        events.sort(key=lambda x: (x['reliability'], x['published_time'] or datetime.min), reverse=True)
        
        # Remove duplicates based on title similarity
        filtered_events = []
        seen_titles = set()
        
        for event in events:
            title_key = self._normalize_title(event['title'])
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                filtered_events.append(event)
        
        return filtered_events
    
    def _normalize_title(self, title: str) -> str:
        """Normalize title for duplicate detection"""
        return re.sub(r'[^\w\s]', '', title.lower().strip())
    
    def _update_cache(self, events: List[Dict]):
        """Update recent events cache"""
        current_time = datetime.now()
        
        # Add new events to cache
        for event in events:
            event['cached_time'] = current_time
            self.recent_events.append(event)
        
        # Remove old events from cache
        self.recent_events = [
            event for event in self.recent_events
            if (current_time - event['cached_time']).total_seconds() < self.cache_duration
        ]
    
    def _is_sp500_specific_event(self, event: Dict) -> bool:
        """Check if event is specifically about S&P 500 changes with enhanced validation"""
        text = event['raw_text'].lower()
        
        # Must contain S&P 500 reference
        sp500_indicators = ['s&p 500', 's&p500', 'standard & poor', 'spx']
        if not any(indicator in text for indicator in sp500_indicators):
            return False
        
        # Check for false positives first
        if any(pattern in text for pattern in self.false_positive_patterns):
            return False
        
        # Must contain specific S&P 500 change indicators
        addition_indicators = ['added to s&p', 'joins s&p', 'enters s&p', 'included in s&p', 's&p addition', 'index addition', 's&p 500 addition', 's&p500 addition', 'joins the s&p', 'enters the s&p']
        removal_indicators = ['removed from s&p', 'leaves s&p', 'exits s&p', 'excluded from s&p', 's&p removal', 'index removal', 's&p 500 removal', 's&p500 removal', 'leaves the s&p', 'exits the s&p']
        
        has_addition = any(indicator in text for indicator in addition_indicators)
        has_removal = any(indicator in text for indicator in removal_indicators)
        
        # Must have specific change indicators AND contain ticker symbols
        has_change_indicators = has_addition or has_removal
        has_tickers = len(self._extract_sp500_tickers(event)) > 0
        
        return has_change_indicators and has_tickers
    
    def _extract_sp500_tickers(self, event: Dict) -> List[str]:
        """Extract S&P 500 tickers from event text with enhanced validation"""
        text = event['raw_text']
        tickers = []
        
        # Common words to exclude
        excluded_words = {
            'AND', 'THE', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'HAD', 'BY', 'WORD', 'WHAT', 'SOME', 'WE', 'IT', 'IS', 'OR', 'OF', 'TO', 'A', 'IN', 'THAT', 'HE', 'ON', 'AS', 'WITH', 'HIS', 'THEY', 'I', 'AT', 'BE', 'THIS', 'HAVE', 'FROM', 'WERE', 'WHEN', 'YOUR', 'SAID', 'THERE', 'EACH', 'WHICH', 'SHE', 'DO', 'HOW', 'THEIR', 'IF', 'WILL', 'UP', 'OTHER', 'ABOUT', 'OUT', 'MANY', 'THEN', 'THEM', 'THESE', 'SO', 'WOULD', 'MAKE', 'LIKE', 'INTO', 'HIM', 'TIME', 'HAS', 'TWO', 'MORE', 'GO', 'NO', 'WAY', 'COULD', 'MY', 'THAN', 'FIRST', 'BEEN', 'CALL', 'WHO', 'ITS', 'NOW', 'FIND', 'LONG', 'DOWN', 'DAY', 'DID', 'GET', 'COME', 'MADE', 'MAY', 'PART', 'INC', 'CORP', 'LTD', 'LLC', 'CO', 'S', 'P', 'SP', 'SPX', 'INDEX', 'STOCK', 'SHARES', 'TRADING', 'MARKET', 'PRICE', 'VOLUME', 'GAINS', 'LOSSES', 'RISE', 'FALL', 'HIGH', 'LOW', 'OPEN', 'CLOSE', 'YEAR', 'MONTH', 'WEEK', 'DAY', 'TIME', 'DATE', 'NEWS', 'REPORT', 'ANALYSIS', 'UPDATE', 'CHANGE', 'CHANGES', 'ANNOUNCED', 'ANNOUNCEMENT', 'EFFECTIVE', 'IMMEDIATELY', 'FOLLOWING', 'QUARTERLY', 'REVIEW', 'REBALANCING', 'ADDITION', 'REMOVAL', 'JOINS', 'LEAVES', 'ENTERS', 'EXITS', 'INCLUDED', 'EXCLUDED', 'ADDED', 'REMOVED', 'DROPPED', 'REPLACED', 'REPLACEMENT', 'SUBSTITUTION', 'COMMITTEE', 'DOW', 'JONES', 'STANDARD', 'POOR', 'POORS'
        }
        
        # Extract tickers using patterns
        for pattern in self.sp500_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Clean ticker - remove parentheses and $ symbols
                ticker = re.sub(r'[^\w]', '', match.upper())
                # Enhanced validation: must be 2-5 characters and not excluded words
                if (len(ticker) >= 2 and len(ticker) <= 5 and ticker not in excluded_words):
                    tickers.append(ticker)
        
        return list(set(tickers))  # Remove duplicates
    
    def _classify_tickers_by_context(self, event: Dict, tickers: List[str]) -> Tuple[List[str], List[str]]:
        """Classify tickers as added or removed based on context with enhanced validation"""
        text = event['raw_text'].lower()
        
        added_tickers = []
        removed_tickers = []
        
        for ticker in tickers:
            # Find ticker context in text
            ticker_context = self._find_ticker_context(text, ticker.lower())
            
            if ticker_context:
                # Check for specific S&P 500 addition keywords
                addition_score = sum(1 for keyword in self.addition_keywords if keyword in ticker_context)
                removal_score = sum(1 for keyword in self.removal_keywords if keyword in ticker_context)
                
                # Only classify if there's a clear indication
                if addition_score > 0 and removal_score == 0:
                    added_tickers.append(ticker)
                elif removal_score > 0 and addition_score == 0:
                    removed_tickers.append(ticker)
                # If both or neither, don't classify (avoid false positives)
                else:
                    logger.warning(f"⚠️ Ambiguous context for ticker {ticker}: {ticker_context[:100]}...")
        
        return added_tickers, removed_tickers
    
    def _find_ticker_context(self, text: str, ticker: str) -> str:
        """Find the context around a ticker in the text"""
        # Look for ticker in text
        ticker_pos = text.find(ticker)
        if ticker_pos == -1:
            return ""
        
        # Extract context around ticker (50 characters before and after)
        start = max(0, ticker_pos - 50)
        end = min(len(text), ticker_pos + len(ticker) + 50)
        context = text[start:end]
        
        return context
    
    def get_recent_events(self, hours: int = 24) -> List[Dict]:
        """Get recent events from cache"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            event for event in self.recent_events
            if event['detected_time'] > cutoff_time
        ]
    
    def validate_sp500_event(self, event: Dict) -> bool:
        """Enhanced validation to ensure event is truly S&P 500 addition/removal"""
        text = event['raw_text'].lower()
        
        # Must contain S&P 500 reference
        sp500_refs = ['s&p 500', 's&p500', 'standard & poor']
        if not any(ref in text for ref in sp500_refs):
            return False
        
        # Must contain specific change language
        change_phrases = [
            'added to s&p', 'removed from s&p', 'joins s&p', 'leaves s&p',
            'enters s&p', 'exits s&p', 'included in s&p', 'excluded from s&p',
            's&p addition', 's&p removal', 'index addition', 'index removal',
            's&p 500 addition', 's&p500 addition', 's&p 500 removal', 's&p500 removal',
            'joins the s&p', 'leaves the s&p', 'enters the s&p', 'exits the s&p',
            's&p 500 changes', 's&p500 changes', 'index changes'
        ]
        if not any(phrase in text for phrase in change_phrases):
            return False
        
        # Must contain ticker symbols
        tickers = self._extract_sp500_tickers(event)
        if not tickers:
            return False
        
        # Must not be false positive patterns
        if any(pattern in text for pattern in self.false_positive_patterns):
            return False
        
        # Additional validation: check for official announcement language
        official_language = [
            'announced', 'announcement', 'effective', 'replacement', 'substitution',
            'index committee', 's&p dow jones', 'standard & poor\'s'
        ]
        has_official_language = any(phrase in text for phrase in official_language)
        
        # High confidence if official language present, medium confidence otherwise
        return has_official_language or len(tickers) >= 1
    
    def get_event_statistics(self) -> Dict:
        """Get statistics about detected events"""
        if not self.recent_events:
            return {'total_events': 0, 'sources': {}, 'recent_activity': 0, 'validated_events': 0}
        
        # Count by source
        source_counts = {}
        validated_events = 0
        
        for event in self.recent_events:
            source = event['source']
            source_counts[source] = source_counts.get(source, 0) + 1
            
            if self.validate_sp500_event(event):
                validated_events += 1
        
        # Recent activity (last hour)
        recent_cutoff = datetime.now() - timedelta(hours=1)
        recent_activity = len([
            event for event in self.recent_events
            if event['detected_time'] > recent_cutoff
        ])
        
        return {
            'total_events': len(self.recent_events),
            'validated_events': validated_events,
            'sources': source_counts,
            'recent_activity': recent_activity
        }

# Test function
def test_news_detector():
    """Test the news detector"""
    detector = EnhancedSP500NewsDetectorV2()
    
    print("🧪 Testing Enhanced S&P 500 News Detector V2")
    print("=" * 50)
    
    # Run detection cycle
    events = detector.run_detection_cycle()
    
    print(f"📊 Found {len(events)} events")
    
    for i, event in enumerate(events[:5]):  # Show first 5 events
        print(f"\n📰 Event {i+1}:")
        print(f"   Title: {event['title']}")
        print(f"   Source: {event['source']}")
        print(f"   Reliability: {event['reliability']:.2f}")
        print(f"   Published: {event['published_time']}")
    
    # Get statistics
    stats = detector.get_event_statistics()
    print(f"\n📈 Statistics:")
    print(f"   Total Events: {stats['total_events']}")
    print(f"   Recent Activity: {stats['recent_activity']}")
    print(f"   Sources: {stats['sources']}")

if __name__ == "__main__":
    test_news_detector()
