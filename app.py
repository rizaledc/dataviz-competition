import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Set page config
st.set_page_config(
    page_title="Pacific Economy - SDG 8 Dashboard",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .category-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Define categories and their indicators
CATEGORY_INDICATORS = {
    "economy": {
        "display_name": "Economy Category",
        "indicators": {
            "SL_EMP_EARN": "8.5.1 Average hourly earnings",
            "DC_TOF_TRDCML": "8.1.1 Total official flows commitments for Aid for Trade, by recipient",
            "DC_TOF_TRDDBML": "8.1.2 Total official flows disbursed for Aid for Trade, by recipient",
            "FB_BNK_ACCSS": "8.1.3 Account at a financial institution or mobile-money-service provider",
        }
    },
    "work": {
        "display_name": "Work Category",
        "indicators": {
            "NY_GDP_PCAP": "8.2.1 Growth rate of real GDP per employed person",
            "SL_TLF_UEM": "8.5.2 Unemployment rate",
            "SL_TLF_NEET": "8.6.1 Youth not in education, employment, or training",
        }
    },
    "trade_resources": {
        "display_name": "Trade and Resources Category",
        "indicators": {
            "SL_TLF_CHD": "8.7.1 Proportion of children in employment",
            "SPC_8_9_1": "8.8.1 Tourism as a proportion of total GDP",
            "SPC_8_9_1IN": "8.9.1 Tourism as a proportion of total GDP, inward",
        }
    },
    "social_growth": {
        "display_name": "Social Growth and Development Category",
        "indicators": {
            "SPC_8_9_1OUT": "8.8.2 Tourism as a proportion of total GDP, outward",
        }
    }
}

@st.cache_data
def load_data():
    """Load and preprocess the dataset"""
    try:
        df = pd.read_csv('data/Sustainable Development Goal 08 - Decent Work and Economic Growth data.csv')
        # Rename the long column name
        df = df.rename(columns={'Pacific Island Countries and territories': 'country_territory'})
        
        # Clean the data
        df['country_territory'] = df['country_territory'].astype(str).str.strip().str.lower()
        df['TIME_PERIOD'] = df['TIME_PERIOD'].astype(str)
        df['OBS_VALUE'] = pd.to_numeric(df['OBS_VALUE'], errors='coerce')
        
        return df
    except FileNotFoundError:
        st.error("Dataset not found. Please ensure the CSV file is in the 'data' directory.")
        return None
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def create_bar_chart(filtered_data, indicator_display_name):
    """Create an interactive bar chart using Plotly"""
    # Aggregate data by country
    aggregated_data = filtered_data.groupby('country_territory')['OBS_VALUE'].sum().reset_index()
    aggregated_data = aggregated_data.sort_values('OBS_VALUE', ascending=False)
    
    fig = px.bar(
        aggregated_data,
        x='country_territory',
        y='OBS_VALUE',
        title=f'{indicator_display_name} - Bar Chart',
        labels={'country_territory': 'Country/Territory', 'OBS_VALUE': 'Observation Value'},
        color='OBS_VALUE',
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        showlegend=False,
        title_x=0.5
    )
    
    return fig

def create_box_plot(filtered_data, indicator_display_name):
    """Create an interactive box plot using Plotly"""
    fig = px.box(
        filtered_data,
        x='country_territory',
        y='OBS_VALUE',
        title=f'{indicator_display_name} - Box Plot',
        labels={'country_territory': 'Country/Territory', 'OBS_VALUE': 'Observation Value'},
        color='country_territory'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        showlegend=False,
        title_x=0.5
    )
    
    return fig

def create_line_chart(filtered_data, indicator_display_name):
    """Create an interactive line chart using Plotly"""
    fig = px.line(
        filtered_data,
        x='TIME_PERIOD',
        y='OBS_VALUE',
        color='country_territory',
        title=f'{indicator_display_name} - Time Series',
        labels={'TIME_PERIOD': 'Time Period', 'OBS_VALUE': 'Observation Value', 'country_territory': 'Country/Territory'},
        markers=True
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        title_x=0.5,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_heatmap(filtered_data, indicator_display_name):
    """Create a heatmap showing values across countries and time periods"""
    # Pivot data for heatmap
    pivot_data = filtered_data.pivot_table(
        values='OBS_VALUE', 
        index='country_territory', 
        columns='TIME_PERIOD', 
        aggfunc='mean'
    )
    
    fig = px.imshow(
        pivot_data,
        aspect="auto",
        title=f'{indicator_display_name} - Heatmap',
        labels={'x': 'Time Period', 'y': 'Country/Territory', 'color': 'Observation Value'},
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        height=500,
        title_x=0.5
    )
    
    return fig

def display_summary_statistics(filtered_data):
    """Display summary statistics"""
    if len(filtered_data) > 0:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Records", len(filtered_data))
        
        with col2:
            st.metric("Countries", filtered_data['country_territory'].nunique())
        
        with col3:
            st.metric("Time Periods", filtered_data['TIME_PERIOD'].nunique())
        
        with col4:
            mean_val = filtered_data['OBS_VALUE'].mean()
            st.metric("Average Value", f"{mean_val:.2f}" if pd.notna(mean_val) else "N/A")

def main():
    # Header
    st.markdown('<h1 class="main-header">🌊 Challenges and Opportunities in the Pacific Economy</h1>', unsafe_allow_html=True)
    st.markdown("### Sustainable Development Goal 8: Decent Work and Economic Growth")
    
    # Load data
    df = load_data()
    if df is None:
        st.stop()
    
    # Sidebar for filters
    st.sidebar.title("🎯 Filters")
    
    # Category selection
    category_options = {key: value["display_name"] for key, value in CATEGORY_INDICATORS.items()}
    selected_category_key = st.sidebar.selectbox(
        "Select Category:",
        options=list(category_options.keys()),
        format_func=lambda x: category_options[x],
        index=0
    )
    
    # Indicator selection
    indicators = CATEGORY_INDICATORS[selected_category_key]["indicators"]
    selected_indicator_code = st.sidebar.selectbox(
        "Select Indicator:",
        options=list(indicators.keys()),
        format_func=lambda x: indicators[x],
        index=0
    )
    
    indicator_display_name = indicators[selected_indicator_code]
    
    # Additional filters
    st.sidebar.markdown("---")
    
    # Country filter
    available_countries = sorted(df['country_territory'].unique())
    selected_countries = st.sidebar.multiselect(
        "Filter by Countries:",
        options=available_countries,
        default=available_countries
    )
    
    # Time period filter
    available_periods = sorted(df['TIME_PERIOD'].unique())
    selected_periods = st.sidebar.multiselect(
        "Filter by Time Periods:",
        options=available_periods,
        default=available_periods
    )
    
    # Filter data
    filtered_data = df[
        (df['INDICATOR'] == selected_indicator_code) &
        (df['country_territory'].isin(selected_countries)) &
        (df['TIME_PERIOD'].isin(selected_periods))
    ].copy()
    
    # Remove rows with NaN values
    filtered_data = filtered_data.dropna(subset=['OBS_VALUE'])
    
    # Main content
    if len(filtered_data) == 0:
        st.warning("No data available for the selected filters. Please adjust your selection.")
        return
    
    # Display selected indicator info
    st.markdown(f'<div class="metric-card"><strong>Selected Indicator:</strong> {indicator_display_name}</div>', unsafe_allow_html=True)
    
    # Summary statistics
    display_summary_statistics(filtered_data)
    
    # Chart selection tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Bar Chart", "📦 Box Plot", "📈 Line Chart", "🔥 Heatmap"])
    
    with tab1:
        st.plotly_chart(create_bar_chart(filtered_data, indicator_display_name), use_container_width=True)
        
        with st.expander("About Bar Chart"):
            st.write("This bar chart shows the aggregated observation values for each country/territory. "
                    "The bars are colored by their values, making it easy to identify patterns and outliers.")
    
    with tab2:
        st.plotly_chart(create_box_plot(filtered_data, indicator_display_name), use_container_width=True)
        
        with st.expander("About Box Plot"):
            st.write("This box plot displays the distribution of observation values for each country/territory, "
                    "showing quartiles, median, and potential outliers.")
    
    with tab3:
        st.plotly_chart(create_line_chart(filtered_data, indicator_display_name), use_container_width=True)
        
        with st.expander("About Line Chart"):
            st.write("This line chart shows the trend of observation values over time for each country/territory. "
                    "You can hover over points to see detailed information and toggle countries in the legend.")
    
    with tab4:
        if len(filtered_data['TIME_PERIOD'].unique()) > 1 and len(filtered_data['country_territory'].unique()) > 1:
            st.plotly_chart(create_heatmap(filtered_data, indicator_display_name), use_container_width=True)
            
            with st.expander("About Heatmap"):
                st.write("This heatmap provides a comprehensive view of observation values across countries and time periods. "
                        "Darker colors indicate higher values, making it easy to spot patterns and trends.")
        else:
            st.info("Heatmap requires data from multiple countries and time periods. Please adjust your filters.")
    
    # Data table
    with st.expander("📋 View Raw Data"):
        st.dataframe(filtered_data, use_container_width=True)
        
        # Download button
        csv = filtered_data.to_csv(index=False)
        st.download_button(
            label="Download filtered data as CSV",
            data=csv,
            file_name=f"sdg8_data_{selected_indicator_code}.csv",
            mime="text/csv"
        )
    
    # Footer
    st.markdown("---")
    st.markdown("Data visualization dashboard for Sustainable Development Goal 8: Decent Work and Economic Growth")

if _name_ == "_main_":
    main()
