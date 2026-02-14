import streamlit as st
import pandas as pd
import requests
import os
from twilio.rest import Client
from pydexcom import Dexcom, DexcomError
from models.models import User, GlucoseReading
from datetime import datetime, timedelta
from utils.nightscout_api import NightscoutAPI
from utils.data_processor import DataProcessor
from utils.db_utils import DatabaseManager
from utils.alert_manager import AlertManager
from components.glucose_display import display_current_glucose
from components.trends import plot_glucose_trend
from components.statistics import display_statistics, plot_distribution
from components.manual_entry import manual_entry_form
from models.base import get_db

st.set_page_config(
    page_title="Diabetes Management Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load custom CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def initialize_session_state():
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'time_range' not in st.session_state:
        st.session_state.time_range = 24
    if 'phone_number' not in st.session_state:
        st.session_state.phone_number = None
    if 'enable_alerts' not in st.session_state:
        st.session_state.enable_alerts = False
    if 'high_threshold' not in st.session_state:
        st.session_state.high_threshold = 180
    if 'low_threshold' not in st.session_state:
        st.session_state.low_threshold = 70

def validate_email(email):
    """Simple email validation"""
    if '@' in email and '.' in email:
        return True
    return False

def validate_phone(phone):
    """Simple phone number validation"""
    # Remove spaces, dashes, and parentheses
    clean_phone = ''.join(c for c in phone if c.isdigit() or c == '+')
    # Must have at least 10 digits and start with + or a digit
    if len(clean_phone) >= 10 and (clean_phone[0].isdigit() or clean_phone[0] == '+'):
        return True
    return False



def main():
    initialize_session_state()
    st.title("Diabetes Management Dashboard")

    # Sidebar configuration
    st.sidebar.title("Settings")

    
    # User login/setup with improved guidance
    user_email = st.sidebar.text_input(
        "Email Address",
        help="Enter your personal email address (e.g., yourname@gmail.com). This will be used to save your data and preferences."
    )

    if user_email and not validate_email(user_email):
        st.sidebar.error("Please enter a valid email address")
        return
        
    phone_number = st.sidebar.text_input(
        "Phone Number",
        help="Enter your phone number for alerts and notifications (e.g., +1234567890)"
    )
    
    # Validate and store phone number in session state
    if phone_number:
        if validate_phone(phone_number):
            st.session_state.phone_number = phone_number
            st.sidebar.success("✅ Phone number saved for alerts")
        else:
            st.sidebar.error("Please enter a valid phone number (must include area code)")
            st.session_state.phone_number = None

    nightscout_url = st.sidebar.text_input(
        "Nightscout URL",
        value="https://your-nightscout-url.herokuapp.com",
        help="Enter your Nightscout URL. Don't have one? Click the button below for setup instructions."
    )

    time_range = st.sidebar.selectbox(
        "Time Range",
        options=[6, 12, 24, 48],
        index=2,
        help="Select time range in hours"
    )
    st.session_state.time_range = time_range

    # Add SMS Alert settings if phone number is valid
    if st.session_state.phone_number:
        st.sidebar.markdown("---")
        st.sidebar.subheader("SMS Alert Settings")
        
        # Enable/disable alerts
        enable_alerts = st.sidebar.checkbox(
            "Enable SMS Alerts", 
            value=st.session_state.enable_alerts,
            help="Receive SMS alerts when glucose levels are outside target range"
        )
        st.session_state.enable_alerts = enable_alerts
        
        if enable_alerts:
            # Alert thresholds
            col1, col2 = st.sidebar.columns(2)
            with col1:
                low_threshold = st.number_input(
                    "Low Alert (mg/dL)",
                    min_value=40,
                    max_value=100,
                    value=st.session_state.low_threshold,
                    step=5,
                    help="Alert when glucose falls below this level"
                )
                st.session_state.low_threshold = low_threshold
            
            with col2:
                high_threshold = st.number_input(
                    "High Alert (mg/dL)",
                    min_value=120,
                    max_value=300,
                    value=st.session_state.high_threshold,
                    step=5,
                    help="Alert when glucose rises above this level"
                )
                st.session_state.high_threshold = high_threshold
            
            # Check if Twilio is configured
            if not AlertManager.can_send_alerts():
                st.sidebar.warning("⚠️ SMS alerts require Twilio configuration. Please add your Twilio credentials in the settings.")
                
                # Optional Twilio credentials input
                with st.sidebar.expander("Configure Twilio"):
                    st.text_input("Twilio Account SID", key="twilio_sid", type="password")
                    st.text_input("Twilio Auth Token", key="twilio_token", type="password")
                    st.text_input("Twilio Phone Number", key="twilio_number", 
                                 placeholder="+1234567890",
                                 help="Must be a Twilio-provided number")
                    
                    if st.button("Save Twilio Settings"):
                        # Store in environment variables (temporary for this session)
                        os.environ['TWILIO_ACCOUNT_SID'] = st.session_state.twilio_sid
                        os.environ['TWILIO_AUTH_TOKEN'] = st.session_state.twilio_token
                        os.environ['TWILIO_PHONE_NUMBER'] = st.session_state.twilio_number
                        
                        # Twilio settings will be available in the next refresh
                        st.success("Twilio settings saved for this session")
                        st.rerun()

    if st.sidebar.button("Need help setting up Nightscout?"):
        st.sidebar.info("""
        To set up Nightscout:
        1. You'll need a free MongoDB database
        2. A free Heroku account
        3. Your Dexcom Share credentials

        Would you like help setting these up? Just ask!
        """)

    if user_email and nightscout_url:
        try:
            # Get database session
            db = next(get_db())

            # Get or create user
            user = DatabaseManager.get_or_create_user(
                db=db, 
                email=user_email, 
                nightscout_url=nightscout_url, 
                phone_number=st.session_state.phone_number
            )

            if not user:
                st.error("Failed to create or retrieve user")
                return

            st.session_state.user_email = user_email

            # Initialize API client
            api = NightscoutAPI(nightscout_url)

            # Fetch and store current glucose
            current_glucose = api.get_current_glucose()

            if current_glucose:
                try:
                    # Pass the whole user object to avoid ID issues
                    DatabaseManager.save_glucose_reading(
                        db=db,
                        user=user,
                        glucose_value=float(current_glucose['sgv']),
                        timestamp=datetime.fromtimestamp(current_glucose['date'] / 1000),
                        source='nightscout'
                    )
                except Exception as e:
                    st.warning(f"Could not save current glucose reading: {str(e)}")

            # Main content area
            col1, col2 = st.columns([2, 1])

            with col1:
                display_current_glucose(current_glucose)
                
                # Get current glucose value
                glucose_value = current_glucose.get('sgv', 0) if current_glucose else 0
                
                # Show advice based on glucose levels, even if alerts are disabled
                if glucose_value > st.session_state.high_threshold:
                    with st.expander("📋 Glucose Management Advice (HIGH)", expanded=True):
                        st.markdown("""
                        ### Your glucose is above your target range
                        
                        Here are some steps you can take to help lower your glucose levels:
                        
                        **Immediate actions:**
                        - Drink water to stay hydrated and help your kidneys flush out excess glucose
                        - Take a brief walk or do light physical activity (if approved by your healthcare provider)
                        - If taking insulin, check with your healthcare provider if an adjustment is needed
                        
                        **Prevention tips:**
                        - Check your carbohydrate intake from recent meals
                        - Monitor for patterns at this time of day
                        - Record any unusual food, activity, or stress in your notes
                        
                        **When to seek help:**
                        - If glucose remains high for several hours
                        - If you experience excessive thirst, frequent urination, fatigue, or blurred vision
                        - If glucose exceeds 250 mg/dL consistently
                        
                        *Always follow your healthcare provider's specific guidance for your diabetes management.*
                        """)
                elif glucose_value < st.session_state.low_threshold:
                    with st.expander("📋 Glucose Management Advice (LOW)", expanded=True):
                        st.markdown("""
                        ### Your glucose is below your target range
                        
                        Here are some steps you can take to raise your glucose levels safely:
                        
                        **Immediate actions:**
                        - Follow the 15-15 rule: Consume 15 grams of fast-acting carbohydrates, wait 15 minutes, then recheck
                        - Examples of 15g carbs: 4 oz fruit juice, 1 tablespoon honey, 3-4 glucose tablets
                        - If still low after 15 minutes, repeat the process
                        
                        **After recovery:**
                        - Eat a small balanced snack with protein once levels normalize (cheese and crackers, nut butter)
                        - Rest and monitor your symptoms
                        - Record the episode in your notes, including what you ate and possible triggers
                        
                        **When to seek help:**
                        - If glucose remains below 70 mg/dL after two treatments
                        - If you experience confusion, difficulty speaking, or inability to swallow
                        - If you lose consciousness (family members should call emergency services)
                        
                        *Always follow your healthcare provider's specific guidance for your diabetes management.*
                        """)
                
                # Check if we need to send alerts based on current glucose
                if (st.session_state.enable_alerts and 
                    (st.session_state.phone_number or user_email) and 
                    current_glucose and 
                    AlertManager.can_send_alerts()):
                    
                    glucose_value = current_glucose.get('sgv', 0)
                    timestamp = datetime.fromtimestamp(current_glucose.get('date', 0) / 1000)
                    
                    # Check for high glucose alert
                    if glucose_value > st.session_state.high_threshold:
                        # Send alerts through both SMS and email
                        phone = st.session_state.phone_number if st.session_state.phone_number else None
                        email = user_email if user_email else None
                        
                        AlertManager.send_glucose_alert(
                            to_number=phone,
                            to_email=email,
                            glucose_value=glucose_value,
                            timestamp=timestamp,
                            alert_type="high"
                        )
                        st.sidebar.warning(f"High glucose alert sent ({glucose_value} mg/dL)")
                    
                    # Check for low glucose alert
                    elif glucose_value < st.session_state.low_threshold:
                        # Send alerts through both SMS and email
                        phone = st.session_state.phone_number if st.session_state.phone_number else None
                        email = user_email if user_email else None
                        
                        AlertManager.send_glucose_alert(
                            to_number=phone,
                            to_email=email,
                            glucose_value=glucose_value,
                            timestamp=timestamp,
                            alert_type="low"
                        )
                        st.sidebar.warning(f"Low glucose alert sent ({glucose_value} mg/dL)")

            # Fetch historical data
            df = api.get_glucose_data(hours=time_range)
            if not df.empty:
                # Store new readings in database
                for _, row in df.iterrows():
                    try:                            
                        DatabaseManager.save_glucose_reading(
                            db=db,
                            user=user,
                            glucose_value=float(row['sgv']),
                            timestamp=datetime.fromtimestamp(row['date'] / 1000),
                            source='nightscout'
                        )
                    except Exception as e:
                        continue  # Skip failed entries but continue processing

                df = DataProcessor.process_glucose_data(df)

                # Display trend chart
                plot_glucose_trend(df)

                # Calculate and display statistics
                stats = DataProcessor.calculate_statistics(df)
                display_statistics(stats)

                # Show distribution
                plot_distribution(df)

            # Manual entry section
            st.markdown("---")
            manual_entry_form(db, user)

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("Please check your settings and try again.")
    else:
        st.info("Please enter your email address and Nightscout URL to get started.")

if __name__ == "__main__":
    main()