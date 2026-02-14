import streamlit as st
import pandas as pd
from datetime import datetime
from utils.db_utils import DatabaseManager
from sqlalchemy.orm import Session

def manual_entry_form(db: Session, user):
    """Form for manual glucose entry with enhanced styling"""
    # Get user ID from user object
    user_id = user.id
    
    # Create a styled container
    st.markdown("""
    <div style="background: white; padding: 20px; border-radius: 15px; 
              box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px;
              border-left: 8px solid #10b981;">
    <h2 style="color: #10b981; margin-bottom: 15px;">Manual Data Entry</h2>
    <p style="color: #4b5563; margin-bottom: 20px;">
        Use this form to manually log glucose readings that aren't captured by your CGM.
    </p>
    """, unsafe_allow_html=True)

    with st.form("manual_entry"):
        # Styled form with columns
        col1, col2 = st.columns(2)
        
        with col1:
            glucose = st.number_input(
                "Glucose Value (mg/dL)", 
                min_value=0, 
                max_value=400, 
                value=100,
                help="Enter your blood glucose reading"
            )
            
            # Show a colored indicator based on the value
            if glucose < 70:
                st.markdown('<p style="color: #eab308; font-weight: 500; margin-top: -15px;">Low</p>', unsafe_allow_html=True)
            elif glucose > 180:
                st.markdown('<p style="color: #ef4444; font-weight: 500; margin-top: -15px;">High</p>', unsafe_allow_html=True)
            else:
                st.markdown('<p style="color: #22c55e; font-weight: 500; margin-top: -15px;">In Range</p>', unsafe_allow_html=True)
        
        with col2:
            date = st.date_input(
                "Date",
                help="Select the date of this reading"
            )
            time = st.time_input(
                "Time", 
                help="Select the time of this reading"
            )
        
        # Notes field
        notes = st.text_area(
            "Notes",
            placeholder="Add any relevant information about this reading (meals, exercise, medication, etc.)",
            help="Optional: Add context about factors affecting this reading"
        )
        
        # Tags selector
        st.markdown('<p style="color: #4b5563; font-size: 0.9rem; margin-bottom: 5px;">Tags (optional)</p>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            meal = st.checkbox("Meal")
        with col2:
            exercise = st.checkbox("Exercise")
        with col3:
            medication = st.checkbox("Medication")
        with col4:
            stress = st.checkbox("Stress")
        
        # Add tags to notes if selected
        tags = []
        if meal: tags.append("#meal")
        if exercise: tags.append("#exercise")
        if medication: tags.append("#medication")
        if stress: tags.append("#stress")
        
        tags_str = " ".join(tags)
        if tags_str and notes:
            notes = f"{notes}\n\nTags: {tags_str}"
        elif tags_str:
            notes = f"Tags: {tags_str}"

        # Styled submit button
        submitted = st.form_submit_button("Save Entry")
        
        if submitted:
            try:
                entry_datetime = datetime.combine(date, time)

                # Save to database
                reading = DatabaseManager.save_glucose_reading(
                    db=db,
                    user=user,
                    glucose_value=glucose,
                    timestamp=entry_datetime,
                    source='manual',
                    notes=notes
                )

                st.success("✅ Entry saved successfully!")
            except Exception as e:
                st.error(f"❌ Error saving entry: {str(e)}")

    # Display manual entries in a styled table
    readings = DatabaseManager.get_user_readings(db, user_id, hours=24)
    if readings:
        st.markdown("""
        <h3 style="color: #10b981; margin-top: 20px; margin-bottom: 15px;">Recent Entries</h3>
        """, unsafe_allow_html=True)

        # Convert to DataFrame
        df = pd.DataFrame([{
            'datetime': r.timestamp,
            'glucose': r.glucose_value,
            'source': r.source,
            'notes': r.notes
        } for r in readings])
        
        # Style the dataframe
        df_styled = df.copy()
        df_styled['datetime'] = df_styled['datetime'].dt.strftime('%Y-%m-%d %I:%M %p')
        # Filter to only show manual entries
        manual_entries = df_styled[df_styled['source'] == 'manual']
        
        if not manual_entries.empty:
            # Apply color formatting based on glucose values
            def color_glucose(val):
                if val < 70:
                    return f'background-color: rgba(234, 179, 8, 0.2); color: #854d0e; font-weight: bold'
                elif val > 180:
                    return f'background-color: rgba(239, 68, 68, 0.2); color: #991b1b; font-weight: bold'
                else:
                    return f'background-color: rgba(34, 197, 94, 0.2); color: #166534; font-weight: bold'
            
            # Apply the style
            styled_df = manual_entries.style.applymap(color_glucose, subset=['glucose'])
            
            # Display with prettier column names
            styled_df = styled_df.format({'glucose': '{:.0f} mg/dL'})
            
            # Hide index - use updated Pandas styling method depending on version
            try:
                styled_df = styled_df.hide_index()  # newer versions
            except:
                styled_df = styled_df.hide(axis='index')  # older versions
            styled_df = styled_df.set_properties(**{
                'background-color': 'white',
                'border': '1px solid #e2e8f0',
                'border-radius': '4px',
                'padding': '10px'
            })
            
            st.dataframe(styled_df, use_container_width=True)
            
            # Export options with styled buttons
            col1, col2 = st.columns([3, 1])
            
            with col2:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📊 Export as CSV",
                    data=csv,
                    file_name="glucose_readings.csv",
                    mime="text/csv",
                    help="Download all your glucose readings as a CSV file"
                )
        else:
            st.info("No manual entries yet. Use the form above to add your first reading.")
    
    st.markdown("</div>", unsafe_allow_html=True)