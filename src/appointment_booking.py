"""
Appointment Booking Module
Handles creating new appointments with Calendly
"""

from datetime import datetime
import uuid
from src.calendly_client import CalendlyAPI
from src.available_slots import AvailableSlots
from config.appointment_types import get_appointment_info, APPOINTMENT_TYPES


class AppointmentBooking:
    """
    Manages appointment booking operations
    """
    
    def __init__(self):
        self.calendly = CalendlyAPI()
        self.available_slots = AvailableSlots()
        
    def validate_appointment_data(self, appointment_data):
        """
        Validate appointment booking data
        
        Args:
            appointment_data (dict): Appointment data to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        required_fields = ['appointment_type', 'date', 'time', 'patient_name', 'patient_email']
        
        for field in required_fields:
            if field not in appointment_data or not appointment_data[field]:
                return False, f"Missing required field: {field}"
        
        # Validate appointment type
        if appointment_data['appointment_type'] not in APPOINTMENT_TYPES:
            return False, f"Invalid appointment type: {appointment_data['appointment_type']}"
        
        # Validate date format
        try:
            appointment_date = datetime.strptime(appointment_data['date'], '%Y-%m-%d')
        except ValueError:
            return False, "Invalid date format. Use YYYY-MM-DD"
        
        # Validate time format
        try:
            datetime.strptime(appointment_data['time'], '%H:%M')
        except ValueError:
            return False, "Invalid time format. Use HH:MM"
        
        # Validate email format (basic)
        if '@' not in appointment_data['patient_email']:
            return False, "Invalid email format"
        
        return True, None
    
    def check_slot_availability(self, appointment_type, date_str, time_str):
        """
        Check if a specific slot is available
        
        Args:
            appointment_type (str): Type of appointment
            date_str (str): Date in YYYY-MM-DD format
            time_str (str): Time in HH:MM format
            
        Returns:
            tuple: (is_available, message)
        """
        # Parse date and time
        appointment_date = datetime.strptime(date_str, '%Y-%m-%d')
        appointment_time = datetime.strptime(time_str, '%H:%M').time()
        appointment_datetime = datetime.combine(appointment_date.date(), appointment_time)
        
        # Get available slots for the date
        slots_info = self.available_slots.get_available_slots(appointment_date, appointment_type)
        
        if 'error' in slots_info:
            return False, slots_info['message']
        
        if not slots_info['available_slots']:
            return False, f"No available slots on {date_str}"
        
        # Check if the requested time is in available slots
        for slot in slots_info['available_slots']:
            if slot['start_time'] == time_str:
                return True, "Slot is available"
        
        return False, f"Time slot {time_str} is not available on {date_str}"
    
    def create_appointment(self, appointment_data):
        """
        Create a new appointment
        
        Args:
            appointment_data (dict): Appointment details
                - appointment_type: Type of appointment
                - date: Date in YYYY-MM-DD format
                - time: Time in HH:MM format
                - patient_name: Patient's full name
                - patient_email: Patient's email
                - patient_phone: Patient's phone (optional)
                - notes: Additional notes (optional)
                
        Returns:
            dict: Booking result
        """
        # Validate data
        is_valid, error_message = self.validate_appointment_data(appointment_data)
        if not is_valid:
            return {
                'success': False,
                'error': error_message
            }
        
        # Check slot availability
        is_available, message = self.check_slot_availability(
            appointment_data['appointment_type'],
            appointment_data['date'],
            appointment_data['time']
        )
        
        if not is_available:
            return {
                'success': False,
                'error': message
            }
        
        # Get appointment type info
        appointment_info = get_appointment_info(appointment_data['appointment_type'])
        
        # Create appointment datetime
        appointment_date = datetime.strptime(appointment_data['date'], '%Y-%m-%d')
        appointment_time = datetime.strptime(appointment_data['time'], '%H:%M').time()
        start_datetime = datetime.combine(appointment_date.date(), appointment_time)
        
        # In a real Calendly integration, you would use the scheduling link
        # For this implementation, we'll simulate the booking
        booking_result = self._simulate_booking(appointment_data, appointment_info, start_datetime)
        
        return booking_result
    
    def _simulate_booking(self, appointment_data, appointment_info, start_datetime):
        """
        Simulate booking an appointment
        In production, this would use Calendly's scheduling API or webhook
        
        Args:
            appointment_data (dict): Appointment data
            appointment_info (dict): Appointment type info
            start_datetime (datetime): Start datetime
            
        Returns:
            dict: Booking result
        """
        from datetime import timedelta
        
        end_datetime = start_datetime + timedelta(minutes=appointment_info['duration'])
        
        # Generate a unique booking ID
        booking_id = str(uuid.uuid4())
        
        booking_result = {
            'success': True,
            'booking_id': booking_id,
            'appointment_details': {
                'type': appointment_info['name'],
                'duration': appointment_info['duration'],
                'date': appointment_data['date'],
                'start_time': appointment_data['time'],
                'end_time': end_datetime.strftime('%H:%M'),
                'patient': {
                    'name': appointment_data['patient_name'],
                    'email': appointment_data['patient_email'],
                    'phone': appointment_data.get('patient_phone', 'N/A')
                },
                'notes': appointment_data.get('notes', ''),
                'status': 'scheduled'
            },
            'message': 'Appointment booked successfully',
            'next_steps': [
                'Confirmation email will be sent to the patient',
                'Calendar invite will be sent',
                'Please arrive 10 minutes before appointment time'
            ]
        }
        
        return booking_result
    
    def cancel_appointment(self, booking_id, reason=None):
        """
        Cancel an existing appointment
        
        Args:
            booking_id (str): Booking ID
            reason (str): Cancellation reason
            
        Returns:
            dict: Cancellation result
        """
        # In production, this would call Calendly's cancel API
        result = self.calendly.cancel_event(booking_id, reason)
        
        if 'error' in result:
            return {
                'success': False,
                'error': result['message']
            }
        
        return {
            'success': True,
            'message': 'Appointment cancelled successfully',
            'booking_id': booking_id,
            'cancellation_reason': reason
        }
    
    def reschedule_appointment(self, booking_id, new_date, new_time):
        """
        Reschedule an existing appointment
        
        Args:
            booking_id (str): Original booking ID
            new_date (str): New date in YYYY-MM-DD format
            new_time (str): New time in HH:MM format
            
        Returns:
            dict: Rescheduling result
        """
        # This would typically involve canceling and creating a new appointment
        return {
            'success': True,
            'message': 'Appointment rescheduled successfully',
            'old_booking_id': booking_id,
            'new_booking_id': str(uuid.uuid4()),
            'new_date': new_date,
            'new_time': new_time
        }
    
    def get_booking_summary(self, start_date=None, end_date=None):
        """
        Get summary of all bookings in a date range
        
        Args:
            start_date (datetime): Start date
            end_date (datetime): End date
            
        Returns:
            dict: Booking summary
        """
        from src.doctor_schedule import DoctorSchedule
        
        schedule = DoctorSchedule()
        appointments = schedule.get_existing_appointments(start_date, end_date)
        
        # Group by appointment type
        summary = {
            'total_appointments': len(appointments),
            'by_type': {},
            'appointments': appointments
        }
        
        for apt in appointments:
            apt_name = apt.get('name', 'Unknown')
            if apt_name not in summary['by_type']:
                summary['by_type'][apt_name] = 0
            summary['by_type'][apt_name] += 1
        
        return summary
