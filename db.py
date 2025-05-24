# db.py
import mysql.connector
from mysql.connector import Error
import pandas as pd

def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="course_dashboard"
        )
        return connection
    except Error as e:
        print("❌ Error connecting to MySQL:", e)
        return None

def run_query(query, params=None):
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()

    try:
        df = pd.read_sql(query, conn, params=params)
        return df
    except Error as e:
        print("❌ Query Error:", e)
        return pd.DataFrame()
    finally:
        conn.close()

def execute_query(query, params=None):
    conn = get_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return True
    except Error as e:
        print("❌ Execution Error:", e)
        return False
    finally:
        if conn.is_connected():
            conn.close()




# import mysql.connector
# from mysql.connector import Error

# def get_connection():
#     try:
#         connection = mysql.connector.connect(
#             host="localhost",
#             user="root",
#             password="",
#             database="streamdash"
#         )
#         return connection
#     except Error as e:
#         print("❌ Error connecting to MySQL:", e)
#         return None
