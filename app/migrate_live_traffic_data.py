import googlemaps
from datetime import datetime
import os
import mysql.connector
import json
from dataclasses import dataclass

@dataclass
class Route:
    route_name: str
    origins: tuple[float, float] # latitude, longitude
    destinations: tuple[float, float] # latitude, longitude

@dataclass
class Traffic:
    id: int
    route_name: str
    date_time: str
    distance: float
    duration_traffic: float
    velocity: float
    avg_delay: float

class NoRouteFound(Exception):
    pass

def migrate(delivery_route_map: dict[str, Route], sql_json_file:str):
    delivery_traffic_map: dict[str, Traffic] = {}
    for order_id, route in delivery_route_map.items():
        try:
            traffic = calculate_traffic(route)
            delivery_traffic_map[order_id] = traffic
        except NoRouteFound as nrf:
            print(nrf)
    persist(delivery_traffic_map, sql_json_file)

def calculate_traffic(route: Route) -> Traffic:
    gmaps_api_key = os.getenv("GOOGLE_MAP_API_KEY")
    gmaps = googlemaps.Client(key = gmaps_api_key)

    response = gmaps.distance_matrix(route.origins, route.destinations, departure_time = "now")

    if response['rows'][0]['elements'][0]['status'] == 'ZERO_RESULTS':
        raise NoRouteFound(f'Google Map cannot find a route from {route.origins} to {route.destinations}')

    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    distance = round((response['rows'][0]['elements'][0]['distance']['value']) / 1000, 2) # km
    duration_traffic = round((response['rows'][0]['elements'][0]['duration_in_traffic']['value']) / 60,  2) # minutes
    velocity = round((distance / duration_traffic) * 60, 2) # km/hour
    avg_delay = round(duration_traffic / distance, 2) # minutes/km

    return Traffic(0, route.route_name, date_time, distance, duration_traffic, velocity, avg_delay)

def persist(delivery_traffic_map: dict[str, Traffic], sql_json_file: str):
    # Retrieve environment variables
    db_host = os.getenv("MYSQL_SERVER")
    db_name = os.getenv("MYSQL_DATABASE")
    db_user = os.getenv("MYSQL_USER")
    db_password = os.getenv("MYSQL_PASSWORD")

    # Connect to MySQL
    try:
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        print("Connected to MySQL successfully!")

        with open(sql_json_file, 'r') as f:
            queries = json.load(f)

        if connection.is_connected():
            cursor = connection.cursor()

            # Insert data into the table
            for order_id, traffic in delivery_traffic_map.items():
                cursor.execute(queries.get('insert_into_traffic_table'), (traffic.route_name, traffic.date_time, traffic.distance, traffic.duration_traffic, traffic.velocity, traffic.avg_delay))
                traffic_id = cursor.lastrowid
                cursor.execute(queries.get('insert_into_delivery_traffic_table'), (order_id, traffic_id))

            # Commit the transaction
            connection.commit()
            print("Data inserted successfully into MySQL database.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("MySQL connection closed.")

    # test route 2025/01/16 23:12:49 4.4 14.7 18.0 3.34