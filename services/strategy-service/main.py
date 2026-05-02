# algo-bot/services/strategy-service/main.py

import redis
import json
import os
import time

# Connect to our local Docker Redis instance
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

def process_tick(tick_data):
    """
    This is where we will route data to specific strategies.
    For now, we just verify the data is arriving.
    """
    instrument = tick_data.get('instrumentToken', 'UNKNOWN')
    ltp = tick_data.get('lastTradedPrice', 0.0)
    print(f"[Strategy Engine] 📈 Tick received | {instrument} | LTP: {ltp}")

def start_event_loop():
    print("🧠 Starting Strategy Service (Python)...")
    
    # decode_responses=True automatically decodes Redis byte strings to UTF-8
    r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    
    try:
        r.ping()
        print("✅ Connected to Redis Event Bus.")
    except redis.ConnectionError:
        print("❌ Could not connect to Redis. Is the Docker container running?")
        return

    pubsub = r.pubsub()
    # Subscribe to the exact topic pattern we defined in our shared TypeScript contracts
    pubsub.psubscribe("market.tick.*")
    print("📡 Listening for market data...")

    # Blocking event loop to listen for ticks
    for message in pubsub.listen():
        if message['type'] == 'pmessage':
            try:
                # The data comes in as a JSON string from the Node.js data-service
                tick_data = json.loads(message['data'])
                process_tick(tick_data)
            except json.JSONDecodeError:
                print("[Error] Received malformed JSON payload.")
            except Exception as e:
                print(f"[Error] Strategy execution failed: {e}")

if __name__ == "__main__":
    start_event_loop()