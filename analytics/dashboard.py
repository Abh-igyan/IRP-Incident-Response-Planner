
import pandas as pd
import numpy as np
import folium
from folium import plugins
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import json
import plotly.io as pio

def load_data():
    data = {}
    data['historical_incidents'] = pd.read_csv('analytics_exports/historical_incidents_clean.csv')
    data['corridor_summary'] = pd.read_csv('analytics_exports/corridor_summary.csv')
    data['event_summary'] = pd.read_csv('analytics_exports/event_summary.csv')
    data['vehicle_summary'] = pd.read_csv('analytics_exports/vehicle_summary.csv')
    data['heatmap_data'] = pd.read_csv('analytics_exports/heatmap_data.csv')
    data['feature_importance'] = pd.read_csv('analytics_exports/feature_importance.csv')
    with open('analytics_exports/project_metadata.json', 'r') as f:
        data['project_metadata'] = json.load(f)
    
    data['historical_incidents']['incident_datetime'] = pd.to_datetime(data['historical_incidents']['incident_datetime'])
    
    return data

def create_visualizations(data):
    # Create a list to hold all plotly figures
    figures = []

    # Feature Importance
    fig_feat_imp = px.bar(
        data['feature_importance'].sort_values('importance', ascending=False),
        x='importance',
        y='feature',
        orientation='h',
        title='Feature Importance'
    )
    figures.append(fig_feat_imp)

    # Incidents over time
    incidents_over_time = data['historical_incidents'].set_index('incident_datetime').resample('D').size().reset_index(name='count')
    fig_incidents_over_time = px.line(incidents_over_time, x='incident_datetime', y='count', title='Incidents Per Day')
    figures.append(fig_incidents_over_time)

    # Incidents by hour
    data['historical_incidents']['hour'] = data['historical_incidents']['incident_datetime'].dt.hour
    incidents_by_hour = data['historical_incidents']['hour'].value_counts().sort_index().reset_index(name='count')
    fig_incidents_by_hour = px.bar(incidents_by_hour, x='hour', y='count', title='Incidents by Hour of Day')
    figures.append(fig_incidents_by_hour)

    # Incidents by day of week
    data['historical_incidents']['day_of_week'] = data['historical_incidents']['incident_datetime'].dt.day_name()
    incidents_by_day = data['historical_incidents']['day_of_week'].value_counts().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']).reset_index(name='count')
    fig_incidents_by_day = px.bar(incidents_by_day, x='day_of_week', y='count', title='Incidents by Day of Week')
    figures.append(fig_incidents_by_day)

    # Top 10 Riskiest Corridors
    top_10_corridors = data['corridor_summary'].sort_values('closure_rate', ascending=False).head(10)
    fig_top_corridors = px.bar(top_10_corridors, x='corridor', y='closure_rate', title='Top 10 Riskiest Corridors by Closure Rate')
    figures.append(fig_top_corridors)
    
    # Event Cause Distribution
    fig_event_cause = px.pie(data['event_summary'], names='event_cause', values='closure_rate', title='Distribution of Event Causes by Closure Rate')
    figures.append(fig_event_cause)
    
    # Vehicle Type Distribution
    data['vehicle_summary'] = data['vehicle_summary'].rename(columns={'veh_type': 'vehicle_category'})
    fig_vehicle_type = px.pie(data['vehicle_summary'], names='vehicle_category', values='closure_rate', title='Distribution of Vehicle Types by Closure Rate')
    figures.append(fig_vehicle_type)

    # Save plotly figures to a single HTML file
    with open('analytics/plotly_visualizations.html', 'w') as f:
        f.write('<html><head><title>Traffic Incident Analytics</title></head><body>')
        for fig in figures:
            f.write(pio.to_html(fig, full_html=False, include_plotlyjs='cdn'))
        f.write('</body></html>')

    # Geographic Heatmap
    m = folium.Map(location=[12.9716, 77.5946], zoom_start=11)
    heat_data = data['heatmap_data'][['latitude', 'longitude']].values.tolist()
    folium.plugins.HeatMap(heat_data).add_to(m)
    m.save('analytics/incident_heatmap.html')

    # Correlation heatmap
    corr_df = data['historical_incidents'][['latitude', 'longitude', 'hour', 'closure_probability', 'impact_score']].corr()
    fig_corr = plt.figure(figsize=(10, 8))
    sns.heatmap(corr_df, annot=True, fmt=".2f")
    plt.title('Correlation Heatmap of Numerical Features')
    plt.savefig('analytics/correlation_heatmap.png')
    
if __name__ == '__main__':
    loaded_data = load_data()
    create_visualizations(loaded_data)
    print("Generated analytics files in the 'analytics' directory.")

