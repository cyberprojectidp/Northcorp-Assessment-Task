"""
Available Time Slots Module
Dynamically generates available time slots based on doctor's schedule and appointment types
"""

from datetime import datetime, timedelta, time
import pytz
from src.doctor_schedule import DoctorSchedule
from config.appointment_types import get_appointment_duration, APPOINTMENT_TYPES


class AvailableSlots:
    """
    Generates and manages available time slots for appointments
    """
    
    def __init__(self):
        self.doctor_schedule = DoctorSchedule()
        self.slot_interval = 15  # minutes - minimum time slot interval
        
    def parse_time_string(self, time_str):
        """
        Parse time string to time object
        
        Args:
            time_str (str): Time string in HH:MM format
            
        Returns:
            time: Time object
        """
        return datetime.strptime(time_str, '%H:%M').time()
    
    def generate_time_slots(self, start_time, end_time, date, interval=15):
        """
        Generate all possible time slots within a time range
        
        Args:
            start_time (time): Start time
            end_time (time): End time
            date (datetime): Date for the slots
            interval (int): Interval in minutes
            
        Returns:
            list: List of datetime objects representing slots
        """
        slots = []
        current_datetime = datetime.combine(date.date(), start_time)
        end_datetime = datetime.combine(date.date(), end_time)
        
        while current_datetime < end_datetime:
            slots.append(current_datetime)
            current_datetime += timedelta(minutes=interval)
        
        return slots
    
    def is_slot_available(self, slot_start, duration, busy_slots):
        """
        Check if a time slot is available (not overlapping with busy slots)
        
        Args:
            slot_start (datetime): Start time of the slot
            duration (int): Duration in minutes
            busy_slots (list): List of busy time slots
            
        Returns:
            bool: True if available, False otherwise
        """
        slot_end = slot_start + timedelta(minutes=duration)
        
        for busy in busy_slots:
            # Parse busy slot times
            busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
            busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
            
            # Convert to naive datetime for comparison if needed
            if busy_start.tzinfo:
                busy_start = busy_start.replace(tzinfo=None)
            if busy_end.tzinfo:
                busy_end = busy_end.replace(tzinfo=None)
            
            # Check for overlap
            if (slot_start < busy_end and slot_end > busy_start):
                return False
        
        return True
    
    def get_available_slots(self, date, appointment_type):
        """
        Get all available time slots for a specific date and appointment type
        
        Args:
            date (datetime): Date to check availability
            appointment_type (str): Type of appointment
            
        Returns:
            dict: Available slots information
        """
        # Get appointment duration
        duration = get_appointment_duration(appointment_type)
        if not duration:
            return {
                'error': True,
                'message': f'Invalid appointment type: {appointment_type}'
            }
        
        # Check if it's a working day
        if not self.doctor_schedule.is_working_day(date):
            return {
                'date': date.strftime('%Y-%m-%d'),
                'appointment_type': appointment_type,
                'duration': duration,
                'available_slots': [],
                'message': 'Not a working day'
            }
        
        # Get working hours for the day
        day_name = date.strftime('%A').lower()
        working_hours = self.doctor_schedule.get_working_hours()[day_name]
        
        start_time = self.parse_time_string(working_hours['start'])
        end_time = self.parse_time_string(working_hours['end'])
        
        # Generate all possible slots
        all_slots = self.generate_time_slots(start_time, end_time, date, self.slot_interval)
        
        # Get busy slots
        busy_slots = self.doctor_schedule.get_busy_time_slots(date)
        
        # Filter available slots
        available_slots = []
        for slot in all_slots:
            if self.is_slot_available(slot, duration, busy_slots):
                # Make sure the slot end time doesn't exceed working hours
                slot_end = slot + timedelta(minutes=duration)
                if slot_end.time() <= end_time:
                    available_slots.append({
                        'start_time': slot.strftime('%H:%M'),
                        'end_time': slot_end.strftime('%H:%M'),
                        'datetime': slot.isoformat()
                    })
        
        return {
            'date': date.strftime('%Y-%m-%d'),
            'day_of_week': date.strftime('%A'),
            'appointment_type': APPOINTMENT_TYPES[appointment_type]['name'],
            'duration': duration,
            'available_slots': available_slots,
            'total_slots': len(available_slots)
        }
    
    def get_available_slots_range(self, start_date, end_date, appointment_type):
        """
        Get available slots for a date range
        
        Args:
            start_date (datetime): Start date
            end_date (datetime): End date
            appointment_type (str): Type of appointment
            
        Returns:
            list: Available slots for each date in range
        """
        results = []
        current_date = start_date
        
        while current_date <= end_date:
            slots = self.get_available_slots(current_date, appointment_type)
            if slots.get('available_slots'):  # Only include dates with available slots
                results.append(slots)
            current_date += timedelta(days=1)
        
        return results
    
    def get_next_available_slot(self, appointment_type, start_from=None):
        """
        Get the next available slot for an appointment type
        
        Args:
            appointment_type (str): Type of appointment
            start_from (datetime): Start searching from this date (default: now)
            
        Returns:
            dict: Next available slot information
        """
        if not start_from:
            start_from = datetime.now()
        
        # Search for next 30 days
        end_date = start_from + timedelta(days=30)
        
        slots_range = self.get_available_slots_range(start_from, end_date, appointment_type)
        
        if slots_range and slots_range[0]['available_slots']:
            first_day = slots_range[0]
            first_slot = first_day['available_slots'][0]
            return {
                'found': True,
                'date': first_day['date'],
                'slot': first_slot,
                'appointment_type': first_day['appointment_type'],
                'duration': first_day['duration']
            }
        
        return {
            'found': False,
            'message': f'No available slots found in the next 30 days for {appointment_type}'
        }
