"""
Calendly Doctor Appointment System - Configuration Package
"""

from config.appointment_types import (
    APPOINTMENT_TYPES,
    get_appointment_duration,
    get_all_appointment_types,
    get_appointment_info
)

__all__ = [
    'APPOINTMENT_TYPES',
    'get_appointment_duration',
    'get_all_appointment_types',
    'get_appointment_info'
]
