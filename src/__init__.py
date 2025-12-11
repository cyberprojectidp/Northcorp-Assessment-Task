"""
Calendly Doctor Appointment System - Main Package
"""

from src.calendly_client import CalendlyAPI
from src.doctor_schedule import DoctorSchedule
from src.available_slots import AvailableSlots
from src.appointment_booking import AppointmentBooking
from src.appointment_type_handler import AppointmentTypeHandler

__version__ = "1.0.0"
__author__ = "Assessment Project"

__all__ = [
    'CalendlyAPI',
    'DoctorSchedule',
    'AvailableSlots',
    'AppointmentBooking',
    'AppointmentTypeHandler'
]
