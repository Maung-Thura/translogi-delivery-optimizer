from flask import Flask, request, jsonify , render_template
import pickle
import numpy as np
import route_optimizer as rop

app = Flask(__name__)

# TODO: change Flask to production ready server, Gunicorn, Waitress, uWSGI, Nginx, Apache, etc.

# Load trained model
model_path = "delivery_time_model.pkl"
with open(model_path, "rb") as file:
    model = pickle.load(file)

# TODO: link with client request
# Sample VRP data
n_locations = 10
n_vehicles = 3
vehicle_capacity = [50, 50, 50]
distance_matrix = np.random.randint(1, 100, size=(n_locations, n_locations)).tolist()
demands = [0] + np.random.randint(1, 10, size=(n_locations - 1)).tolist()
time_windows = [(0, 100)] + [(np.random.randint(10, 50), np.random.randint(51, 100)) for _ in range(n_locations - 1)]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict_delivery_time():
    data = request.json
    features = [data[key] for key in data]
    prediction = model.predict([features])[0]
    return jsonify({"predicted_delivery_time": prediction})

@app.route('/optimize_routes', methods=['GET'])
def optimize_routes():
    # TODO: request.data
    routes = rop.optimize(n_locations, n_vehicles, vehicle_capacity)
    return jsonify({"optimized_routes": routes})


if __name__ == '__main__':
    app.run(debug=True)
