# Calendly Doctor Appointment System

A comprehensive Python-based system for integrating with Calendly API to manage doctor appointments with multiple appointment types and dynamic scheduling.

## 📋 Features

### 1. **Calendly Integration**
- Complete API integration with Calendly
- Fetch doctor's schedules and working hours
- Retrieve existing appointments
- Real-time availability checking

### 2. **Doctor Schedule Management**
- View working hours by day
- Check schedule summaries
- Identify busy time slots
- Manage working/non-working days

### 3. **Dynamic Available Time Slots**
- Generate available slots based on:
  - Doctor's working hours
  - Existing appointments
  - Appointment type duration
- Find next available slot
- Check availability for date ranges

### 4. **Appointment Booking**
- Create new appointments
- Validate booking data
- Check slot availability
- Cancel appointments
- Reschedule appointments

### 5. **Appointment Types with Durations**
- **General Consultation**: 30 minutes
- **Follow-up**: 15 minutes
- **Physical Exam**: 45 minutes
- **Specialist Consultation**: 60 minutes

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- Virtual environment (recommended)

### Setup

1. **Clone or download the project**
```bash
cd /home/tester1/assesment
```

2. **Create and activate virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env and add your Calendly API credentials
```

## 📁 Project Structure

```
assesment/
├── venv/                       # Virtual environment
├── config/
│   ├── __init__.py
│   └── appointment_types.py    # Appointment types configuration
├── src/
│   ├── __init__.py
│   ├── calendly_client.py      # Calendly API integration
│   ├── doctor_schedule.py      # Schedule management
│   ├── available_slots.py      # Time slot generation
│   ├── appointment_booking.py  # Booking functionality
│   ├── appointment_type_handler.py  # Type management
│   └── main.py                 # CLI application
├── examples/
│   ├── __init__.py
│   └── demo.py                 # Demo script
├── dashboard.py                # Streamlit web dashboard ⭐
├── run_dashboard.sh            # Dashboard launcher script
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## 🔧 Configuration

### Environment Variables (.env)

```env
CALENDLY_API_TOKEN=your_calendly_api_token_here
CALENDLY_USER_URI=your_calendly_user_uri_here
DOCTOR_NAME=Dr. Smith
DOCTOR_EMAIL=doctor@example.com
```

### Getting Calendly Credentials

1. **API Token**: 
   - Go to Calendly Settings → Integrations → API & Webhooks
   - Generate a Personal Access Token

2. **User URI**:
   - Format: `https://api.calendly.com/users/XXXXXX`
   - Get from API response: `GET https://api.calendly.com/users/me`

## 💻 Usage

### Running the Streamlit Dashboard (Recommended) 🎨

The interactive web dashboard provides the best user experience:

```bash
# Option 1: Using the run script
./run_dashboard.sh

# Option 2: Manual command
source venv/bin/activate
streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501` with features:
- 🏠 **Dashboard**: Overview of appointments and quick stats
- 📅 **Book Appointment**: Interactive booking form with real-time slot availability
- 🔍 **Check Availability**: Search and visualize available time slots
- 📊 **Schedule View**: View working hours and weekly schedule
- ⚙️ **Appointment Types**: Manage and filter appointment types
- 📈 **Analytics**: Trends, distribution, and capacity analysis

### Running the CLI Application

```bash
source venv/bin/activate
python src/main.py
```

This launches an interactive menu with options to:
1. View Appointment Types
2. View Doctor's Schedule
3. Check Available Slots
4. Book New Appointment
5. View Booking Summary
6. Cancel Appointment
7. Find Next Available Slot
8. Exit

### Running the Demo

```bash
source venv/bin/activate
python examples/demo.py
```

The demo showcases all functionalities without requiring Calendly API credentials.

## 📚 API Documentation

### Calendly Client (`src/calendly_client.py`)

```python
from src.calendly_client import CalendlyAPI

client = CalendlyAPI()

# Get user info
user_info = client.get_user_info()

# Get scheduled events
events = client.get_scheduled_events(start_time, end_time)

# Get event types
event_types = client.get_event_types()

# Cancel event
result = client.cancel_event(event_uuid, reason)
```

### Doctor Schedule (`src/doctor_schedule.py`)

```python
from src.doctor_schedule import DoctorSchedule

schedule = DoctorSchedule()

# Get working hours
hours = schedule.get_working_hours()

# Get existing appointments
appointments = schedule.get_existing_appointments(start_date, end_date)

# Get schedule summary
summary = schedule.get_schedule_summary(date)
```

### Available Slots (`src/available_slots.py`)

```python
from src.available_slots import AvailableSlots
from datetime import datetime

slots = AvailableSlots()

# Get available slots for a date
available = slots.get_available_slots(datetime.now(), 'general_consultation')

# Get next available slot
next_slot = slots.get_next_available_slot('follow_up')
```

### Appointment Booking (`src/appointment_booking.py`)

