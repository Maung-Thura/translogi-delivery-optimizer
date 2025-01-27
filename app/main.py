import migrate_delivery_transactions as mdt
import migrate_live_traffic_data as mlt
from migrate_live_traffic_data import Route
import predictive_modeling as pm

# migrate delivery transactions
mdt.migrate('sql.json')

# migrate live Google Map Live traffic data
delivery_route_map = {}
order_id = 'ialx566343618'
route = Route("Joe F Mar 19 Morning Delivery", (22.745049, 75.892471), (22.765049, 75.912471))
delivery_route_map[order_id] = route

order_id = 'akqg208421122'
route = Route("Kathleen K Mar 25 Evening Delivery", (12.913041, 77.683237), (13.043041, 77.813237))
delivery_route_map[order_id] = route

mlt.migrate(delivery_route_map, 'sql.json')

# generate predictive model
pm.generate_model()
