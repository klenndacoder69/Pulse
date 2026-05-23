import requests
import time
import random

URL = "http://localhost:8080/ingest"

print("Transmitting telemetry data. Press Ctrl+C to stop.")

try:
    while True:
        # Simulate a small cluster of 5 servers
        server_name = f"ws-{random.randint(1, 5):03d}"
        
        # Baseline normal operations
        cpu = round(random.uniform(10.0, 45.0), 1)
        status = "healthy"
        
        # Simulate a sudden CPU spike anomaly 10% of the time
        if random.random() > 0.90:
            cpu = round(random.uniform(85.0, 99.9), 1)
            status = "warning"
            print(f"⚠️  ANOMALY DETECTED on {server_name}")

        payload = {
            "server_id": server_name,
            "cpu_usage": cpu,
            "status": status
        }

        try:
            res = requests.post(URL, json=payload)
            print(f"[{time.strftime('%H:%M:%S')}] {server_name} | CPU: {cpu}% | HTTP {res.status_code}")
        except Exception as e:
            print(f"Connection dropped: {e}")
            
        # Sleep for 1 second to create a steady trickle
        time.sleep(1)

except KeyboardInterrupt:
    print("\nAgent offline.")
