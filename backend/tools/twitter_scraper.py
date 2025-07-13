"""
Twitter Scraper Tool for CrewAI
Collects real-time market signals from Twitter/X using snscrape
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List
from crewai.tools import BaseTool
import snscrape.modules.twitter as sntwitter


class TwitterScraperTool(BaseTool):
    """Tool for scraping Twitter/X data for market sentiment analysis"""
    
    name: str = "twitter_scraper"
    description: str = "Scrapes Twitter/X for market sentiment and trending topics related to a query"
    
    def _run(self, query: str) -> str:
        """
        Execute the Twitter scraping operation
        
        Args:
            query: Search query for Twitter/X
            
        Returns:
            JSON string with sentiment_score, trending_topics, and events
        """
        try:
            # Rate limiting: max 100 tweets to stay in free tier
            max_tweets = 100
            tweets_data = []
            
            # Create search query with date filter (last 7 days)
            since_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            search_query = f"{query} since:{since_date}"
            
            # Collect tweets
            tweet_count = 0
            for tweet in sntwitter.TwitterSearchScraper(search_query).get_items():
                if tweet_count >= max_tweets:
                    break
                    
                tweets_data.append({
                    'text': tweet.content,
                    'date': tweet.date.isoformat(),
                    'likes': tweet.likeCount,
                    'retweets': tweet.retweetCount,
                    'user_followers': tweet.user.followersCount if tweet.user else 0
                })
                tweet_count += 1
            
            # Analyze sentiment and extract insights
            sentiment_score = self._calculate_sentiment(tweets_data)
            trending_topics = self._extract_trending_topics(tweets_data)
            events = self._identify_events(tweets_data, query)
            
            result = {
                'sentiment_score': sentiment_score,
                'trending_topics': trending_topics,
                'events': events,
                'tweet_count': len(tweets_data),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            return json.dumps(result)
            
        except Exception as e:
            # Error handling with JSON error response
            error_result = {
                'error': str(e),
                'error_type': type(e).__name__,
                'sentiment_score': 0.5,  # Neutral default
                'trending_topics': [],
                'events': [],
                'tweet_count': 0
            }
            return json.dumps(error_result)
    
    def _calculate_sentiment(self, tweets: List[Dict[str, Any]]) -> float:
        """
        Calculate aggregate sentiment score from tweets
        
        Args:
            tweets: List of tweet data
            
        Returns:
            Sentiment score between 0 (negative) and 1 (positive)
        """
        if not tweets:
            return 0.5  # Neutral
        
        # Simple sentiment analysis based on keywords and engagement
        positive_keywords = ['bullish', 'growth', 'increase', 'high demand', 'surge', 'boom', 'up', 'profit']
        negative_keywords = ['bearish', 'decline', 'decrease', 'low demand', 'crash', 'down', 'loss']
        
        sentiment_scores = []
        
        for tweet in tweets:
            text = tweet['text'].lower()
            
            # Count positive and negative keywords
            pos_count = sum(1 for keyword in positive_keywords if keyword in text)
            neg_count = sum(1 for keyword in negative_keywords if keyword in text)
            
            # Weight by engagement
            engagement_weight = 1 + (tweet['likes'] + tweet['retweets']) / 100
            
            # Calculate tweet sentiment
            if pos_count > neg_count:
                score = 0.7 + (0.3 * min(pos_count / 5, 1))
            elif neg_count > pos_count:
                score = 0.3 - (0.3 * min(neg_count / 5, 1))
            else:
                score = 0.5
            
            sentiment_scores.append(score * engagement_weight)
        
        # Calculate weighted average
        total_weight = sum(1 + (tweet['likes'] + tweet['retweets']) / 100 for tweet in tweets)
        weighted_sentiment = sum(sentiment_scores) / total_weight if total_weight > 0 else 0.5
        
        return max(0.0, min(1.0, weighted_sentiment))
    
    def _extract_trending_topics(self, tweets: List[Dict[str, Any]]) -> List[str]:
        """
        Extract trending topics from tweets
        
        Args:
            tweets: List of tweet data
            
        Returns:
            List of trending topics
        """
        if not tweets:
            return []
        
        # Extract hashtags and common phrases
        hashtags = {}
        
        for tweet in tweets:
            text = tweet['text']
            # Find hashtags
            found_hashtags = re.findall(r'#\w+', text)
            
            for hashtag in found_hashtags:
                hashtag_lower = hashtag.lower()
                if hashtag_lower not in hashtags:
                    hashtags[hashtag_lower] = 0
                hashtags[hashtag_lower] += 1
        
        # Sort by frequency and return top 5
        sorted_hashtags = sorted(hashtags.items(), key=lambda x: x[1], reverse=True)
        return [tag[0] for tag in sorted_hashtags[:5]]
    
    def _identify_events(self, tweets: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """
        Identify high-impact events from tweets
        
        Args:
            tweets: List of tweet data
            query: Original search query
            
        Returns:
            List of identified events
        """
        events = []
        
        # Keywords that indicate events
        event_keywords = ['launch', 'release', 'announce', 'event', 'sale', 'discount', 
                         'promotion', 'conference', 'update', 'new', 'coming soon']
        
        seen_events = set()
        
        for tweet in tweets:
            text = tweet['text'].lower()
            
            # Check for event keywords
            for keyword in event_keywords:
                if keyword in text and tweet['likes'] + tweet['retweets'] > 10:
                    # Extract event description (simplified)
                    event_text = text[:100] + '...' if len(text) > 100 else text
                    
                    # Avoid duplicates
                    if event_text not in seen_events:
                        seen_events.add(event_text)
                        
                        events.append({
                            'description': event_text,
                            'impact': 'high' if tweet['likes'] + tweet['retweets'] > 50 else 'medium',
                            'date': tweet['date'],
                            'engagement': tweet['likes'] + tweet['retweets']
                        })
        
        # Sort by engagement and return top 3
        events.sort(key=lambda x: x['engagement'], reverse=True)
        return events[:3]
