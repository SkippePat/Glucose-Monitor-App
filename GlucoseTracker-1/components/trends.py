import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta

def plot_glucose_trend(df):
    """Create an enhanced interactive glucose trend plot"""
    if df.empty:
        st.warning("⚠️ No data available for trend visualization")
        return
    
    # Create a styled container
    st.markdown("""
    <div style="background: white; padding: 20px; border-radius: 15px; 
              box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px;
              border-left: 8px solid #10b981;">
    <h2 style="color: #10b981; margin-bottom: 15px;">Glucose Trend</h2>
    """, unsafe_allow_html=True)
    
    # Create figure with gradient line
    fig = go.Figure()
    
    # Calculate gradients for line segments based on values (in range, high, low)
    line_color = []
    for i in range(len(df) - 1):
        # Color based on glucose range
        if df['sgv'].iloc[i] < 70:
            line_color.append('#eab308')  # Yellow for low
        elif df['sgv'].iloc[i] > 180:
            line_color.append('#ef4444')  # Red for high
        else:
            line_color.append('#22c55e')  # Green for in range
    
    # Create colored line segments for each point to the next
    for i in range(len(df) - 1):
        fig.add_trace(go.Scatter(
            x=df['datetime'].iloc[i:i+2],
            y=df['sgv'].iloc[i:i+2],
            mode='lines',
            line=dict(color=line_color[i], width=3),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Add markers for each reading
    fig.add_trace(go.Scatter(
        x=df['datetime'],
        y=df['sgv'],
        mode='markers',
        name='Glucose',
        marker=dict(
            size=8,
            color=df['sgv'].apply(lambda x: '#eab308' if x < 70 else ('#ef4444' if x > 180 else '#22c55e')),
            line=dict(color='white', width=1)
        ),
        hovertemplate='<b>%{y:.0f} mg/dL</b><br>%{x|%I:%M %p}<extra></extra>'
    ))
    
    # Add rolling average as a smooth line
    if 'rolling_avg' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['datetime'],
            y=df['rolling_avg'],
            mode='lines',
            name='3-Hour Average',
            line=dict(color='rgba(16, 185, 129, 0.7)', width=2, dash='dot'),
            hovertemplate='<b>Avg: %{y:.0f} mg/dL</b><extra></extra>'
        ))
    
    # Add colored range bands for low, normal, high
    fig.add_hrect(
        y0=0, y1=70,
        fillcolor="rgba(234, 179, 8, 0.1)",
        layer="below",
        line_width=0,
        name="Low Range"
    )
    
    fig.add_hrect(
        y0=70, y1=180,
        fillcolor="rgba(34, 197, 94, 0.1)",
        layer="below",
        line_width=0,
        name="Target Range"
    )
    
    fig.add_hrect(
        y0=180, y1=400,
        fillcolor="rgba(239, 68, 68, 0.1)",
        layer="below",
        line_width=0,
        name="High Range"
    )
    
    # Add horizontal threshold lines
    fig.add_shape(
        type="line",
        x0=df['datetime'].min(), 
        x1=df['datetime'].max(),
        y0=70, y1=70,
        line=dict(color="rgba(234, 179, 8, 0.7)", width=1.5, dash="dash"),
    )
    
    fig.add_shape(
        type="line",
        x0=df['datetime'].min(), 
        x1=df['datetime'].max(),
        y0=180, y1=180,
        line=dict(color="rgba(239, 68, 68, 0.7)", width=1.5, dash="dash"),
    )
    
    # Add annotations for the thresholds
    fig.add_annotation(
        x=df['datetime'].min() + timedelta(minutes=20),
        y=65,
        text="Low",
        showarrow=False,
        font=dict(size=10, color="#4b5563")
    )
    
    fig.add_annotation(
        x=df['datetime'].min() + timedelta(minutes=20),
        y=185,
        text="High",
        showarrow=False,
        font=dict(size=10, color="#4b5563")
    )
    
    # Update layout with modern styling
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Glucose (mg/dL)",
        hovermode='closest',
        height=450,
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            gridcolor='rgba(220,220,220,0.4)',
            showgrid=True,
            zeroline=False
        ),
        yaxis=dict(
            gridcolor='rgba(220,220,220,0.4)',
            showgrid=True,
            zeroline=False,
            range=[max(0, df['sgv'].min() - 20), min(400, df['sgv'].max() + 20)]
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add time period selector buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="text-align: center;">
            <button style="background: linear-gradient(90deg, #10b981, #059669); color: white; border: none; padding: 8px 15px; 
                    border-radius: 8px; font-weight: 500; width: 100%; cursor: pointer;">6 Hours</button>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center;">
            <button style="background: linear-gradient(90deg, #10b981, #059669); color: white; border: none; padding: 8px 15px; 
                    border-radius: 8px; font-weight: 500; width: 100%; cursor: pointer;">12 Hours</button>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center;">
            <button style="background: linear-gradient(90deg, #10b981, #059669); color: white; border: none; padding: 8px 15px; 
                    border-radius: 8px; font-weight: 500; width: 100%; cursor: pointer;">24 Hours</button>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="text-align: center;">
            <button style="background: linear-gradient(90deg, #10b981, #059669); color: white; border: none; padding: 8px 15px; 
                    border-radius: 8px; font-weight: 500; width: 100%; cursor: pointer;">48 Hours</button>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
