import pulp
import numpy as np

def optimize(n_locations:int, n_vehicles:int, vehicle_capacity:list[int]) -> list:
    distance_matrix = np.random.randint(1, 100, size=(n_locations, n_locations)).tolist()
    demands = [0] + np.random.randint(1, 10, size=(n_locations - 1)).tolist()
    time_windows = [(0, 100)] + [(np.random.randint(10, 50), np.random.randint(51, 100)) for _ in range(n_locations - 1)]

    # Define VRP model
    model = pulp.LpProblem("Vehicle_Routing_Problem", pulp.LpMinimize)

    # Decision Variables
    x = pulp.LpVariable.dicts("Route", [(i, j, k) for i in range(n_locations) for j in range(n_locations) for k in range(n_vehicles)], cat=pulp.LpBinary)
    y = pulp.LpVariable.dicts("Visit", [(i, k) for i in range(n_locations) for k in range(n_vehicles)], cat=pulp.LpBinary)

    t = pulp.LpVariable.dicts("Time", [i for i in range(n_locations)], lowBound=0, cat=pulp.LpContinuous)

    # Objective Function: Minimize total travel distance
    model += pulp.lpSum(distance_matrix[i][j] * x[i, j, k] for i in range(n_locations) for j in range(n_locations) for k in range(n_vehicles))

    # Constraints
    for i in range(1, n_locations):
        model += pulp.lpSum(y[i, k] for k in range(n_vehicles)) == 1  # Each location is visited exactly once

    for k in range(n_vehicles):
        model += pulp.lpSum(demands[i] * y[i, k] for i in range(n_locations)) <= vehicle_capacity[k]  # Capacity constraint
        model += pulp.lpSum(x[0, j, k] for j in range(1, n_locations)) == 1  # Each vehicle starts from depot
        model += pulp.lpSum(x[i, 0, k] for i in range(1, n_locations)) == 1  # Each vehicle returns to depot

    for i in range(n_locations):
        for k in range(n_vehicles):
            model += pulp.lpSum(x[i, j, k] for j in range(n_locations)) == y[i, k]  # Flow constraint

    for i in range(1, n_locations):
        for j in range(1, n_locations):
            for k in range(n_vehicles):
                if i != j:
                    model += t[j] >= t[i] + distance_matrix[i][j] - (1 - x[i, j, k]) * 1000  # Time window constraints

    for i in range(n_locations):
        model += t[i] >= time_windows[i][0]
        model += t[i] <= time_windows[i][1]

    # Solve the problem
    model.solve()

    # Extract Results
    routes = []
    for k in range(n_vehicles):
        route = []
        for i in range(n_locations):
            for j in range(n_locations):
                if pulp.value(x[i, j, k]) == 1:
                    route.append((i, j))
        routes.append(route)

    return routes

# TODO: Link with db data source, additional data source will be needed for number of vehicles available
# TODO: Link with Google Map Live Traffic, ref: migrate_live_traffic_data.py
# Sample Data (Replace with actual data)
n_locations = 10  # Number of delivery locations
n_vehicles = 3  # Number of available vehicles
vehicle_capacity = [50, 50, 50]  # Vehicle capacities
routes = optimize(n_locations, n_vehicles, vehicle_capacity)
print("Optimized Routes:", routes)
