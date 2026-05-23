#made with ai

import asyncio
import aiohttp
import time
import random

# Configuration
URL = "http://localhost:8080/ingest"
TOTAL_REQUESTS = 10000
# We cap concurrent connections to avoid exhausting your Windows/WSL ephemeral ports
CONCURRENT_CONNECTIONS = 500

def generate_payload():
    """Generates a randomized, realistic telemetry log."""
    return {
        "server_id": f"ws-{random.randint(1, 100):03d}",
        "cpu_usage": round(random.uniform(5.0, 99.9), 1),
        "status": random.choice(["healthy", "warning", "critical"])
    }

async def fire_request(session):
    """Fires a single POST request and returns the HTTP status code."""
    payload = generate_payload()
    try:
        async with session.post(URL, json=payload) as response:
            return response.status
    except Exception as e:
        return 500 # Count networking drops as server errors

async def main():
    print(f"🚀 Preparing to blast {URL} with {TOTAL_REQUESTS} requests...")

    # Configure the connection pool limit
    connector = aiohttp.TCPConnector(limit=CONCURRENT_CONNECTIONS)

    start_time = time.time()

    async with aiohttp.ClientSession(connector=connector) as session:
        # Build the list of asynchronous tasks
        tasks = [fire_request(session) for _ in range(TOTAL_REQUESTS)]

        print("🔥 Firing payloads...")
        # Gather executes them all concurrently
        results = await asyncio.gather(*tasks)

    end_time = time.time()
    duration = end_time - start_time

    # Calculate metrics
    rps = TOTAL_REQUESTS / duration
    successes = sum(1 for r in results if r == 202)
    failures = TOTAL_REQUESTS - successes

    print("\n" + "="*30)
    print("📈 LOAD TEST RESULTS")
    print("="*30)
    print(f"⏱️  Time Elapsed: {duration:.2f} seconds")
    print(f"⚡ Throughput:   {rps:.2f} Requests Per Second (RPS)")
    print(f"✅ Successes:    {successes} (HTTP 202)")
    print(f"❌ Failures:     {failures}")
    print("="*30)

if __name__ == "__main__":
    # Suppress Windows/WSL specific asyncio loop closing errors if they occur
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    asyncio.run(main())
