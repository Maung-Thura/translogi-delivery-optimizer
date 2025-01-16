import kagglehub
import os
import pandas as pd
import mysql.connector
from pandas import DataFrame
import json
import numpy as np

def migrate(sql_json_file:str):
    data = download_delivery_transactions()
    data = prepare_for_db_compatibility(data)
    persist(data, sql_json_file)

def download_delivery_transactions() -> DataFrame:
    path = kagglehub.dataset_download("sujalsuthar/amazon-delivery-dataset")

    # Load the CSV file
    file_path = path + '/amazon_delivery.csv'
    return pd.read_csv(file_path)

def prepare_for_db_compatibility(data:DataFrame) -> DataFrame:
    # Replace NaN, NaT with None
    return data.replace(np.nan, None).replace(pd.NaT, None).replace('NaN ', None)

def persist(data:DataFrame, sql_json_file:str):
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
            cursor.execute(queries.get('create_delivery_transaction_table_if_not_exists'))
            cursor.execute(queries.get('empty_delivery_transaction_table'))

            # Insert data into the table
            for _, row in data.iterrows():
                cursor.execute(queries.get('insert_into_delivery_transaction_table_all_columns'), tuple(row))

            # Commit the transaction
            connection.commit()
            print("Data inserted successfully into MySQL database.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("MySQL connection closed.")