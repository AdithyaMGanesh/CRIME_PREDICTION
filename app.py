from flask import Flask, request, jsonify
import pickle
import networkx as nx
from geopy.geocoders import Nominatim

app = Flask(__name__)

# Load trained crime prediction model
with open("crime_model.pkl", "rb") as f:
    model = pickle.load(f)

geolocator = Nominatim(user_agent="crime_safe_path")

# Convert location name to latitude and longitude
def get_coordinates(location_name):
    location = geolocator.geocode(location_name)
    if location:
        return (location.latitude, location.longitude)
    return None

# Crime Prediction Endpoint
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    import pandas as pd
    input_df = pd.DataFrame([data])

    if 'state_ut' in input_df.columns:
        input_df = pd.get_dummies(input_df, columns=['state_ut'], drop_first=True)
    if 'district' in input_df.columns:
        input_df = pd.get_dummies(input_df, columns=['district'], drop_first=True)

    expected_cols = model.feature_names_in_
    input_df = input_df.reindex(columns=expected_cols, fill_value=0)

    prediction = model.predict(input_df)[0]
    return jsonify({"predicted_total_ipc_crimes": prediction})

# Safe Path Recommendation Endpoint
@app.route('/safe_path', methods=['POST'])
def safe_path():
    data = request.get_json()
    start_name = data.get('current_location')
    destination_name = data.get('destination')

    start_coords = get_coordinates(start_name)
    end_coords = get_coordinates(destination_name)

    if not start_coords or not end_coords:
        return jsonify({"error": "Invalid location names"}), 400

    G = nx.Graph()
    G.add_edge(start_coords, end_coords, weight=0.5)  # Example: add crime risk-based weights
    
    try:
        path = nx.shortest_path(G, source=start_coords, target=end_coords, weight='weight')
    except nx.NetworkXNoPath:
        return jsonify({"error": "No safe path found"}), 400

    return jsonify({"safe_route": path})

# Emergency Tap Endpoint
@app.route('/emergency', methods=['POST'])
def emergency():
    data = request.get_json()
    user_location = data.get('location')
    user_id = data.get('user_id')
    print(f"EMERGENCY triggered by user {user_id} at location {user_location}")
    return jsonify({"status": "Emergency received. Authorities notified."})

if __name__ == '__main__':
    app.run(debug=True)
