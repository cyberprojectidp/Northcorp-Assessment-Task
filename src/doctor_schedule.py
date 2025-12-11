"""
Doctor Schedule Management
Handles fetching and managing doctor's schedules, working hours, and existing appointments
"""

from datetime import datetime, timedelta
import pytz
from src.calendly_client import CalendlyAPI


class DoctorSchedule:
    """
    Manages doctor's schedule including working hours and appointments
    """
    
    def __init__(self):
        self.calendly = CalendlyAPI()
        
    def get_working_hours(self):
        """
        Get doctor's working hours configuration
        In a real implementation, this would come from Calendly availability rules
        
        Returns:
            dict: Working hours by day of week
        """
        # Default working hours (can be customized)
        working_hours = {
            'monday': {'start': '09:00', 'end': '17:00', 'available': True},
            'tuesday': {'start': '09:00', 'end': '17:00', 'available': True},
            'wednesday': {'start': '09:00', 'end': '17:00', 'available': True},
            'thursday': {'start': '09:00', 'end': '17:00', 'available': True},
            'friday': {'start': '09:00', 'end': '17:00', 'available': True},
            'saturday': {'start': '10:00', 'end': '14:00', 'available': True},
            'sunday': {'start': None, 'end': None, 'available': False}
        }
        return working_hours
    
    def get_existing_appointments(self, start_date=None, end_date=None):
        """
        Fetch all existing appointments for the doctor
        
        Args:
            start_date (datetime): Start date for query
            end_date (datetime): End date for query
            
        Returns:
            list: List of existing appointments
        """
        if not start_date:
            start_date = datetime.utcnow()
        if not end_date:
            end_date = start_date + timedelta(days=30)
            
        start_time_str = start_date.isoformat() + 'Z'
        end_time_str = end_date.isoformat() + 'Z'
        
        # Fetch scheduled events from Calendly
        response = self.calendly.get_scheduled_events(
            start_time=start_time_str,
            end_time=end_time_str
        )
        
        if 'error' in response:
            print(f"Error fetching appointments: {response['message']}")
            return []
        
        appointments = []
        if 'collection' in response:
            for event in response['collection']:
                appointment = {
                    'id': event.get('uri', '').split('/')[-1],
                    'name': event.get('name'),
                    'start_time': event.get('start_time'),
                    'end_time': event.get('end_time'),
                    'status': event.get('status'),
                    'location': event.get('location'),
                    'invitees_counter': event.get('invitees_counter', {})
                }
                appointments.append(appointment)
        
        return appointments
    
    def get_schedule_summary(self, date=None):
        """
        Get a comprehensive schedule summary for a specific date
        
        Args:
            date (datetime): Date to get schedule for (default: today)
            
        Returns:
            dict: Schedule summary including working hours and appointments
        """
        if not date:
            date = datetime.now()
            
        day_name = date.strftime('%A').lower()
        working_hours = self.get_working_hours()
        
        # Get appointments for the specific day
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        appointments = self.get_existing_appointments(start_of_day, end_of_day)
        
        summary = {
            'date': date.strftime('%Y-%m-%d'),
            'day_of_week': day_name.capitalize(),
            'working_hours': working_hours.get(day_name, {}),
            'total_appointments': len(appointments),
            'appointments': appointments
        }
        
        return summary
    
    def is_working_day(self, date):
        """
        Check if a specific date is a working day
        
        Args:
            date (datetime): Date to check
            
        Returns:
            bool: True if working day, False otherwise
        """
        day_name = date.strftime('%A').lower()
        working_hours = self.get_working_hours()
        return working_hours.get(day_name, {}).get('available', False)
    
    def get_busy_time_slots(self, date):
        """
        Get all busy (booked) time slots for a specific date
        
        Args:
            date (datetime): Date to check
            
        Returns:
            list: List of busy time slots
        """
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        appointments = self.get_existing_appointments(start_of_day, end_of_day)
        
        busy_slots = []
        for appointment in appointments:
            if appointment['status'] == 'active':
                busy_slots.append({
                    'start': appointment['start_time'],
                    'end': appointment['end_time']
                })
        
        return busy_slots
