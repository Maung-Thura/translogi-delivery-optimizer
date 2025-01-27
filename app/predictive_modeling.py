import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error, r2_score
import os
import mysql.connector
import json
import pandas as pd
from pandas import DataFrame
from dotenv import load_dotenv


def retrieve_preprocessed_data(sql_json_file: str) -> DataFrame:
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
            cursor.execute(queries.get('select_preprocessed_delivery_transactions_all_columns'))
            results = cursor.fetchall()

            # Get column names from cursor description
            column_names = [column[0] for column in cursor.description]

            print("Successfully retrieved the data.")

            # Return a pandas DataFrame
            return  pd.DataFrame(results, columns=column_names)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("MySQL connection closed.")

def generate_model():
    # Fetch preprocessed delivery transaction data
    load_dotenv()
    os.environ['MYSQL_SERVER'] = 'localhost'
    data = retrieve_preprocessed_data('sql.json')

    # Feature selection
    features = [
        "agent_age", "agent_rating", "store_latitude", "store_longitude",
        "drop_latitude", "drop_longitude", "order_time", "pickup_time",
        "weather", "traffic", "vehicle", "area", "category",
        "avg_delivery_time_by_area", "avg_delivery_time_by_traffic_and_weather",
        "vehicle_capacity_utilization"
    ]
    target = "delivery_time"

    # Convert time features to numerical (seconds from midnight)
    data["order_time"] = pd.to_timedelta(data["order_time"]).dt.total_seconds()
    data["pickup_time"] = pd.to_timedelta(data["pickup_time"]).dt.total_seconds()

    # Splitting Data
    X = data[features]
    y = data[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Preprocessing: Encoding categorical features and scaling numerical features
    numeric_features = ["agent_age", "agent_rating", "store_latitude", "store_longitude",
                        "drop_latitude", "drop_longitude", "order_time", "pickup_time",
                        "avg_delivery_time_by_area", "avg_delivery_time_by_traffic_and_weather",
                        "vehicle_capacity_utilization"]
    categorical_features = ["weather", "traffic", "vehicle", "area", "category"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    # Building Pipeline with Random Forest Regressor
    model = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("regressor", RandomForestRegressor(n_estimators=100, random_state=42))
    ])

    # Training the Model
    model.fit(X_train, y_train)

    # Predictions and Evaluation
    y_pred = model.predict(X_test)
    rmse = root_mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # Save Model
    model_filename = "delivery_time_model.pkl"
    with open(model_filename, "wb") as file:
        pickle.dump(model, file)

    print(f"Model saved as {model_filename}")
    print(f"RMSE: {rmse}, R² Score: {r2}")
