import pickle
import pandas as pd
import googlemaps
import os
import cx_Oracle  # Oracle DB Connection
from flask import Flask, request, jsonify
from geopy.geocoders import Nominatim

app = Flask(__name__)

# ✅ Load Crime Prediction Model
with open("crime_model.pkl", "rb") as f:
    model = pickle.load(f)

# ✅ Initialize Google Maps API Client
GMAPS_API_KEY = "YOUR_GOOGLE_MAPS_API_KEY"  # Replace with your API key
gmaps = googlemaps.Client(key=GMAPS_API_KEY)

# ✅ Geolocation Service (for Safe Path)
geolocator = Nominatim(user_agent="crime_safe_path")

# ✅ Oracle Database Connection
ORACLE_DSN = cx_Oracle.makedsn("localhost", 1521, service_name="XE")  # Update as per your setup
ORACLE_USER = "your_username"
ORACLE_PASSWORD = "your_password"

def get_db_connection():
    return cx_Oracle.connect(ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN)

# ✅ Convert Location Name to Latitude & Longitude
def get_coordinates(location_name):
    try:
        location = geolocator.geocode(location_name)
        return (location.latitude, location.longitude) if location else None
    except Exception as e:
        print(f"⚠️ Geolocation error: {e}")
        return None

# ✅ **Crime Prediction API**
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        # ✅ Convert all keys to uppercase (to match SQL & model columns)
        data = {key.upper(): value for key, value in data.items()}

        # ✅ Convert JSON input to DataFrame
        input_df = pd.DataFrame([data])

        # ✅ Ensure columns match model training
        expected_cols = model.feature_names_in_
        input_df = input_df.reindex(columns=expected_cols, fill_value=0)

        # ✅ Make Prediction
        prediction = model.predict(input_df)[0]

        return jsonify({"predicted_total_ipc_crimes": prediction})

    except Exception as e:
        print(f"❌ Error in prediction: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# ✅ **Fetch Crime Data from Oracle**
@app.route('/get_crime_data', methods=['GET'])
def get_crime_data():
    try:
        state = request.args.get("state_ut")
        district = request.args.get("district")
        year = request.args.get("year")

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        SELECT * FROM crime_data
        WHERE STATE_UT = :state AND DISTRICT = :district AND YEAR = :year
        """
        cursor.execute(query, {"state": state, "district": district, "year": year})
        data = cursor.fetchall()
        cursor.close()
        conn.close()

        if not data:
            return jsonify({"error": "No data found"}), 404

        return jsonify({"crime_data": data})

    except Exception as e:
        print(f"❌ Error fetching crime data: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# ✅ **Safe Path Recommendation API**
@app.route('/safe_path', methods=['POST'])
def safe_path():
    try:
        data = request.get_json()
        start_name = data.get("current_location")
        destination_name = data.get("destination")

        if not start_name or not destination_name:
            return jsonify({"error": "Missing start or destination"}), 400

        start_coords = get_coordinates(start_name)
        end_coords = get_coordinates(destination_name)

        if not start_coords or not end_coords:
            return jsonify({"error": "Invalid location names"}), 400

        # ✅ Get Directions from Google Maps API
        directions = gmaps.directions(
            f"{start_coords[0]},{start_coords[1]}",
            f"{end_coords[0]},{end_coords[1]}",
            mode="driving"
        )

        if not directions:
            return jsonify({"error": "No route found"}), 404

        # ✅ Extract Route Steps
        steps = []
        for step in directions[0]["legs"][0]["steps"]:
            lat = step["start_location"]["lat"]
            lon = step["start_location"]["lng"]
            steps.append((lat, lon))

        return jsonify({"safe_route": steps})

    except Exception as e:
        print(f"❌ Error in Safe Path Recommendation: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# ✅ **Emergency Tap API**
@app.route('/emergency', methods=['POST'])
def emergency():
    try:
        data = request.get_json()
        user_location = data.get("location")
        user_id = data.get("user_id", "Unknown User")

        # ✅ Send notification (SMS, email, etc. - Placeholder)
        print(f"🚨 EMERGENCY triggered by {user_id} at {user_location}")

        return jsonify({"status": "Emergency received. Authorities notified."})

    except Exception as e:
        print(f"❌ Error in Emergency Tap: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# ✅ **Run the Flask App**
if __name__ == "__main__":
    app.run(debug=True)
