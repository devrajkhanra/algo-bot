# algo-bot/services/strategy-service/simulator.py

import redis
import json
import time
import datetime

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def publish_fake_tick(price, hour, minute):
    """Creates a fake tick with a specific time and blasts it to Redis"""
    # Create a fake IST timestamp for today
    now = datetime.datetime.now()
    fake_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    timestamp_ms = int(fake_time.timestamp() * 1000)

    tick = {
        "instrumentToken": "NSE_INDEX|Nifty 50",
        "lastTradedPrice": price,
        "timestamp": timestamp_ms
    }
    
    r.publish("market.tick.NSE_INDEX|Nifty 50", json.dumps(tick))
    print(f"--> Sent Tick: {hour:02d}:{minute:02d} | Price: {price}")
    time.sleep(1.5) # Pause so we can read the output

print("🚀 Starting L99 Gamma Trap Simulation...\n")

# PHASE 1: The Opening Range (9:15 to 9:30)
publish_fake_tick(24000.0, 9, 15)  # Market Open
publish_fake_tick(24050.0, 9, 20)  # Establishes High
publish_fake_tick(23950.0, 9, 25)  # Establishes Low
publish_fake_tick(24020.0, 9, 30)  # 9:30 hits! ORB is locked.

# PHASE 2: The Fakeout Breakout
publish_fake_tick(24060.0, 9, 35)  # UPSIDE BREAKOUT! (Retail buys CE)

# PHASE 3: The Trap (Reversal back into range)
publish_fake_tick(24040.0, 9, 38)  # Reverses below ORB High. (Trap Armed!)

# PHASE 4: The Gamma Blast Ignition
publish_fake_tick(24065.0, 9, 42)  # Crosses back above. IGNITION!

print("\n✅ Simulation Complete.")