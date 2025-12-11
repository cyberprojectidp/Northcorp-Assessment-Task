"""
Streamlit Dashboard for Calendly Doctor Appointment System
Interactive web-based dashboard for managing appointments
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.doctor_schedule import DoctorSchedule
from src.available_slots import AvailableSlots
from src.appointment_booking import AppointmentBooking
from src.appointment_type_handler import AppointmentTypeHandler
from config.appointment_types import APPOINTMENT_TYPES

# Page configuration
st.set_page_config(
    page_title="Doctor Appointment System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #e3f2fd 0%, #bbdefb 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'booking_history' not in st.session_state:
    st.session_state.booking_history = []

# Initialize classes
@st.cache_resource
def get_managers():
    return {
        'schedule': DoctorSchedule(),
        'slots': AvailableSlots(),
        'booking': AppointmentBooking(),
        'types': AppointmentTypeHandler()
    }

managers = get_managers()

# Header
st.markdown('<h1 class="main-header">🏥 Doctor Appointment System</h1>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar navigation
st.sidebar.title("📋 Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["🏠 Dashboard", "📅 Book Appointment", "🔍 Check Availability", 
     "📊 Schedule View", "⚙️ Appointment Types", "📈 Analytics"]
)

# ==================== DASHBOARD PAGE ====================
if page == "🏠 Dashboard":
    st.header("Dashboard Overview")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📋 Total Appointment Types",
            value=len(APPOINTMENT_TYPES)
        )
    
    with col2:
        today = datetime.now()
        schedule_summary = managers['schedule'].get_schedule_summary(today)
        st.metric(
            label="📅 Today's Appointments",
            value=schedule_summary['total_appointments']
        )
    
    with col3:
        working_hours = managers['schedule'].get_working_hours()
        working_days = sum(1 for day, hours in working_hours.items() if hours['available'])
        st.metric(
            label="🗓️ Working Days/Week",
            value=working_days
        )
    
    with col4:
        st.metric(
            label="📝 Session Bookings",
            value=len(st.session_state.booking_history)
        )
    
    st.markdown("---")
    
    # Today's Schedule
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 Today's Schedule")
        today_summary = managers['schedule'].get_schedule_summary(datetime.now())
        
        st.write(f"**Date:** {today_summary['date']}")
        st.write(f"**Day:** {today_summary['day_of_week']}")
        
        if today_summary['working_hours'].get('available'):
            st.write(f"**Working Hours:** {today_summary['working_hours']['start']} - {today_summary['working_hours']['end']}")
        else:
            st.info("Not a working day today")
        
        if today_summary['appointments']:
            st.write(f"**Appointments:** {today_summary['total_appointments']}")
            for apt in today_summary['appointments']:
                st.write(f"- {apt['name']} at {apt['start_time']}")
        else:
            st.success("No appointments scheduled for today")
    
    with col2:
        st.subheader("⏰ Next Available Slots")
        
        apt_type = st.selectbox(
            "Select appointment type",
            options=list(APPOINTMENT_TYPES.keys()),
            format_func=lambda x: APPOINTMENT_TYPES[x]['name'],
            key="dashboard_apt_type"
        )
        
        next_slot = managers['slots'].get_next_available_slot(apt_type)
        
        if next_slot['found']:
            st.success("✅ Slot Found!")
            st.write(f"**Date:** {next_slot['date']}")
            st.write(f"**Time:** {next_slot['slot']['start_time']} - {next_slot['slot']['end_time']}")
            st.write(f"**Duration:** {next_slot['duration']} minutes")
        else:
            st.warning(next_slot['message'])
    
    # Weekly overview
    st.markdown("---")
    st.subheader("📆 This Week Overview")
    
    week_data = []
    for i in range(7):
        check_date = datetime.now() + timedelta(days=i)
        is_working = managers['schedule'].is_working_day(check_date)
        week_data.append({
            'Day': check_date.strftime('%A'),
            'Date': check_date.strftime('%Y-%m-%d'),
            'Status': '✅ Working' if is_working else '❌ Off'
        })
    
    df_week = pd.DataFrame(week_data)
    st.dataframe(df_week, use_container_width=True, hide_index=True)

# ==================== BOOK APPOINTMENT PAGE ====================
elif page == "📅 Book Appointment":
    st.header("Book New Appointment")
    
    with st.form("booking_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Appointment Details")
            
            apt_type = st.selectbox(
                "Appointment Type *",
                options=list(APPOINTMENT_TYPES.keys()),
                format_func=lambda x: f"{APPOINTMENT_TYPES[x]['name']} ({APPOINTMENT_TYPES[x]['duration']} min)"
            )
            
            apt_date = st.date_input(
                "Appointment Date *",
                min_value=datetime.now().date(),
                max_value=datetime.now().date() + timedelta(days=90)
            )
            
            # Get available slots for selected date
            check_datetime = datetime.combine(apt_date, datetime.min.time())
            slots_info = managers['slots'].get_available_slots(check_datetime, apt_type)
            
            if slots_info.get('available_slots'):
                time_options = [slot['start_time'] for slot in slots_info['available_slots']]
                apt_time = st.selectbox("Appointment Time *", options=time_options)
            else:
                st.warning("No available slots for this date. Please select another date.")
                apt_time = st.text_input("Time (HH:MM)", value="09:00")
        
        with col2:
            st.subheader("Patient Information")
            
            patient_name = st.text_input("Patient Name *")
            patient_email = st.text_input("Patient Email *")
            patient_phone = st.text_input("Patient Phone")
            notes = st.text_area("Additional Notes")
        
        submitted = st.form_submit_button("📅 Book Appointment", use_container_width=True)
        
        if submitted:
            if not patient_name or not patient_email:
                st.error("Please fill in all required fields (marked with *)")
            else:
                appointment_data = {
                    'appointment_type': apt_type,
                    'date': apt_date.strftime('%Y-%m-%d'),
                    'time': apt_time,
                    'patient_name': patient_name,
                    'patient_email': patient_email,
                    'patient_phone': patient_phone,
                    'notes': notes
                }
                
                result = managers['booking'].create_appointment(appointment_data)
                
                if result['success']:
                    st.success("✅ Appointment Booked Successfully!")
                    
                    # Add to session history
                    st.session_state.booking_history.append({
                        'booking_id': result['booking_id'],
                        'date': apt_date.strftime('%Y-%m-%d'),
                        'time': apt_time,
                        'patient': patient_name,
                        'type': APPOINTMENT_TYPES[apt_type]['name'],
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    
                    # Display booking details
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.write("**Booking Confirmation**")
                    st.write(f"**Booking ID:** {result['booking_id']}")
                    st.write(f"**Patient:** {result['appointment_details']['patient']['name']}")
                    st.write(f"**Type:** {result['appointment_details']['type']}")
                    st.write(f"**Date:** {result['appointment_details']['date']}")
                    st.write(f"**Time:** {result['appointment_details']['start_time']} - {result['appointment_details']['end_time']}")
                    st.write(f"**Duration:** {result['appointment_details']['duration']} minutes")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.balloons()
                else:
                    st.error(f"❌ Booking Failed: {result['error']}")
    
    # Show booking history
    if st.session_state.booking_history:
        st.markdown("---")
        st.subheader("📝 Recent Bookings (This Session)")
        df_history = pd.DataFrame(st.session_state.booking_history)
        st.dataframe(df_history, use_container_width=True, hide_index=True)

# ==================== CHECK AVAILABILITY PAGE ====================
elif page == "🔍 Check Availability":
    st.header("Check Available Time Slots")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Search Parameters")
        
        apt_type = st.selectbox(
            "Appointment Type",
            options=list(APPOINTMENT_TYPES.keys()),
            format_func=lambda x: APPOINTMENT_TYPES[x]['name']
        )
        
        date_range = st.radio(
            "Search Range",
            ["Single Day", "Date Range"]
        )
        
        if date_range == "Single Day":
            check_date = st.date_input(
                "Select Date",
                min_value=datetime.now().date()
            )
            start_date = check_date
            end_date = check_date
        else:
            col_start, col_end = st.columns(2)
            with col_start:
                start_date = st.date_input(
                    "Start Date",
                    min_value=datetime.now().date()
                )
            with col_end:
                end_date = st.date_input(
                    "End Date",
                    min_value=start_date,
                    max_value=start_date + timedelta(days=30)
                )
        
        search_button = st.button("🔍 Search Availability", use_container_width=True)
    
    with col2:
        st.subheader("Available Slots")
        
        if search_button:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.min.time())
            
            if date_range == "Single Day":
                slots_info = managers['slots'].get_available_slots(start_datetime, apt_type)
                
                st.info(f"📅 {slots_info['date']} ({slots_info['day_of_week']})")
                st.write(f"**Appointment Type:** {slots_info['appointment_type']}")
                st.write(f"**Duration:** {slots_info['duration']} minutes")
                st.write(f"**Available Slots:** {slots_info['total_slots']}")
                
                if slots_info['available_slots']:
                    # Create DataFrame for display
                    slots_df = pd.DataFrame(slots_info['available_slots'])
                    st.dataframe(slots_df, use_container_width=True, hide_index=True)
                    
                    # Visualize slots
                    fig = px.scatter(
                        slots_df,
                        x='start_time',
                        y=[1]*len(slots_df),
                        title=f"Available Slots Timeline - {slots_info['date']}",
                        labels={'start_time': 'Time', 'y': ''},
                        height=200
                    )
                    fig.update_yaxes(showticklabels=False)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No available slots for this date")
            else:
                slots_range = managers['slots'].get_available_slots_range(
                    start_datetime, end_datetime, apt_type
                )
                
                if slots_range:
                    summary_data = []
                    for day_slots in slots_range:
                        summary_data.append({
                            'Date': day_slots['date'],
                            'Day': day_slots['day_of_week'],
                            'Available Slots': day_slots['total_slots']
                        })
                    
                    df_summary = pd.DataFrame(summary_data)
                    st.dataframe(df_summary, use_container_width=True, hide_index=True)
                    
                    # Chart
                    fig = px.bar(
                        df_summary,
                        x='Date',
                        y='Available Slots',
                        title='Available Slots Per Day',
                        color='Available Slots',
                        color_continuous_scale='Blues'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No available slots in the selected date range")

# ==================== SCHEDULE VIEW PAGE ====================
elif page == "📊 Schedule View":
    st.header("Doctor's Schedule")
    
    tab1, tab2 = st.tabs(["Working Hours", "Weekly Schedule"])
    
    with tab1:
        st.subheader("⏰ Working Hours Configuration")
        
        working_hours = managers['schedule'].get_working_hours()
        
        schedule_data = []
        for day, hours in working_hours.items():
            schedule_data.append({
                'Day': day.capitalize(),
                'Status': '✅ Working' if hours['available'] else '❌ Off',
                'Start Time': hours.get('start', 'N/A'),
                'End Time': hours.get('end', 'N/A')
            })
        
        df_schedule = pd.DataFrame(schedule_data)
        st.dataframe(df_schedule, use_container_width=True, hide_index=True)
        
        # Visual representation
        working_days = [d['Day'] for d in schedule_data if '✅' in d['Status']]
        fig = go.Figure(data=[
            go.Bar(
                x=working_days,
                y=[1]*len(working_days),
                marker_color='lightblue',
                text=working_days,
                textposition='auto'
            )
        ])
        fig.update_layout(
            title='Working Days',
            yaxis_title='',
            showlegend=False,
            height=300
        )
        fig.update_yaxes(showticklabels=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("📆 Weekly Schedule")
        
        start_date = st.date_input(
            "Week Starting From",
            value=datetime.now().date()
        )
        
        weekly_data = []
        for i in range(7):
            check_date = datetime.combine(start_date, datetime.min.time()) + timedelta(days=i)
            summary = managers['schedule'].get_schedule_summary(check_date)
            
            weekly_data.append({
                'Date': summary['date'],
                'Day': summary['day_of_week'],
                'Working': '✅' if summary['working_hours'].get('available') else '❌',
                'Hours': f"{summary['working_hours'].get('start', 'N/A')} - {summary['working_hours'].get('end', 'N/A')}",
                'Appointments': summary['total_appointments']
            })
        
        df_weekly = pd.DataFrame(weekly_data)
        st.dataframe(df_weekly, use_container_width=True, hide_index=True)

# ==================== APPOINTMENT TYPES PAGE ====================
elif page == "⚙️ Appointment Types":
    st.header("Appointment Types Configuration")
    
    types_list = managers['types'].list_all_types()
    summary = managers['types'].get_types_summary()
    
    # Summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Types", summary['total_types'])
    with col2:
        st.metric("Shortest", f"{summary['shortest_duration']} min")
    with col3:
        st.metric("Longest", f"{summary['longest_duration']} min")
    with col4:
        st.metric("Average", f"{summary['average_duration']:.0f} min")
    
    st.markdown("---")
    
    # Detailed table
    st.subheader("📋 All Appointment Types")
    
    types_df = pd.DataFrame(types_list)
    
    # Color code by duration
    def color_duration(val):
        if val <= 20:
            return 'background-color: #d4edda'
        elif val <= 40:
            return 'background-color: #fff3cd'
        else:
            return 'background-color: #f8d7da'
    
    styled_df = types_df.style.applymap(color_duration, subset=['duration'])
    st.dataframe(types_df, use_container_width=True, hide_index=True)
    
    # Duration chart
    fig = px.bar(
        types_df,
        x='name',
        y='duration',
        title='Appointment Durations',
        labels={'name': 'Appointment Type', 'duration': 'Duration (minutes)'},
        color='duration',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Filter by duration
    st.markdown("---")
    st.subheader("🔍 Filter by Duration")
    
    col1, col2 = st.columns(2)
    with col1:
        min_duration = st.number_input("Minimum Duration (min)", min_value=0, value=0)
    with col2:
        max_duration = st.number_input("Maximum Duration (min)", min_value=0, value=60)
    
    filtered = managers['types'].filter_types_by_duration(min_duration, max_duration)
    
    if filtered:
        st.write(f"Found {len(filtered)} appointment type(s):")
        for apt in filtered:
            st.write(f"- **{apt['name']}**: {apt['duration']} minutes - {apt['description']}")
    else:
        st.info("No appointment types match the filter criteria")

# ==================== ANALYTICS PAGE ====================
elif page == "📈 Analytics":
    st.header("System Analytics")
    
    tab1, tab2, tab3 = st.tabs(["Availability Trends", "Appointment Distribution", "Capacity Analysis"])
    
    with tab1:
        st.subheader("📊 Availability Trends (Next 14 Days)")
        
        # Generate data for next 14 days
        trend_data = []
        today = datetime.now()
        
        for apt_type_key in APPOINTMENT_TYPES.keys():
            for i in range(14):
                check_date = today + timedelta(days=i)
                slots_info = managers['slots'].get_available_slots(check_date, apt_type_key)
                
                trend_data.append({
                    'Date': slots_info['date'],
                    'Type': APPOINTMENT_TYPES[apt_type_key]['name'],
                    'Available Slots': slots_info['total_slots']
                })
        
        df_trends = pd.DataFrame(trend_data)
        
        # Line chart
        fig = px.line(
            df_trends,
            x='Date',
            y='Available Slots',
            color='Type',
            title='Available Slots Over Time',
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("📊 Appointment Type Distribution")
        
        types_list = managers['types'].list_all_types()
        df_types = pd.DataFrame(types_list)
        
        # Pie chart
        fig = px.pie(
            df_types,
            names='name',
            values='duration',
            title='Time Distribution by Appointment Type'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("📊 Daily Capacity Analysis")
        
        capacity_data = []
        working_hours = managers['schedule'].get_working_hours()
        
        for day, hours in working_hours.items():
            if hours['available']:
                start = datetime.strptime(hours['start'], '%H:%M')
                end = datetime.strptime(hours['end'], '%H:%M')
                total_minutes = (end - start).seconds // 60
                
                capacity_data.append({
                    'Day': day.capitalize(),
                    'Total Minutes': total_minutes,
                    'Potential 30-min Slots': total_minutes // 30,
                    'Potential 60-min Slots': total_minutes // 60
                })
        
        df_capacity = pd.DataFrame(capacity_data)
        st.dataframe(df_capacity, use_container_width=True, hide_index=True)
        
        # Bar chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_capacity['Day'],
            y=df_capacity['Potential 30-min Slots'],
            name='30-min Slots'
        ))
        fig.add_trace(go.Bar(
            x=df_capacity['Day'],
            y=df_capacity['Potential 60-min Slots'],
            name='60-min Slots'
        ))
        fig.update_layout(
            title='Daily Appointment Capacity',
            barmode='group',
            xaxis_title='Day',
            yaxis_title='Number of Slots'
        )
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>🏥 Doctor Appointment System | Powered by Calendly API</p>
        <p>Built with Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)
