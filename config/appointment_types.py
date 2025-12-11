"""
Appointment Types Configuration
Defines different appointment types with their durations
"""

APPOINTMENT_TYPES = {
    "general_consultation": {
        "name": "General Consultation",
        "duration": 30,  # minutes
        "description": "Standard medical consultation"
    },
    "follow_up": {
        "name": "Follow-up",
        "duration": 15,  # minutes
        "description": "Follow-up appointment for previous consultation"
    },
    "physical_exam": {
        "name": "Physical Exam",
        "duration": 45,  # minutes
        "description": "Comprehensive physical examination"
    },
    "specialist_consultation": {
        "name": "Specialist Consultation",
        "duration": 60,  # minutes
        "description": "Detailed consultation with specialist"
    }
}

def get_appointment_duration(appointment_type):
    """
    Get duration for a specific appointment type
    
    Args:
        appointment_type (str): Type of appointment
        
    Returns:
        int: Duration in minutes, or None if type not found
    """
    if appointment_type in APPOINTMENT_TYPES:
        return APPOINTMENT_TYPES[appointment_type]["duration"]
    return None

def get_all_appointment_types():
    """
    Get all available appointment types
    
    Returns:
        dict: Dictionary of all appointment types
    """
    return APPOINTMENT_TYPES

def get_appointment_info(appointment_type):
    """
    Get full information for a specific appointment type
    
    Args:
        appointment_type (str): Type of appointment
        
    Returns:
        dict: Appointment type information or None
    """
    return APPOINTMENT_TYPES.get(appointment_type)
