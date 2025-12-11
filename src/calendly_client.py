"""
Calendly API Integration Module
Handles all interactions with Calendly API
"""

import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CalendlyAPI:
    """
    Main class for Calendly API integration
    """
    
    def __init__(self):
        self.api_token = os.getenv('CALENDLY_API_TOKEN')
        self.user_uri = os.getenv('CALENDLY_USER_URI')
        self.base_url = 'https://api.calendly.com'
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
    def _make_request(self, method, endpoint, params=None, data=None):
        """
        Make HTTP request to Calendly API
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint
            params (dict): Query parameters
            data (dict): Request body data
            
        Returns:
            dict: API response or error message
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'error': True,
                'message': str(e),
                'status_code': response.status_code if response else None
            }
    
    def get_user_info(self):
        """
        Get current user information
        
        Returns:
            dict: User information
        """
        return self._make_request('GET', '/users/me')
    
    def get_event_types(self):
        """
        Get all event types for the user
        
        Returns:
            dict: List of event types
        """
        params = {'user': self.user_uri}
        return self._make_request('GET', '/event_types', params=params)
    
    def get_scheduled_events(self, start_time=None, end_time=None, status='active'):
        """
        Get scheduled events (appointments) for the user
        
        Args:
            start_time (str): Start time in ISO format
            end_time (str): End time in ISO format
            status (str): Event status (active, canceled)
            
        Returns:
            dict: List of scheduled events
        """
        if not start_time:
            start_time = datetime.utcnow().isoformat() + 'Z'
        if not end_time:
            end_time = (datetime.utcnow() + timedelta(days=30)).isoformat() + 'Z'
            
        params = {
            'user': self.user_uri,
            'min_start_time': start_time,
            'max_start_time': end_time,
            'status': status
        }
        return self._make_request('GET', '/scheduled_events', params=params)
    
    def get_event_details(self, event_uuid):
        """
        Get details of a specific event
        
        Args:
            event_uuid (str): UUID of the event
            
        Returns:
            dict: Event details
        """
        return self._make_request('GET', f'/scheduled_events/{event_uuid}')
    
    def cancel_event(self, event_uuid, reason=None):
        """
        Cancel a scheduled event
        
        Args:
            event_uuid (str): UUID of the event to cancel
            reason (str): Cancellation reason
            
        Returns:
            dict: Cancellation response
        """
        data = {}
        if reason:
            data['reason'] = reason
            
        return self._make_request('POST', f'/scheduled_events/{event_uuid}/cancellation', data=data)
    
    def get_user_availability(self, event_type_uri, start_date, end_date):
        """
        Get available time slots for a specific event type
        
        Args:
            event_type_uri (str): URI of the event type
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            
        Returns:
            dict: Available time slots
        """
        params = {
            'event_type': event_type_uri,
            'start_time': f"{start_date}T00:00:00Z",
            'end_time': f"{end_date}T23:59:59Z"
        }
        return self._make_request('GET', '/user_availability_schedules', params=params)
