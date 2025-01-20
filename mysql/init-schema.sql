CREATE SCHEMA IF NOT EXISTS translogi_delivery_db;
CREATE TABLE IF NOT EXISTS translogi_delivery_db.delivery_transaction (order_id VARCHAR(255) PRIMARY KEY, agent_age INT, agent_rating FLOAT, store_latitude DECIMAL(10,8), store_longitude DECIMAL(11,8), drop_latitude DECIMAL(10,8), drop_longitude DECIMAL(11,8), order_date DATE, order_time TIME, pickup_time TIME, weather VARCHAR(50), traffic VARCHAR(50), vehicle VARCHAR(50), area VARCHAR(50), delivery_time INT, category VARCHAR(50));
CREATE TABLE IF NOT EXISTS translogi_delivery_db.traffic(traffic_id BIGINT PRIMARY KEY AUTO_INCREMENT, route_name TEXT, date_time DATETIME, distance DECIMAL(10,2),  duration_traffic DECIMAL(10,2), velocity DECIMAL(10,2), avg_delay DECIMAL(10,2));
CREATE TABLE IF NOT EXISTS translogi_delivery_db.delivery_traffic(order_id varchar(255), traffic_id BIGINT, PRIMARY KEY (order_id, traffic_id), CONSTRAINT fk_order_id FOREIGN KEY (order_id) REFERENCES translogi_delivery_db.delivery_transaction (order_id) ON DELETE CASCADE, CONSTRAINT fk_traffic_id FOREIGN KEY (traffic_id) REFERENCES translogi_delivery_db.traffic (traffic_id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS translogi_delivery_db.preprocessed_delivery_transaction (agent_age INT, agent_rating FLOAT, store_latitude DECIMAL(10,8), store_longitude DECIMAL(11,8), drop_latitude DECIMAL(10,8), drop_longitude DECIMAL(11,8), order_date DATE, order_time TIME, pickup_time TIME, weather VARCHAR(50), traffic VARCHAR(50), vehicle VARCHAR(50), area VARCHAR(50), delivery_time INT, category VARCHAR(50), avg_delivery_time_by_area DECIMAL(10,2), avg_delivery_time_by_traffic_and_weather DECIMAL(10,2), vehicle_capacity_utilization DECIMAL(10,2));