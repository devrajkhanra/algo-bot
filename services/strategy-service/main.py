# algo-bot/services/strategy-service/main.py

import redis
import json
import os
from strategies.l99_strategy import L99Strategy

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Load the Institutional State Machine
ACTIVE_STRATEGIES = [
    L99Strategy(instrument_token="NSE_INDEX|Nifty 50")
]

def start_engine():
    print("🧠 Starting Quantitative Engine...")
    r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    
    try:
        r.ping()
        print("✅ Connected to Redis Event Bus.")
    except redis.ConnectionError:
        print("❌ Could not connect to Redis.")
        return

    pubsub = r.pubsub()
    pubsub.psubscribe("market.tick.*")
    print("📡 Listening for market data...")

    for message in pubsub.listen():
        if message['type'] == 'pmessage':
            try:
                tick_data = json.loads(message['data'])
                token = tick_data.get('instrumentToken')
                
                # Route the tick to the strategy
                for strategy in ACTIVE_STRATEGIES:
                    if strategy.instrument_token == token:
                        intent = strategy.on_tick(tick_data)
                        
                        # We will handle the intent in Sprint 2
                        if intent:
                            pass 
                            
            except Exception as e:
                print(f"[Error] Execution failed: {e}")

if __name__ == "__main__":
    start_engine()