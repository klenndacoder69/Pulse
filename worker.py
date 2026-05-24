import json
import redis
import psycopg2
import time
import os
from psycopg2.extras import execute_values

def setup_database(cursor):
    """Creates the telemetry table if it doesn't already exist."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS server_health (
            id SERIAL PRIMARY KEY,
            server_id VARCHAR(50) NOT NULL,
            cpu_usage FLOAT NOT NULL,
            status VARCHAR(20) NOT NULL,
            ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("Database schema verified.")

def main():
    redis_host = os.environ.get("REDIS_HOST", "127.0.0.1")
    db_host = os.environ.get("DB_HOST", "127.0.0.1")
    # decode_responses=True automatically converts byte payloads to strings
    r = redis.Redis(host=redis_host, port=6379, decode_responses=True)
    
    pg_conn = psycopg2.connect(
        host=db_host, port="5432", dbname="telemetry",
        user=os.environ.get("POSTGRES_USER", "admin"),
        password=os.environ.get("DB_PASSWORD", "secret")
    )
    pg_conn.autocommit = True
    cursor = pg_conn.cursor()

    setup_database(cursor)
    print("Worker started. Listening for telemetry on Redis queue...")

    # 3. The Infinite Daemon Loop
    while True:
        try:
            
            # brpop to ensure that the thread only wakes up when redis has new data
            result = r.brpop("telemetry_queue", timeout=0)
            
            if result:
                # result is a tuple: (queue_name, data)
                _, data = result
                payload = json.loads(data)

                cursor.execute("""
                    INSERT INTO server_health (server_id, cpu_usage, status)
                    VALUES (%s, %s, %s);
                """, (payload['server_id'], payload['cpu_usage'], payload['status']))

                print(f"Flushed to DB: {payload['server_id']} (CPU: {payload['cpu_usage']}%)")

        except Exception as e:
            print(f"⚠️ Error processing log: {e}")
            # prevents spam when db dies
            time.sleep(1)

if __name__ == "__main__":
    main()
