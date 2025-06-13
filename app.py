from flask import Flask, render_template, request
import pandas as pd
import os
from bokeh.plotting import figure, show
from bokeh.embed import components
from bokeh.models import FactorRange, HoverTool, ColumnDataSource

app = Flask(__name__)

# Load the dataset globally
df = pd.read_csv('data/Sustainable Development Goal 08 - Decent Work and Economic Growth data.csv')
# Define categories and their indicators with human-readable names and descriptions
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

# Create a mapping from indicator code to human-readable name
indicator_names = df.set_index('INDICATOR')['Indicator'].drop_duplicates().to_dict()
# print(f"Dataset columns: {df.columns.tolist()}") # Temporary print for debugging

# Ensure the visualization directory exists
if not os.path.exists('static/visualizations'):
    os.makedirs('static/visualizations')

# Route for the homepage
@app.route('/')
def index():
    # Pass all categories and their indicators to the template for dynamic dropdowns
    return render_template(
        'index.html',
        title="Challenges and Opportunities in the Pacific Economy",
        categories_data=CATEGORY_INDICATORS, # New variable
        selected_category_key="economy", # Default selected category
        selected_indicator_code="", # Default selected indicator
        bokeh_script_bar=None, bokeh_div_bar=None,
        bokeh_script_box=None, bokeh_div_box=None,
        bokeh_script_line=None, bokeh_div_line=None
    )

