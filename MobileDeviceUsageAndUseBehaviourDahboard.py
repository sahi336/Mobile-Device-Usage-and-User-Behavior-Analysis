import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configure the page
st.set_page_config(
    page_title="Mobile Device Usage Dashboard",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin: 1.5rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Load and cache data
@st.cache_data
def load_data():
    """Load the dataset"""
    try:
        df = pd.read_csv('user_behavior_dataset.csv')
        # Create age groups
        df['Age_Group'] = pd.cut(df['Age'], 
                                bins=[17, 25, 35, 45, 59], 
                                labels=['18-25', '26-35', '36-45', '46-59'])
        return df
    except FileNotFoundError:
        st.error("❌ Dataset file 'user_behavior_dataset.csv' not found!")
        st.stop()

# Load data
df = load_data()

# Dashboard Title
st.markdown('<h1 class="main-header">📱 Mobile Device Usage Dashboard</h1>', unsafe_allow_html=True)

# Sidebar for filters
st.sidebar.markdown("## 🔧 Filters")

# Age filter
age_range = st.sidebar.slider(
    "Select Age Range",
    min_value=int(df['Age'].min()),
    max_value=int(df['Age'].max()),
    value=(int(df['Age'].min()), int(df['Age'].max()))
)

# Gender filter
gender_options = ['All'] + list(df['Gender'].unique())
selected_gender = st.sidebar.selectbox("Select Gender", gender_options)

# OS filter
os_options = ['All'] + list(df['Operating System'].unique())
selected_os = st.sidebar.selectbox("Select Operating System", os_options)

# Device filter
device_options = ['All'] + list(df['Device Model'].unique())
selected_device = st.sidebar.selectbox("Select Device Model", device_options)

# Apply filters
filtered_df = df[
    (df['Age'] >= age_range[0]) & 
    (df['Age'] <= age_range[1])
]

if selected_gender != 'All':
    filtered_df = filtered_df[filtered_df['Gender'] == selected_gender]

if selected_os != 'All':
    filtered_df = filtered_df[filtered_df['Operating System'] == selected_os]

if selected_device != 'All':
    filtered_df = filtered_df[filtered_df['Device Model'] == selected_device]

# Display filtered data info
st.sidebar.markdown("---")
st.sidebar.markdown(f"**📊 Filtered Data: {len(filtered_df)} users**")

# Main dashboard content
if len(filtered_df) == 0:
    st.warning("⚠️ No data matches your filters. Please adjust the selection.")
    st.stop()

# Key Metrics Row
st.markdown('<h2 class="sub-header">📈 Key Metrics</h2>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_screen_time = filtered_df['Screen On Time (hours/day)'].mean()
    st.metric(
        label="Avg Screen Time",
        value=f"{avg_screen_time:.1f} hrs/day",
        delta=f"{avg_screen_time - df['Screen On Time (hours/day)'].mean():.1f}"
    )

with col2:
    avg_app_usage = filtered_df['App Usage Time (min/day)'].mean()
    st.metric(
        label="Avg App Usage",
        value=f"{avg_app_usage:.0f} min/day",
        delta=f"{avg_app_usage - df['App Usage Time (min/day)'].mean():.0f}"
    )

with col3:
    avg_battery = filtered_df['Battery Drain (mAh/day)'].mean()
    st.metric(
        label="Avg Battery Drain",
        value=f"{avg_battery:.0f} mAh/day",
        delta=f"{avg_battery - df['Battery Drain (mAh/day)'].mean():.0f}"
    )

with col4:
    heavy_users = len(filtered_df[filtered_df['Screen On Time (hours/day)'] >= 8])
    heavy_percent = (heavy_users / len(filtered_df)) * 100
    st.metric(
        label="Heavy Users",
        value=f"{heavy_percent:.1f}%",
        delta=f"{heavy_users} users"
    )

# Visualization Section


# Create tabs for different visualizations
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "👥 Demographics", 
    "📱 Usage Patterns", 
    "🔋 Device Analysis", 
    "🎯 Behavior Classes",
    "🔍 Correlations"
])

