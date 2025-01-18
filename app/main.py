import migrate_delivery_transactions as mdt
import migrate_live_traffic_data as mlt
from migrate_live_traffic_data import Route

mdt.migrate('sql.json')

order_id = 'ltwr528697521'
route = Route("Joe S Feb 14 Morning Delivery", (22.745049, 75.892471), (22.835049, 75.982471))
delivery_route_map = {order_id: route}
mlt.migrate(delivery_route_map, 'sql.json')


# gmaps = googlemaps.Client(key = "AIzaSyD5hAlCfEe5TDWxD3fRrrDMqFyXopD_TNk")
#
# response = gmaps.distance_matrix((22.745049, 75.892471),(22.765049, 75.912471), departure_time = "now")
# print(response)
#
# date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# distance = round((response['rows'][0]['elements'][0]['distance']['value']) / 1000, 2) # km
# duration_traffic = round((response['rows'][0]['elements'][0]['duration_in_traffic']['value']) / 60,  2) # minutes
# velocity = round((distance / duration_traffic) * 60, 2) # km/hour
# avg_delay = round(duration_traffic / distance, 2) # minutes/km
#
# print(date_time, distance, duration_traffic, velocity, avg_delay)