import folium
from flask import Flask, render_template_string
from folium.plugins import Search

from data_processing import get_population_data
import json

app = Flask(__name__)

# Load data
df_total = get_population_data("data/europepopulation.xlsx", 2024, 'total')
df_under_15 = get_population_data("data/europepopulation.xlsx", 2024, 'under_15')
df_15_64 = get_population_data("data/europepopulation.xlsx", 2024, 'age_15_64')
df_over_65 = get_population_data("data/europepopulation.xlsx", 2024, 'over_65')
df_male_total = get_population_data("data/europepopulation.xlsx", 2024, 'male_total')
df_male_under_15 = get_population_data("data/europepopulation.xlsx", 2024, 'male_under_15')
df_male_15_64 = get_population_data("data/europepopulation.xlsx", 2024, 'male_15_64')
df_male_over_65 = get_population_data("data/europepopulation.xlsx", 2024, 'male_over_65')
df_female_total = get_population_data("data/europepopulation.xlsx", 2024, 'female_total')
df_female_under_15 = get_population_data("data/europepopulation.xlsx", 2024, 'female_under_15')
df_female_15_64 = get_population_data("data/europepopulation.xlsx", 2024, 'female_15_64')
df_female_over_65 = get_population_data("data/europepopulation.xlsx", 2024, 'female_over_65')

maps = {
    'total_map': df_total.set_index('NUTS_ID')['Population'].to_dict(),
    'under_15_map': df_under_15.set_index('NUTS_ID')['Population'].to_dict(),
    'age_15_64_map': df_15_64.set_index('NUTS_ID')['Population'].to_dict(),
    'over_65_map': df_over_65.set_index('NUTS_ID')['Population'].to_dict(),
    'male_total_map': df_male_total.set_index('NUTS_ID')['Population'].to_dict(),
    'male_under_15_map': df_male_under_15.set_index('NUTS_ID')['Population'].to_dict(),
    'male_15_64_map': df_male_15_64.set_index('NUTS_ID')['Population'].to_dict(),
    'male_over_65_map': df_male_over_65.set_index('NUTS_ID')['Population'].to_dict(),
    'female_total_map': df_female_total.set_index('NUTS_ID')['Population'].to_dict(),
    'female_under_15_map': df_female_under_15.set_index('NUTS_ID')['Population'].to_dict(),
    'female_15_64_map': df_female_15_64.set_index('NUTS_ID')['Population'].to_dict(),
    'female_over_65_map': df_female_over_65.set_index('NUTS_ID')['Population'].to_dict(),
}

with open("data/nutseurope.geojson", 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

# Add population to the GeoJSON file
for feature in geojson_data['features']:
    nuts_id = str(feature['properties'].get('NUTS_ID', '')).strip()
    for key, population_map in maps.items():
        prop_name = key.replace('_map', '').replace('_', ' ').title().replace(' ', '_') + '_Population'
        feature['properties'][prop_name] = population_map.get(nuts_id, None)
@app.route("/")
def fullscreen():
    """Render the population map."""
    m = folium.Map(location=[54.0, 15.0], zoom_start=4, tiles="Cartodb dark_matter", world_copy_jump=True, font_size=15)

    layer_configs = {
        'total_map': ('Total_Population', "Total population", "lightblue"),
        'under_15_map': ('Under_15_Population', "Population under 15", "blue"),
        'age_15_64_map': ('Age_15_64_Population', "Population age 15-64", "green"),
        'over_65_map': ('Over_65_Population', "Population over 65", "orange"),
        'male_total_map': ('Male_Total_Population', "Total male population", "grey"),
        'male_under_15_map': ('Male_Under_15_Population', "Male population under 15", "navy"),
        'male_15_64_map': ('Male_15_64_Population', "Male population 15-64", "teal"),
        'male_over_65_map': ('Male_Over_65_Population', "Male population over 65", "purple"),
        'female_total_map': ('Female_Total_Population', "Total female population", "pink"),
        'female_under_15_map': ('Female_Under_15_Population', "Female population under 15", "red"),
        'female_15_64_map': ('Female_15_64_Population', "Female population 15-64", "coral"),
        'female_over_65_map': ('Female_Over_65_Population', "Female population over 65", "magenta"),
    }

    layers = {}
    for map_key, (property_field, layer_name, fill_color) in layer_configs.items():
        layer = folium.GeoJson(
            geojson_data,
            name=layer_name,
            show=False,
            style_function=lambda feature, color=fill_color: {
                'fillColor': color,
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.5
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["NUTS_NAME", property_field],
                aliases=["Region", layer_name],
                localize=True
            ),
            popup=folium.GeoJsonPopup(fields=["NUTS_ID", "NUTS_NAME", property_field])
        ).add_to(m)
        layers[map_key] = layer

    Search(
        layer=layers['total_map'],
        geom_type='MultiPolygon',
        placeholder='Search area...',
        collapsed=False,
        search_label='NUTS_NAME',
        position='topright',
        search_zoom=7,
    ).add_to(m)

    folium.LayerControl(position="topright").add_to(m)

    return m.get_root().render()

if __name__ == "__main__":
    app.run(debug=True)