```python
from src.appointment_booking import AppointmentBooking

booking = AppointmentBooking()

# Book appointment
appointment_data = {
    'appointment_type': 'general_consultation',
    'date': '2025-12-15',
    'time': '10:00',
    'patient_name': 'John Doe',
    'patient_email': 'john@example.com'
}

result = booking.create_appointment(appointment_data)
```

### Appointment Types (`config/appointment_types.py`)

```python
from config.appointment_types import get_appointment_duration, APPOINTMENT_TYPES

# Get duration
duration = get_appointment_duration('general_consultation')  # Returns 30

# Get all types
all_types = APPOINTMENT_TYPES
```

## 🎯 Key Features Explained

### 1. Dynamic Slot Generation

The system automatically calculates available time slots by:
- Reading doctor's working hours
- Fetching existing appointments
- Calculating gaps between appointments
- Ensuring sufficient time for appointment type duration

### 2. Appointment Type Management

Four pre-configured appointment types with specific durations:
- Each type has a unique duration
- Slots are generated based on type requirements
- Easy to add new types in `config/appointment_types.py`

### 3. Schedule Conflict Prevention

- Validates slot availability before booking
- Checks for overlapping appointments
- Ensures appointments fit within working hours
- Real-time availability checking

### 4. Comprehensive Validation

- Date and time format validation
- Email format validation
- Appointment type validation
- Working day verification

## 🔍 Example Usage

### Check Available Slots

```python
from src.available_slots import AvailableSlots
from datetime import datetime

slots_manager = AvailableSlots()
date = datetime(2025, 12, 15)

# Get available slots for 30-minute consultation
available = slots_manager.get_available_slots(date, 'general_consultation')

print(f"Available slots: {available['total_slots']}")
for slot in available['available_slots'][:5]:
    print(f"  {slot['start_time']} - {slot['end_time']}")
```

### Book an Appointment

```python
from src.appointment_booking import AppointmentBooking

booking = AppointmentBooking()

appointment_data = {
    'appointment_type': 'physical_exam',
    'date': '2025-12-16',
    'time': '14:00',
    'patient_name': 'Jane Smith',
    'patient_email': 'jane@example.com',
    'patient_phone': '+1234567890',
    'notes': 'Annual physical examination'
}

result = booking.create_appointment(appointment_data)

if result['success']:
    print(f"Booking successful! ID: {result['booking_id']}")
else:
    print(f"Booking failed: {result['error']}")
```

## 🛠️ Customization

### Adding New Appointment Types

Edit `config/appointment_types.py`:

```python
APPOINTMENT_TYPES = {
    "new_type": {
        "name": "New Appointment Type",
        "duration": 20,  # minutes
        "description": "Description here"
    }
}
```

### Modifying Working Hours

Edit `src/doctor_schedule.py` in the `get_working_hours()` method:

```python
working_hours = {
    'monday': {'start': '08:00', 'end': '18:00', 'available': True},
    # ... other days
}
```

## 📝 Testing

Run the demo to test all functionalities:

```bash
python examples/demo.py
```

This will demonstrate:
- Appointment type listing
- Schedule viewing
- Available slot checking
- Appointment booking
- Booking summaries

## 🐛 Troubleshooting

### Common Issues

1. **"Module not found" error**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

2. **Calendly API errors**
   - Check API token is valid
   - Verify user URI is correct
   - Ensure token has required permissions

3. **No available slots**
   - Check working hours configuration
   - Verify date is a working day
   - Ensure appointment duration fits in available time

## 📦 Dependencies

### Core Dependencies
- `requests`: HTTP library for API calls
- `python-dotenv`: Environment variable management
- `pytz`: Timezone handling

### Dashboard Dependencies
- `streamlit`: Interactive web dashboard framework
- `pandas`: Data manipulation and analysis
- `plotly`: Interactive data visualizations

## 🤝 Contributing

To extend the system:

1. Add new modules in `src/`
2. Update configuration in `config/`
3. Add examples in `examples/`
4. Update README documentation

## 📄 License

This project is created for assessment purposes.

## 👥 Support

For issues or questions about the system:
1. Check the documentation above
2. Run the demo to see examples
3. Review the code comments for detailed explanations

## ✅ Assessment Requirements Checklist

- [x] Calendly Integration
  - [x] Fetch doctor's schedule
  - [x] Get working hours
  - [x] Retrieve existing appointments
- [x] Dynamic Available Time Slots
  - [x] Calculate based on schedule
  - [x] Consider appointment durations
  - [x] Real-time availability
- [x] Create New Appointments
  - [x] Book appointments
  - [x] Validate data
  - [x] Check availability
- [x] Appointment Types with Durations
  - [x] General Consultation: 30 minutes
  - [x] Follow-up: 15 minutes
  - [x] Physical Exam: 45 minutes
  - [x] Specialist Consultation: 60 minutes

---

**System Ready for Assessment** ✨
