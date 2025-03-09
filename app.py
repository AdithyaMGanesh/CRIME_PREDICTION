from flask import Flask, request, jsonify
import pickle

app = Flask(__name__)

# 1. Load your trained crime model (already created)
with open("crime_model.pkl", "rb") as f:
    model = pickle.load(f)

########################################
# 2. CRIME PREDICTION ENDPOINT (/predict)
########################################
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    # Convert the incoming data into the format your model expects.
    # Typically, you’ll do the same transformations (e.g., one-hot encoding).
    # For simplicity, assume the user sends everything in correct format or we do minimal checks.

    # Example minimal approach:
    import pandas as pd
    input_df = pd.DataFrame([data])

    # If you used get_dummies on 'state_ut' and 'district' (and possibly others), replicate that:
    if 'state_ut' in input_df.columns:
        input_df = pd.get_dummies(input_df, columns=['state_ut'], drop_first=True)
    if 'district' in input_df.columns:
        input_df = pd.get_dummies(input_df, columns=['district'], drop_first=True)

    # Align columns with the model’s training columns
    expected_cols = model.feature_names_in_
    input_df = input_df.reindex(columns=expected_cols, fill_value=0)

    # Get prediction
    prediction = model.predict(input_df)[0]

    return jsonify({"predicted_total_ipc_crimes": prediction})

########################################
# 3. SAFE PATH RECOMMENDATION ENDPOINT (/safe_path)
########################################
@app.route('/safe_path', methods=['POST'])
def safe_path():
    data = request.get_json()
    current_location = data.get('current_location')
    destination = data.get('destination')

    # Here you implement or call your route-finding logic.
    # For demonstration, we'll just return a placeholder route.
    # In a real scenario, you might do:
    #  - Graph-based pathfinding (Dijkstra, A*)
    #  - Weighted edges based on crime risk from your model
    #  - Integration with Google Maps / OpenStreetMap

    # Placeholder: "Safe route from X to Y"
    route_info = f"Safe route from {current_location} to {destination}"

    return jsonify({"safe_route": route_info})

########################################
# 4. EMERGENCY TAP ENDPOINT (/emergency)
########################################
@app.route('/emergency', methods=['POST'])
def emergency():
    data = request.get_json()
    user_location = data.get('location')
    user_id = data.get('user_id')  # if you want to track which user triggered it

    # In a real-world scenario:
    #  - Send SMS or email alerts using a service like Twilio, SendGrid, etc.
    #  - Log the event to a database
    #  - Possibly share the location with authorities

    # For demonstration, we'll just print to the console
    print(f"EMERGENCY triggered by user {user_id} at location {user_location}")

    return jsonify({"status": "Emergency received. Authorities notified."})

########################################
# 5. RUN THE FLASK APP
########################################
if __name__ == '__main__':
    app.run(debug=True)
