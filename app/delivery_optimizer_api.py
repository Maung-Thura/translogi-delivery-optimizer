from flask import Flask, request, jsonify , render_template
import pickle
import numpy as np
import route_optimizer as rop

app = Flask(__name__)

# TODO: change Flask to production ready server, Gunicorn, Waitress, uWSGI, Nginx, Apache, etc.

@app.route('/')
def home():
    return render_template('index.html')

# Load the trained model
with open("delivery_time_model.pkl", "rb") as model_file:
    model = pickle.load(model_file)

@app.route('/predict_delivery_time', methods=['POST'])
def predict_delivery_time():
    try:
        data = request.get_json()

        # Extract features from the request
        numeric_features = [
            "agent_age", "agent_rating", "store_latitude", "store_longitude",
            "drop_latitude", "drop_longitude", "order_time", "pickup_time",
            "avg_delivery_time_by_area", "avg_delivery_time_by_traffic_and_weather",
            "vehicle_capacity_utilization"
        ]
        categorical_features = ["weather", "traffic", "vehicle", "area", "category"]

        # Prepare the feature array
        numeric_values = [float(data[feature]) for feature in numeric_features]
        categorical_values = [data[feature] for feature in categorical_features]

        input_features = np.array(numeric_values + categorical_values).reshape(1, -1)

        # Predict delivery time
        predicted_time = model.predict(input_features)[0]

        return jsonify({"predicted_time": predicted_time})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/optimize_routes', methods=['POST'])
def optimize_routes():
    if request.content_type != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 415  # Explicitly handle wrong content type

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        n_locations = int(data.get('n_locations', 0))
        n_vehicles = int(data.get('n_vehicles', 0))
        vehicle_capacity = data.get('vehicle_capacity', [])

        if not isinstance(vehicle_capacity, list) or not all(isinstance(i, int) for i in vehicle_capacity):
            return jsonify({"error": "vehicle_capacity must be a list of integers"}), 400

        optimized_routes = rop.optimize(n_locations, n_vehicles, vehicle_capacity)

        return jsonify({"optimized_routes": optimized_routes})

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Handle any unexpected errors

def main():
    app.run(debug=True)

if __name__ == '__main__':
    main()