# Route to display the visualizations
@app.route('/visualize', methods=['POST'])
def visualize():
    selected_category_key = request.form.get('category')
    indicator_code = request.form.get('indicator')

    # Retrieve display name from the CATEGORY_INDICATORS structure
    indicator_display_name = CATEGORY_INDICATORS.get(selected_category_key, {}).get("indicators", {}).get(indicator_code, indicator_code)

    # Store selected indicator for display after submission
    selected_indicator_code = indicator_code

    filtered_data = df[df['INDICATOR'] == indicator_code]

    # Clean and aggregate data to handle duplicate 'Pacific Island Countries and territories'
    filtered_data['Pacific Island Countries and territories'] = filtered_data['Pacific Island Countries and territories'].astype(str).str.strip().str.lower()
    aggregated_data = filtered_data.groupby('Pacific Island Countries and territories')['OBS_VALUE'].sum().reset_index()
    aggregated_data = aggregated_data.rename(columns={'Pacific Island Countries and territories': 'country_territory'})
    print(f"DEBUG: Aggregated Data Columns (Bar Chart): {aggregated_data.columns.tolist()}")
    print(f"DEBUG: Aggregated Data Sample (Bar Chart):\n{aggregated_data.head()}")

    # Initialize all Bokeh components to None
    bokeh_script_bar, bokeh_div_bar = None, None
    bokeh_script_box, bokeh_div_box = None, None
    bokeh_script_line, bokeh_div_line = None, None

    # --- Generate Bar Chart (Statistical Category) ---
    countries_bar = sorted(aggregated_data['country_territory'].unique().tolist())
    p_bar = figure(x_range=FactorRange(factors=countries_bar), height=350, sizing_mode='scale_width', title=f'Visualization for {indicator_display_name} (Bar Chart)',
               x_axis_label="Country/Territory", y_axis_label="Observation Value")
    source_bar = ColumnDataSource(aggregated_data)
    p_bar.vbar(x='country_territory', top='OBS_VALUE', width=0.9, source=source_bar)

    p_bar.xgrid.grid_line_color = None
    p_bar.y_range.start = 0
    p_bar.xaxis.major_label_orientation = 1.2
    
    # Add HoverTool for Bar Chart
    p_bar.add_tools(HoverTool(tooltips=[
        ("Country/Territory", "@country_territory"),
        ("Observation Value", "@OBS_VALUE"),
    ]))

    bokeh_script_bar, bokeh_div_bar = components(p_bar)

    # --- Generate Box Plot (Geographical Category) ---
    box_data = filtered_data.groupby('Pacific Island Countries and territories')['OBS_VALUE'].agg([
        ('q1', lambda x: x.quantile(0.25)),
        ('q2', lambda x: x.quantile(0.5)),
        ('q3', lambda x: x.quantile(0.75)),
        ('upper', lambda x: x.quantile(0.75) + 1.5*(x.quantile(0.75)-x.quantile(0.25))),
        ('lower', lambda x: x.quantile(0.25) - 1.5*(x.quantile(0.75)-x.quantile(0.25)))
    ]).reset_index()
    box_data = box_data.rename(columns={'Pacific Island Countries and territories': 'country_territory'})
    print(f"DEBUG: Box Data Columns (Box Plot): {box_data.columns.tolist()}")
    print(f"DEBUG: Box Data Sample (Box Plot):\n{box_data.head()}")

    countries_box = sorted(box_data['country_territory'].unique().tolist())
    p_box = figure(x_range=FactorRange(factors=countries_box), height=350, sizing_mode='scale_width', title=f'Visualization for {indicator_display_name} (Box Plot)',
               x_axis_label="Country/Territory", y_axis_label="Observation Value")

    source_box = ColumnDataSource(box_data)
    p_box.vbar(x='country_territory', width=0.7, bottom='q1', top='q3', fill_color="#1f77b4", line_color="black", source=source_box)
    p_box.vbar(x='country_territory', width=0.2, bottom='lower', top='upper', line_color="black", source=source_box)
    p_box.line(x='country_territory', y='q2', line_color="white", line_width=2, source=source_box)

    p_box.xgrid.grid_line_color = None
    p_box.y_range.start = 0
    p_box.xaxis.major_label_orientation = 1.2

    # Add HoverTool for Box Plot
    p_box.add_tools(HoverTool(tooltips=[
        ("Country/Territory", "@country_territory"),
        ("Q1", "@q1"),
        ("Q2 (Median)", "@q2"),
        ("Q3", "@q3"),
        ("Upper", "@upper"),
        ("Lower", "@lower"),
    ]))

    bokeh_script_box, bokeh_div_box = components(p_box)

    # --- Generate Line Chart (Time Category) ---
    filtered_data['TIME_PERIOD'] = filtered_data['TIME_PERIOD'].astype(str)
    time_periods = sorted(filtered_data['TIME_PERIOD'].unique().tolist())
    p_line = figure(x_range=FactorRange(factors=time_periods), height=350, sizing_mode='scale_width', title=f'Visualization for {indicator_display_name} (Line Chart)',
               x_axis_label="Time Period", y_axis_label="Observation Value")

    # Add HoverTool for Line Chart (before plotting lines)
    p_line.add_tools(HoverTool(tooltips=[
        ("Country/Territory", "$name"), # $name refers to the legend_label
        ("Time Period", "@TIME_PERIOD"),
        ("Observation Value", "@OBS_VALUE"),
    ]))

    for country in filtered_data['Pacific Island Countries and territories'].unique():
        country_data = filtered_data[filtered_data['Pacific Island Countries and territories'] == country].sort_values(by='TIME_PERIOD')
        country_data = country_data.rename(columns={'Pacific Island Countries and territories': 'country_territory'})
        print(f"DEBUG: Line Chart Data Columns for {country}: {country_data.columns.tolist()}")
        print(f"DEBUG: Line Chart Data Sample for {country}:\n{country_data.head()}")
        source_line = ColumnDataSource(country_data) # Create a source for each country
        p_line.line(x='TIME_PERIOD', y='OBS_VALUE', source=source_line, legend_label=country, line_width=2)

    p_line.xgrid.grid_line_color = None
    p_line.y_range.start = 0
    p_line.xaxis.major_label_orientation = 1.2
    p_line.legend.location = "top_left"
    bokeh_script_line, bokeh_div_line = components(p_line)

    return render_template('index.html', 
                           title="Challenges and Opportunities in the Pacific Economy", 
                           categories_data=CATEGORY_INDICATORS,
                           selected_category_key=selected_category_key,
                           selected_indicator_code=selected_indicator_code,
                           selected_indicator_display_name=indicator_display_name,
                           bokeh_script_bar=bokeh_script_bar, bokeh_div_bar=bokeh_div_bar,
                           bokeh_script_box=bokeh_script_box, bokeh_div_box=bokeh_div_box,
                           bokeh_script_line=bokeh_script_line, bokeh_div_line=bokeh_div_line)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Get port from environment or default to 5000
        app.run(host='0.0.0.0', port=port, debug=True)  # Use 0.0.0.0 and the dynamic port