with tab1:
    st.subheader("Demographics Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Age distribution
        fig_age = px.histogram(
            filtered_df, 
            x='Age', 
            nbins=20,
            title="Age Distribution",
            color_discrete_sequence=['#1f77b4']
        )
        fig_age.update_layout(height=400)
        st.plotly_chart(fig_age, use_container_width=True)
    
    with col2:
        # Screen time by age group and gender
        screen_by_demo = filtered_df.groupby(['Age_Group', 'Gender'])['Screen On Time (hours/day)'].mean().reset_index()
        fig_demo = px.bar(
            screen_by_demo,
            x='Age_Group',
            y='Screen On Time (hours/day)',
            color='Gender',
            title="Screen Time by Age Group and Gender",
            color_discrete_map={'Male': 'darkgreen', 'Female': 'purple'}
        )
        fig_demo.update_layout(height=400)
        st.plotly_chart(fig_demo, use_container_width=True)

with tab2:
    st.subheader("Usage Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # App usage vs battery drain scatter plot
        fig_scatter = px.scatter(
            filtered_df,
            x='App Usage Time (min/day)',
            y='Battery Drain (mAh/day)',
            color='User Behavior Class',
            title="App Usage vs Battery Drain",
            hover_data=['Age', 'Gender', 'Device Model']
        )
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col2:
        # Screen time distribution with thresholds
        fig_hist = px.histogram(
            filtered_df,
            x='Screen On Time (hours/day)',
            title="Screen Time Distribution",
            nbins=20
        )
        # Add threshold lines
        fig_hist.add_vline(x=8, line_dash="dash", line_color="orange", 
                          annotation_text="High Usage (8h)")
        fig_hist.add_vline(x=10, line_dash="dash", line_color="red", 
                          annotation_text="Extreme Usage (10h)")
        fig_hist.update_layout(height=400)
        st.plotly_chart(fig_hist, use_container_width=True)

with tab3:
    st.subheader("Device Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Device model usage comparison
        device_usage = filtered_df.groupby('Device Model')['Screen On Time (hours/day)'].mean().sort_values(ascending=True)
        fig_device = px.bar(
            x=device_usage.values,
            y=device_usage.index,
            orientation='h',
            title="Average Screen Time by Device Model",
            color=device_usage.values,
            color_continuous_scale='viridis'
        )
        fig_device.update_layout(height=400)
        st.plotly_chart(fig_device, use_container_width=True)
    
    with col2:
        # iOS vs Android comparison
        os_comparison = filtered_df.groupby('Operating System')[
            ['Screen On Time (hours/day)', 'App Usage Time (min/day)', 'Data Usage (MB/day)']
        ].mean()
        
        fig_os = go.Figure()
        
        for metric in os_comparison.columns:
            fig_os.add_trace(go.Bar(
                name=metric,
                x=os_comparison.index,
                y=os_comparison[metric]
            ))
        
        fig_os.update_layout(
            title="iOS vs Android Usage Comparison",
            barmode='group',
            height=400
        )
        st.plotly_chart(fig_os, use_container_width=True)

with tab4:
    st.subheader("User Behavior Classes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Behavior class distribution
        behavior_counts = filtered_df['User Behavior Class'].value_counts().sort_index()
        fig_behavior = px.pie(
            values=behavior_counts.values,
            names=[f"Class {i}" for i in behavior_counts.index],
            title="User Behavior Class Distribution"
        )
        fig_behavior.update_layout(height=400)
        st.plotly_chart(fig_behavior, use_container_width=True)
    
    with col2:
        # Data usage by behavior class
        fig_box = px.box(
            filtered_df,
            x='User Behavior Class',
            y='Data Usage (MB/day)',
            title="Data Usage by Behavior Class"
        )
        fig_box.update_layout(height=400)
        st.plotly_chart(fig_box, use_container_width=True)

with tab5:
    st.subheader("Correlation Analysis")
    
    # Correlation heatmap
    correlation_vars = [
        'Age', 'Screen On Time (hours/day)', 'App Usage Time (min/day)',
        'Battery Drain (mAh/day)', 'Data Usage (MB/day)', 'Number of Apps Installed'
    ]
    
    correlation_matrix = filtered_df[correlation_vars].corr()
    
    fig_corr = px.imshow(
        correlation_matrix,
        title="Correlation Matrix - Usage Metrics",
        color_continuous_scale='RdBu',
        aspect="auto"
    )
    fig_corr.update_layout(height=500)
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # Show correlation values
    st.subheader("Correlation Values")
    st.dataframe(correlation_matrix.round(3))

# Data Table Section
st.markdown('<h2 class="sub-header">📋 Filtered Data</h2>', unsafe_allow_html=True)

# Show data table with option to download
st.subheader(f"Data Table ({len(filtered_df)} rows)")

# Add download button
csv = filtered_df.to_csv(index=False)
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv,
    file_name='filtered_mobile_usage_data.csv',
    mime='text/csv'
)

# Display the data
st.dataframe(filtered_df, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>📱 Mobile Device Usage Dashboard | Built with Streamlit</p>
        <p>Interactive analysis of mobile device usage patterns and user behavior</p>
    </div>
    """, 
    unsafe_allow_html=True
)
