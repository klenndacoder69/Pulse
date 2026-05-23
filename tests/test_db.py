import psycopg2
from psycopg2 import OperationalError

def test_connection():
    try:
        connection = psycopg2.connect(
            host="127.0.0.1",
            port="5432",
            database="telemetry",
            user="admin",
            password="secret"
        )
        
        cursor = connection.cursor()
        
        cursor.execute("SELECT version();")
        
        record = cursor.fetchone()
        print(f"Success! Connected to database.\nDatabase Info: {record[0]}")
        
    except OperationalError as e:
        print(f"Connection failed: {e}")
        
    finally:
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    test_connection()
