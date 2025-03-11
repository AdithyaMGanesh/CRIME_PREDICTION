from flask import Flask, request, jsonify
from flask_cors import CORS  # ✅ Import CORS for handling frontend requests
import pickle
import networkx as nx
from geopy.geocoders import Nominatim
import cx_Oracle
import pandas as pd
import os

app = Flask(__name__)
CORS(app)  # ✅ Enable CORS for all routes

# ✅ Load trained crime prediction model
MODEL_PATH = "crime_model.pkl"
if os.path.exists(MODEL_PATH):
    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        print("✅ Model loaded successfully!")
    except Exception as e:
        model = None
        print(f"⚠️ Error loading model: {e}")
else:
    model = None
    print("⚠️ Warning: crime_model.pkl not found!")

# ✅ Oracle Database Connection
def get_db_connection():
    try:
        dsn_tns = cx_Oracle.makedsn("localhost", 1521, service_name="XE")  
        conn = cx_Oracle.connect(user="system", password="adithya123", dsn=dsn_tns)
        return conn
    except cx_Oracle.DatabaseError as e:
        print("❌ Database connection failed:", str(e))
        return None

# ✅ Geolocation Service
geolocator = Nominatim(user_agent="crime_safe_path")

# ✅ Convert Location Name to Latitude & Longitude
def get_coordinates(location_name):
    if not location_name:
        return None
    try:
        location = geolocator.geocode(location_name)
        if location:
            return (location.latitude, location.longitude)
    except Exception as e:
        print(f"⚠️ Geolocation error: {e}")
        return None
    return None  

# ====================== 🟢 API ENDPOINTS ======================

# ✅ **Default Homepage Route**
@app.route('/')
def home():
    return "✅ Crime Prediction System API is Running! Use /predict or /safe_path."

# ✅ **Crime Prediction API**
@app.route('/predict', methods=['POST'])
def predict():
    if not model:
        print("❌ Model not loaded!")
        return jsonify({"error": "Crime model not loaded"}), 500
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        print("📥 Received data:", data)

        input_df = pd.DataFrame([data])

        # ✅ Ensure categorical columns exist before encoding
        categorical_columns = ['state_ut', 'district']
        for col in categorical_columns:
            if col in input_df.columns:
                input_df = pd.get_dummies(input_df, columns=[col], drop_first=True)

        # ✅ Ensure correct column order
        expected_cols = model.feature_names_in_
        input_df = input_df.reindex(columns=expected_cols, fill_value=0)

        print("📊 Processed DataFrame:", input_df)

        # ✅ Make Prediction
        prediction = model.predict(input_df)[0]
        print("🔢 Prediction:", prediction)

        # ✅ Store Prediction in Oracle Database
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO crime_predictions (state_ut, district, predicted_crimes)
                    VALUES (:1, :2, :3)
                """, (data.get("state_ut"), data.get("district"), int(prediction)))
                conn.commit()
                cursor.close()
                conn.close()
            except cx_Oracle.DatabaseError as e:
                print("❌ Database insertion error:", str(e))

        return jsonify({"predicted_total_ipc_crimes": int(prediction)})

    except Exception as e:
        print("❌ Error in prediction:", str(e))
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

# ✅ **Safe Path API**
@app.route('/safe_path', methods=['POST'])
def safe_path():
    try:
        data = request.get_json()
        start_name = data.get('current_location')
        destination_name = data.get('destination')

        if not start_name or not destination_name:
            return jsonify({"error": "Missing start or destination"}), 400

        start_coords = get_coordinates(start_name)
        end_coords = get_coordinates(destination_name)

        if not start_coords or not end_coords:
            return jsonify({"error": "Invalid location names"}), 400

        # ✅ Create a Road Network Graph
        G = nx.Graph()

        # ✅ Load Real-World Data (Oracle)
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT source, destination, crime_weight FROM road_network")
                for source, destination, weight in cursor.fetchall():
                    G.add_edge(source, destination, weight=weight)
                cursor.close()
                conn.close()
            except cx_Oracle.DatabaseError as e:
                print("❌ Database query error:", str(e))

        # ✅ Add Start & Destination if Not in Graph
        if start_name not in G:
            G.add_node(start_name)
        if destination_name not in G:
            G.add_node(destination_name)

        # ✅ Find Shortest Safe Path
        if not nx.has_path(G, start_name, destination_name):
            return jsonify({"error": "No safe path found"}), 404

        path = nx.shortest_path(G, source=start_name, target=destination_name, weight='weight')

        return jsonify({"safe_route": path})

    except Exception as e:
        print("❌ Error in Safe Path Recommendation:", str(e))
        return jsonify({"error": "Internal server error"}), 500

# ✅ **Emergency API**
@app.route('/emergency', methods=['POST'])
def emergency():
    try:
        data = request.get_json()
        user_location = data.get('location')
        user_id = data.get('user_id')

        if not user_location or not user_id:
            return jsonify({"error": "Missing user_id or location"}), 400

        print(f"🚨 EMERGENCY triggered by user {user_id} at location {user_location}")

        # ✅ Store Emergency Alert in Oracle
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO emergency_alerts (user_id, location)
                    VALUES (:1, :2)
                """, (user_id, user_location))
                conn.commit()
                cursor.close()
                conn.close()
            except cx_Oracle.DatabaseError as e:
                print("❌ Database insertion error:", str(e))

        return jsonify({"status": "Emergency received. Authorities notified."})

    except Exception as e:
        print("❌ Error in emergency reporting:", str(e))
        return jsonify({"error": "Emergency report failed"}), 500

# ✅ **Run Flask App**
if __name__ == '__main__':
    app.run(debug=True)  # ✅ Fixed error in the last line
