from flask import Flask, render_template, request
import pandas as pd
import os
from bokeh.plotting import figure, show
from bokeh.embed import components
from bokeh.models import FactorRange

app = Flask(__name__)

# Load the dataset globally
df = pd.read_csv('data/Sustainable Development Goal 08 - Decent Work and Economic Growth data.csv')
# print(f"Dataset columns: {df.columns.tolist()}") # Temporary print for debugging

# Ensure the visualization directory exists
if not os.path.exists('static/visualizations'):
    os.makedirs('static/visualizations')

# Route for the homepage
@app.route('/')
def index():
    # You can pass any relevant data to be displayed on the homepage here
    indicators = df['INDICATOR'].unique().tolist()
    return render_template('index.html', title="SDG 08 Visualization", indicators=indicators)

# Route to display the visualizations
@app.route('/visualize', methods=['POST'])
def visualize():
    indicator = request.form.get('indicator')
    # Removed visualization_type as it's now handled by client-side tabs

    # Store the selected indicator for display after submission
    selected_indicator = indicator

    filtered_data = df[df['INDICATOR'] == indicator]

    # Clean and aggregate data to handle duplicate 'Pacific Island Countries and territories'
    filtered_data['Pacific Island Countries and territories'] = filtered_data['Pacific Island Countries and territories'].astype(str).str.strip().str.lower()
    aggregated_data = filtered_data.groupby('Pacific Island Countries and territories')['OBS_VALUE'].sum().reset_index()

    # Initialize all Bokeh components to None
    bokeh_script_bar, bokeh_div_bar = None, None
    bokeh_script_box, bokeh_div_box = None, None
    bokeh_script_line, bokeh_div_line = None, None

    # --- Generate Bar Chart (Kategori Statistik) ---
    countries_bar = sorted(aggregated_data['Pacific Island Countries and territories'].unique().tolist())
    p_bar = figure(x_range=FactorRange(factors=countries_bar), height=350, sizing_mode='scale_width', title=f'Visualization for {indicator} (Bar Chart)',
               x_axis_label="Pacific Island Countries and territories", y_axis_label="Observation Value")
    p_bar.vbar(x=aggregated_data['Pacific Island Countries and territories'], top=aggregated_data['OBS_VALUE'], width=0.9)
    p_bar.xgrid.grid_line_color = None
    p_bar.y_range.start = 0
    p_bar.xaxis.major_label_orientation = 1.2
    bokeh_script_bar, bokeh_div_bar = components(p_bar)

    # --- Generate Box Plot (Kategori Geografis) ---
    box_data = filtered_data.groupby('Pacific Island Countries and territories')['OBS_VALUE'].agg([
        ('q1', lambda x: x.quantile(0.25)),
        ('q2', lambda x: x.quantile(0.5)),
        ('q3', lambda x: x.quantile(0.75)),
        ('upper', lambda x: x.quantile(0.75) + 1.5*(x.quantile(0.75)-x.quantile(0.25))),
        ('lower', lambda x: x.quantile(0.25) - 1.5*(x.quantile(0.75)-x.quantile(0.25)))
    ]).reset_index()

    countries_box = sorted(box_data['Pacific Island Countries and territories'].unique().tolist())
    p_box = figure(x_range=FactorRange(factors=countries_box), height=350, sizing_mode='scale_width', title=f'Visualization for {indicator} (Box Plot)',
               x_axis_label="Pacific Island Countries and territories", y_axis_label="Observation Value")

    p_box.vbar(x=box_data['Pacific Island Countries and territories'], width=0.7, bottom=box_data.q1, top=box_data.q3, fill_color="#1f77b4", line_color="black")
    p_box.vbar(x=box_data['Pacific Island Countries and territories'], width=0.2, bottom=box_data.lower, top=box_data.upper, line_color="black")
    p_box.line(box_data['Pacific Island Countries and territories'], box_data.q2, line_color="white", line_width=2)

    p_box.xgrid.grid_line_color = None
    p_box.y_range.start = 0
    p_box.xaxis.major_label_orientation = 1.2
    bokeh_script_box, bokeh_div_box = components(p_box)

    # --- Generate Line Chart (Kategori Waktu) ---
    filtered_data['TIME_PERIOD'] = filtered_data['TIME_PERIOD'].astype(str)
    time_periods = sorted(filtered_data['TIME_PERIOD'].unique().tolist())
    p_line = figure(x_range=FactorRange(factors=time_periods), height=350, sizing_mode='scale_width', title=f'Visualization for {indicator} (Line Chart)',
               x_axis_label="Time Period", y_axis_label="Observation Value")

    for country in filtered_data['Pacific Island Countries and territories'].unique():
        country_data = filtered_data[filtered_data['Pacific Island Countries and territories'] == country].sort_values(by='TIME_PERIOD')
        p_line.line(x=country_data['TIME_PERIOD'], y=country_data['OBS_VALUE'], legend_label=country, line_width=2)

    p_line.xgrid.grid_line_color = None
    p_line.y_range.start = 0
    p_line.xaxis.major_label_orientation = 1.2
    p_line.legend.location = "top_left"
    bokeh_script_line, bokeh_div_line = components(p_line)

    # Ensure indicators are always passed back to the template
    indicators = df['INDICATOR'].unique().tolist()
    return render_template('index.html', 
                           title="SDG 08 Visualization", 
                           indicators=indicators,
                           selected_indicator=selected_indicator,
                           bokeh_script_bar=bokeh_script_bar, bokeh_div_bar=bokeh_div_bar,
                           bokeh_script_box=bokeh_script_box, bokeh_div_box=bokeh_div_box,
                           bokeh_script_line=bokeh_script_line, bokeh_div_line=bokeh_div_line)

if __name__ == '__main__':
    app.run(debug=True)
