"""
Appointment Type Handler
Manages different appointment types and their specific durations
"""

from config.appointment_types import APPOINTMENT_TYPES, get_appointment_duration, get_appointment_info


class AppointmentTypeHandler:
    """
    Handles operations related to appointment types
    """
    
    def __init__(self):
        self.appointment_types = APPOINTMENT_TYPES
    
    def list_all_types(self):
        """
        List all available appointment types
        
        Returns:
            list: List of appointment types with details
        """
        types_list = []
        for key, value in self.appointment_types.items():
            types_list.append({
                'id': key,
                'name': value['name'],
                'duration': value['duration'],
                'description': value['description']
            })
        return types_list
    
    def get_type_by_id(self, type_id):
        """
        Get appointment type information by ID
        
        Args:
            type_id (str): Appointment type ID
            
        Returns:
            dict: Appointment type information or None
        """
        return get_appointment_info(type_id)
    
    def get_duration(self, type_id):
        """
        Get duration for a specific appointment type
        
        Args:
            type_id (str): Appointment type ID
            
        Returns:
            int: Duration in minutes or None
        """
        return get_appointment_duration(type_id)
    
    def display_types_table(self):
        """
        Display appointment types in a formatted table
        
        Returns:
            str: Formatted table string
        """
        header = f"{'Type':<30} {'Duration':<15} {'Description':<50}"
        separator = "-" * 95
        
        rows = [header, separator]
        
        for apt_type in self.list_all_types():
            row = f"{apt_type['name']:<30} {apt_type['duration']} minutes{'':<6} {apt_type['description']:<50}"
            rows.append(row)
        
        return "\n".join(rows)
    
    def validate_type(self, type_id):
        """
        Validate if an appointment type exists
        
        Args:
            type_id (str): Appointment type ID
            
        Returns:
            bool: True if valid, False otherwise
        """
        return type_id in self.appointment_types
    
    def get_types_summary(self):
        """
        Get a summary of all appointment types
        
        Returns:
            dict: Summary information
        """
        types = self.list_all_types()
        total_types = len(types)
        durations = [t['duration'] for t in types]
        
        return {
            'total_types': total_types,
            'shortest_duration': min(durations),
            'longest_duration': max(durations),
            'average_duration': sum(durations) / len(durations),
            'types': types
        }
    
    def filter_types_by_duration(self, min_duration=None, max_duration=None):
        """
        Filter appointment types by duration range
        
        Args:
            min_duration (int): Minimum duration in minutes
            max_duration (int): Maximum duration in minutes
            
        Returns:
            list: Filtered appointment types
        """
        types = self.list_all_types()
        filtered = []
        
        for apt_type in types:
            duration = apt_type['duration']
            if min_duration and duration < min_duration:
                continue
            if max_duration and duration > max_duration:
                continue
            filtered.append(apt_type)
        
        return filtered
    
    def get_type_recommendations(self, available_time):
        """
        Recommend appointment types based on available time
        
        Args:
            available_time (int): Available time in minutes
            
        Returns:
            list: Recommended appointment types
        """
        types = self.list_all_types()
        recommendations = []
        
        for apt_type in types:
            if apt_type['duration'] <= available_time:
                recommendations.append({
                    'type': apt_type,
                    'fits': True,
                    'time_remaining': available_time - apt_type['duration']
                })
        
        # Sort by duration (longest first that fits)
        recommendations.sort(key=lambda x: x['type']['duration'], reverse=True)
        
        return recommendations
