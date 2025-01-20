import os
import mysql.connector
import json
import numpy as np
import pandas as pd
from pandas import DataFrame
from dotenv import load_dotenv
from sklearn.preprocessing import MinMaxScaler

def init():
    load_dotenv()
    os.environ['MYSQL_SERVER'] = 'localhost'

def retrieve_raw_data(sql_json_file: str) -> DataFrame:
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
            cursor.execute(queries.get('select_delivery_transactions_all_columns'))
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

def detect_missing_values(data:DataFrame):
    # Find columns with missing values
    missing_values = data.isnull().sum()

    # Filter columns that have missing values
    missing_columns = missing_values[missing_values > 0]

    # Display the columns with missing values and their counts
    print("Columns with Missing Values:")
    print(missing_columns)

def detect_outliers_iqr(data:DataFrame, column):
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Find outliers
    outliers = data[(data[column] < lower_bound) | (data[column] > upper_bound)]

    print(f"Column: {column}")
    print(f"Lower Bound: {lower_bound}, Upper Bound: {upper_bound}")
    print(f"Number of Outliers: {outliers.shape[0]}")
    # print(f"Outliers: {outliers}")
    print("-" * 50)

def handle_missing_values(data:DataFrame):
    # Impute missing 'agent_rating' with the mean
    data['agent_rating'] = data['agent_rating'].fillna(data['agent_rating'].mean())

    # Impute missing 'weather' and 'traffic' with the mode
    data['weather'] = data['weather'].fillna(data['weather'].mode()[0])
    data['traffic'] = data['traffic'].fillna(data['traffic'].mode()[0])

    # Impute missing 'order_time' with 00:00:00 midnight
    midnight = np.timedelta64(0, 'h')
    data['order_time'] = data['order_time'].fillna(midnight)

def handle_outliers(data:DataFrame):
    # Limit 'agent_rating' within the valid range (1-5)
    data['agent_rating'] = data['agent_rating'].clip(lower=1, upper=5)

    # Limit 'delivery_time' within the valid range (0-265)
    data['delivery_time'] = data['delivery_time'].clip(lower=0, upper=265)

def normalize_columns(data:DataFrame, columns_names:list[str]):
    scaler = MinMaxScaler()
    data[columns_names] = scaler.fit_transform(data[columns_names])

def add_average_x_by_y(data:DataFrame, x_column_name:str, y_column_name:str, avg_column_name:str):
    avg_x_by_y = data.groupby(y_column_name)[x_column_name].mean().to_dict()
    data[avg_column_name] =data[y_column_name].map(avg_x_by_y)

def add_average_x_by_y_list(data:DataFrame, x_column_name:str, y_columns_names:list[str], avg_column_name:str):
    avg_x_by_y = data.groupby(y_columns_names)[x_column_name].mean().to_dict()
    data[avg_column_name] = data.apply(lambda row: avg_x_by_y.get(tuple(row[col] for col in y_columns_names)), axis=1)

def add_vehicle_capacity_utilization(data:DataFrame, vehicle_capacity:dict[str,float], new_column_name:str):
    data[new_column_name] = data['delivery_time'] / data['vehicle'].map(vehicle_capacity)

def trim_string_values(data:DataFrame, column_name:str):
    data[column_name] = data[column_name].str.strip()

def save_preprocessed_data(data:DataFrame, sql_json_file:str):
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
            cursor.execute(queries.get('empty_preprocessed_delivery_transaction_table'))

            # Insert data into the table
            for _, row in data.iterrows():
                cursor.execute(queries.get('insert_into_preprocessed_delivery_transaction_table_all_columns'), tuple(row))

            # Commit the transaction
            connection.commit()
            print("Preprocessed data inserted successfully into MySQL database.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("MySQL connection closed.")
