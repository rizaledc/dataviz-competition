  return render_template('index.html', 
                           title="Challenges and Opportunities in the Pacific Economy", 
                           categories_data=CATEGORY_INDICATORS,
                           selected_category_key=selected_category_key,
                           selected_indicator_code=selected_indicator_code,
                           selected_indicator_display_name=indicator_display_name,
                           bokeh_script_bar=bokeh_script_bar, bokeh_div_bar=bokeh_div_bar,
                           bokeh_script_box=bokeh_script_box, bokeh_div_box=bokeh_div_box,
                           bokeh_script_line=bokeh_script_line, bokeh_div_line=bokeh_div_line)