"""
Calendar Collector Tool for CrewAI
Collects high-impact events from Google Calendar for demand forecasting
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from crewai.tools import BaseTool
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class CalendarCollectorTool(BaseTool):
    """Tool for collecting high-impact events from Google Calendar"""
    
    name: str = "calendar_collector"
    description: str = "Collects high-impact events from Google Calendar for demand forecasting"
    
    def __init__(self):
        """Initialize the calendar collector with Google Calendar API credentials"""
        super().__init__()
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self) -> None:
        """Initialize Google Calendar API service"""
        try:
            # Try to use API key from environment
            api_key = os.getenv('GOOGLE_CALENDAR_API_KEY')
            if api_key:
                self.service = build('calendar', 'v3', developerKey=api_key)
            else:
                # Fallback to mock mode if no API key
                print("No Google Calendar API key found, using mock mode")
                self.service = None
        except Exception as e:
            print(f"Failed to initialize Google Calendar service: {e}")
            self.service = None
    
    def _run(self, query: str) -> str:
        """
        Execute the calendar collection operation
        
        Args:
            query: Search query for calendar events
            
        Returns:
            JSON string with high_impact_events, timeline, and demand_forecast
        """
        try:
            if self.service:
                # Use real Google Calendar API
                events = self._fetch_real_events(query)
            else:
                # Use mock events as fallback
                events = self._generate_mock_events(query)
            
            # Process events for demand forecasting
            high_impact_events = self._identify_high_impact_events(events)
            timeline = self._create_event_timeline(events)
            demand_forecast = self._forecast_demand_impact(high_impact_events)
            
            result = {
                'high_impact_events': high_impact_events,
                'timeline': timeline,
                'demand_forecast': demand_forecast,
                'event_count': len(events),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            return json.dumps(result)
            
        except Exception as e:
            # Error handling with JSON error response
            error_result = {
                'error': str(e),
                'error_type': type(e).__name__,
                'high_impact_events': [],
                'timeline': [],
                'demand_forecast': {'impact_score': 0.5, 'confidence': 0.1}
            }
            return json.dumps(error_result)
    
    def _fetch_real_events(self, query: str) -> List[Dict[str, Any]]:
        """
        Fetch real events from Google Calendar API
        
        Args:
            query: Search query for events
            
        Returns:
            List of event dictionaries
        """
        events_list = []
        
        try:
            # Set time range for next 30 days
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'
            time_max = (now + timedelta(days=30)).isoformat() + 'Z'
            
            # Query events
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=50,
                singleEvents=True,
                orderBy='startTime',
                q=query
            ).execute()
            
            events = events_result.get('items', [])
            
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                events_list.append({
                    'summary': event.get('summary', 'No title'),
                    'description': event.get('description', ''),
                    'start': start,
                    'location': event.get('location', ''),
                    'attendees': len(event.get('attendees', [])),
                    'status': event.get('status', 'confirmed')
                })
                
        except HttpError as error:
            print(f"An error occurred: {error}")
            # Return mock events on API error
            return self._generate_mock_events(query)
        
        return events_list
    
    def _generate_mock_events(self, query: str) -> List[Dict[str, Any]]:
        """
        Generate mock events when API is not available
        
        Args:
            query: Search query for events
            
        Returns:
            List of mock event dictionaries
        """
        mock_events = []
        base_date = datetime.now()
        
        # Generate different types of events based on query
        event_templates = [
            {
                'summary': f'Major Product Launch - {query}',
                'description': 'High-impact product launch event expected to drive significant demand',
                'impact': 'high',
                'days_offset': 7
            },
            {
                'summary': f'Industry Conference - {query} Summit',
                'description': 'Annual industry conference with major announcements',
                'impact': 'medium',
                'days_offset': 14
            },
            {
                'summary': f'Seasonal Sale Event - {query}',
                'description': 'Promotional event with expected demand surge',
                'impact': 'high',
                'days_offset': 3
            },
            {
                'summary': f'Marketing Campaign Launch - {query}',
                'description': 'New marketing campaign targeting key demographics',
                'impact': 'medium',
                'days_offset': 10
            },
            {
                'summary': f'Partner Event - {query} Collaboration',
                'description': 'Strategic partnership announcement',
                'impact': 'low',
                'days_offset': 20
            }
        ]
        
        for template in event_templates:
            event_date = base_date + timedelta(days=template['days_offset'])
            mock_events.append({
                'summary': template['summary'],
                'description': template['description'],
                'start': event_date.isoformat(),
                'location': 'Virtual/Online',
                'attendees': 50 if template['impact'] == 'high' else 20,
                'status': 'confirmed',
                'impact': template['impact']
            })
        
        return mock_events
    
    def _identify_high_impact_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify events with high demand impact
        
        Args:
            events: List of calendar events
            
        Returns:
            List of high-impact events
        """
        high_impact_events = []
        
        # Keywords indicating high impact
        high_impact_keywords = ['launch', 'release', 'major', 'annual', 'sale', 'promotion', 
                               'conference', 'summit', 'campaign', 'grand opening']
        
        for event in events:
            summary = event.get('summary', '').lower()
            description = event.get('description', '').lower()
            
            # Calculate impact score
            impact_score = 0
            
            # Check for high-impact keywords
            for keyword in high_impact_keywords:
                if keyword in summary or keyword in description:
                    impact_score += 1
            
            # Consider attendee count
            attendees = event.get('attendees', 0)
            if attendees > 30:
                impact_score += 2
            elif attendees > 10:
                impact_score += 1
            
            # Determine impact level
            if impact_score >= 3:
                impact_level = 'high'
            elif impact_score >= 1:
                impact_level = 'medium'
            else:
                impact_level = 'low'
            
            # Add to high-impact list if significant
            if impact_level in ['high', 'medium']:
                high_impact_events.append({
                    'summary': event['summary'],
                    'date': event['start'],
                    'impact_level': impact_level,
                    'impact_score': impact_score,
                    'description': event.get('description', '')[:200]
                })
        
        # Sort by impact score and date
        high_impact_events.sort(key=lambda x: (-x['impact_score'], x['date']))
        
        return high_impact_events[:5]  # Return top 5
    
    def _create_event_timeline(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create a timeline of events for visualization
        
        Args:
            events: List of calendar events
            
        Returns:
            Timeline data structure
        """
        timeline = []
        
        for event in sorted(events, key=lambda x: x['start'])[:10]:
            timeline.append({
                'date': event['start'],
                'event': event['summary'],
                'type': 'calendar_event'
            })
        
        return timeline
    
    def _forecast_demand_impact(self, high_impact_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Forecast demand impact based on upcoming events
        
        Args:
            high_impact_events: List of high-impact events
            
        Returns:
            Demand forecast with impact score and confidence
        """
        if not high_impact_events:
            return {
                'impact_score': 0.5,
                'confidence': 0.1,
                'peak_periods': [],
                'recommendations': ['No significant events detected']
            }
        
        # Calculate aggregate impact
        total_impact = 0
        peak_periods = []
        
        for event in high_impact_events:
            if event['impact_level'] == 'high':
                total_impact += 0.3
                peak_periods.append({
                    'date': event['date'],
                    'expected_multiplier': 1.5
                })
            elif event['impact_level'] == 'medium':
                total_impact += 0.15
                peak_periods.append({
                    'date': event['date'],
                    'expected_multiplier': 1.25
                })
        
        # Normalize impact score
        impact_score = min(0.9, 0.5 + total_impact)
        
        # Calculate confidence based on number of events
        confidence = min(0.9, 0.3 + (len(high_impact_events) * 0.1))
        
        # Generate recommendations
        recommendations = []
        if impact_score > 0.7:
            recommendations.append('Significant demand increase expected - consider price optimization')
            recommendations.append('Prepare inventory for peak periods')
        elif impact_score > 0.6:
            recommendations.append('Moderate demand increase expected')
            recommendations.append('Monitor market closely during event periods')
        else:
            recommendations.append('Standard demand patterns expected')
        
        return {
            'impact_score': impact_score,
            'confidence': confidence,
            'peak_periods': peak_periods[:3],  # Top 3 peak periods
            'recommendations': recommendations
        }
