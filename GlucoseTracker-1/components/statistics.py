import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def display_statistics(stats):
    """Display glucose statistics with enhanced styling"""
    if not stats:
        st.warning("⚠️ No data available for statistics")
        return
    
    st.markdown("""
    <div style="background: white; padding: 20px; border-radius: 15px; 
              box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px;
              border-left: 8px solid #10b981;">
    <h2 style="color: #10b981; margin-bottom: 15px;">Glucose Statistics</h2>
    """, unsafe_allow_html=True)
    
    # Create a row with 3 metrics in styled cards
    col1, col2, col3 = st.columns(3)

    # Determine colors based on values
    avg_color = "#22c55e" if 70 <= stats['average'] <= 180 else "#ef4444"
    range_color = "#22c55e" if stats['in_range'] >= 70 else (
        "#eab308" if stats['in_range'] >= 50 else "#ef4444"
    )
    std_color = "#22c55e" if stats['std'] < 40 else (
        "#eab308" if stats['std'] < 60 else "#ef4444"
    )
    
    with col1:
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.05); padding: 15px; border-radius: 12px; text-align: center;">
            <div style="color: #4b5563; font-size: 1rem;">Average Glucose</div>
            <div style="font-size: 2rem; font-weight: bold; color: {avg_color};">{stats['average']:.0f} mg/dL</div>
            <div style="font-size: 0.9rem; color: #4b5563; margin-top: 5px;">Target: 70-180 mg/dL</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.05); padding: 15px; border-radius: 12px; text-align: center;">
            <div style="color: #4b5563; font-size: 1rem;">Time in Range</div>
            <div style="font-size: 2rem; font-weight: bold; color: {range_color};">{stats['in_range']:.1f}%</div>
            <div style="font-size: 0.9rem; color: #4b5563; margin-top: 5px;">Target: >70%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.05); padding: 15px; border-radius: 12px; text-align: center;">
            <div style="color: #4b5563; font-size: 1rem;">Standard Deviation</div>
            <div style="font-size: 2rem; font-weight: bold; color: {std_color};">{stats['std']:.0f} mg/dL</div>
            <div style="font-size: 0.9rem; color: #4b5563; margin-top: 5px;">Target: <40 mg/dL</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Add the min/max glucose row
    st.markdown("""
    <div style="display: flex; margin-top: 15px; gap: 15px;">
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.05); padding: 15px; border-radius: 12px; text-align: center;">
            <div style="color: #4b5563; font-size: 1rem;">Lowest Reading</div>
            <div style="font-size: 1.8rem; font-weight: bold; color: #eab308;">{stats['min']:.0f} mg/dL</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.05); padding: 15px; border-radius: 12px; text-align: center;">
            <div style="color: #4b5563; font-size: 1rem;">Highest Reading</div>
            <div style="font-size: 1.8rem; font-weight: bold; color: #ef4444;">{stats['max']:.0f} mg/dL</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def plot_distribution(df):
    """Create enhanced glucose distribution plot"""
    if df.empty:
        return
    
    st.markdown("""
    <div style="background: white; padding: 20px; border-radius: 15px; 
              box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px;
              border-left: 8px solid #10b981;">
    <h2 style="color: #10b981; margin-bottom: 15px;">Glucose Distribution</h2>
    """, unsafe_allow_html=True)
    
    # Create distribution with colored regions
    fig = make_subplots(specs=[[{"secondary_y": False}]])
    
    # Add the histogram trace
    hist_trace = go.Histogram(
        x=df['sgv'],
        nbinsx=30,
        marker_color='rgba(16, 185, 129, 0.6)',
        name="Glucose Readings"
    )
    
    fig.add_trace(hist_trace)
    
    # Add colored region shapes for Low, Normal, and High
    fig.add_shape(
        type="rect",
        x0=0, x1=70,
        y0=0, y1=1,
        yref="paper",
        fillcolor="rgba(234, 179, 8, 0.2)",
        line=dict(width=0),
        layer="below"
    )
    
    fig.add_shape(
        type="rect",
        x0=70, x1=180,
        y0=0, y1=1,
        yref="paper",
        fillcolor="rgba(34, 197, 94, 0.2)",
        line=dict(width=0),
        layer="below"
    )
    
    fig.add_shape(
        type="rect",
        x0=180, x1=400,
        y0=0, y1=1,
        yref="paper",
        fillcolor="rgba(239, 68, 68, 0.2)",
        line=dict(width=0),
        layer="below"
    )
    
    # Add vertical lines for target range boundaries
    fig.add_shape(
        type="line",
        x0=70, x1=70,
        y0=0, y1=1,
        yref="paper",
        line=dict(color="rgba(34, 197, 94, 0.8)", width=2, dash="dash"),
    )
    
    fig.add_shape(
        type="line",
        x0=180, x1=180,
        y0=0, y1=1,
        yref="paper",
        line=dict(color="rgba(239, 68, 68, 0.8)", width=2, dash="dash"),
    )
    
    # Add annotations
    fig.add_annotation(
        x=50, y=0.95,
        text="Low",
        showarrow=False,
        yref="paper",
        font=dict(size=12, color="#4b5563")
    )
    
    fig.add_annotation(
        x=125, y=0.95,
        text="Target Range",
        showarrow=False,
        yref="paper",
        font=dict(size=12, color="#4b5563")
    )
    
    fig.add_annotation(
        x=240, y=0.95,
        text="High",
        showarrow=False,
        yref="paper",
        font=dict(size=12, color="#4b5563")
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title="Glucose (mg/dL)",
        yaxis_title="Frequency",
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            gridcolor='rgba(220,220,220,0.4)',
            showgrid=True,
            zeroline=False,
            range=[40, 300]
        ),
        yaxis=dict(
            gridcolor='rgba(220,220,220,0.4)',
            showgrid=True,
            zeroline=False
        ),
        bargap=0.05,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
