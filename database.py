import mysql.connector
import pandas as pd

def get_connection():

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345678",
        database="OLA_Ride_Analysis"
    )
    return conn

def run_query(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df