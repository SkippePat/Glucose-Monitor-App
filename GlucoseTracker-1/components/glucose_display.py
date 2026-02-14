import streamlit as st
from utils.data_processor import DataProcessor
import datetime

def display_current_glucose(glucose_data):
    """Display current glucose reading with trend arrow"""
    if not glucose_data:
        st.error("⚠️ Unable to fetch current glucose data")
        return

    value = glucose_data.get('sgv', 0)
    direction = glucose_data.get('direction', 'NONE')
    date = glucose_data.get('date', 0)
    
    # Get trend arrow symbol
    trend_arrow = DataProcessor.get_trend_arrow(direction)
    
    # Create a stylish container
    with st.container():
        st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 15px; 
                  box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px;
                  border-left: 8px solid #10b981;">
        """, unsafe_allow_html=True)
        
        # Display the glucose value with large colored text
        if value < 70:
            glucose_class = "glucose-low"
            status_message = "Low Glucose Alert"
            icon = "⚠️"
        elif value > 180:
            glucose_class = "glucose-high"
            status_message = "High Glucose Alert"
            icon = "⚠️"
        else:
            glucose_class = "glucose-normal"
            status_message = "In Range"
            icon = "✅"
        
        # Format the timestamp
        timestamp = datetime.datetime.fromtimestamp(date / 1000).strftime('%I:%M %p') if date else "Unknown"
        
        st.markdown(f"""
        <h2 style="margin-bottom: 5px; color: #10b981;">Current Glucose</h2>
        <div class="main-metric {glucose_class}">{value} mg/dL {trend_arrow}</div>
        <div style="margin-top: 10px; font-size: 1.2rem;">
            <span style="font-weight: bold;">{icon} {status_message}</span>
            <span style="color: #4b5563; margin-left: 15px;">Last updated: {timestamp}</span>
        </div>
        
        <div style="display: flex; margin-top: 15px;">
            <div style="flex: 1; text-align: center; padding: 10px; background: #f0fdf4; border-radius: 8px; margin-right: 10px;">
                <div style="font-size: 0.9rem; color: #4b5563;">Target Range</div>
                <div style="font-weight: bold; color: #10b981;">70-180 mg/dL</div>
            </div>
            <div style="flex: 1; text-align: center; padding: 10px; background: #f0fdf4; border-radius: 8px;">
                <div style="font-size: 0.9rem; color: #4b5563;">Trend</div>
                <div style="font-weight: bold; color: #10b981;">{trend_arrow} {direction}</div>
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)
