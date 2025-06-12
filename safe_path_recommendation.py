import folium
import geopandas as gpd
import networkx as nx
import osmnx as ox
import pandas as pd
from flask import Flask, request, render_template

app = Flask(__name__)

# Load crime data (assuming you have risk scores for districts)
crime_data = pd.read_csv("districtwise_crime_rates.csv")

# Function to generate a safe route

def get_safe_route(start, end):
    # Load OpenStreetMap road network
    G = ox.graph_from_place("India", network_type='drive')
    
    # Convert locations to nearest nodes
    orig_node = ox.distance.nearest_nodes(G, start[1], start[0])
    dest_node = ox.distance.nearest_nodes(G, end[1], end[0])
    
    # Assign crime risk as edge weights
    for u, v, data in G.edges(data=True):
        data['weight'] = 1  # Default weight
        for _, row in crime_data.iterrows():
            if row['District'] in data.get('name', ''):
                data['weight'] += row['Crime_Risk_Score']
    
    # Find the safest path
    route = nx.shortest_path(G, orig_node, dest_node, weight='weight')
    return route, G

@app.route('/safe_route', methods=['GET'])
def safe_route():
    start_lat = float(request.args.get('start_lat'))
    start_lon = float(request.args.get('start_lon'))
    end_lat = float(request.args.get('end_lat'))
    end_lon = float(request.args.get('end_lon'))
    
    route, G = get_safe_route((start_lat, start_lon), (end_lat, end_lon))
    
    # Generate a map
    m = ox.plot_route_folium(G, route, route_map=folium.Map(location=[start_lat, start_lon], zoom_start=12))
    map_path = "templates/safe_route.html"
    m.save(map_path)
    
    return render_template("safe_route.html")

if __name__ == '__main__':
    app.run(debug=True)