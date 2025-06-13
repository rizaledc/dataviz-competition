from flask import Flask, render_template, request
import pandas as pd
import os
from bokeh.plotting import figure, show
from bokeh.embed import components
from bokeh.models import FactorRange

app = Flask(__name__)

# Load the dataset globally
df = pd.read_csv('data/Sustainable Development Goal 08 - Decent Work and Economic Growth data.csv')

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
    filtered_data = df[df['INDICATOR'] == indicator]

    # Clean and aggregate data to handle duplicate 'Pacific Island Countries and territories'
    filtered_data['Pacific Island Countries and territories'] = filtered_data['Pacific Island Countries and territories'].astype(str).str.strip().str.lower()
    aggregated_data = filtered_data.groupby('Pacific Island Countries and territories')['OBS_VALUE'].sum().reset_index()

    # Ensure unique and sorted categories for Bokeh x_range
    countries = sorted(aggregated_data['Pacific Island Countries and territories'].unique().tolist())
    print(f"Countries for Bokeh x_range: {countries}") # Temporary print for debugging
    
    # Create an interactive plot using Bokeh
    p = figure(x_range=FactorRange(factors=countries), height=350, title=f'Visualization for {indicator}',
               x_axis_label="Pacific Island Countries and territories", y_axis_label="Observation Value")
    p.vbar(x=aggregated_data['Pacific Island Countries and territories'], top=aggregated_data['OBS_VALUE'], width=0.9)

    # Customize plot (optional)
    p.xgrid.grid_line_color = None
    p.y_range.start = 0
    p.xaxis.major_label_orientation = 1.2 # Rotate x-axis labels for better readability

    # Generate Bokeh components
    script, div = components(p)

    # Ensure indicators are always passed back to the template
    indicators = df['INDICATOR'].unique().tolist()
    return render_template('index.html', title="SDG 08 Visualization", bokeh_script=script, bokeh_div=div, indicators=indicators)

if __name__ == '__main__':
    app.run(debug=True)
