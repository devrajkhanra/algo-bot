# algo-bot/services/strategy-service/strategies/l99_strategy.py

from enum import Enum
import datetime
from strategies.base_strategy import BaseStrategy

class L99State(Enum):
    PRE_MARKET = 0          # Before 9:15 AM
    CALCULATING_ORB = 1     # 9:15 AM to 9:30 AM (Building the range)
    HUNTING = 2             # 9:30 AM onwards (Waiting for a breakout)
    FAKEOUT_WATCH = 3       # Price broke out. Waiting to see if it reverses.
    ARMED = 4               # Price reversed back in. The trap is set.
    FIRED = 5               # The trap triggered. We are in a trade.
    DONE_FOR_DAY = 6        # Max trades hit or time is up.

class L99Strategy(BaseStrategy):
    def __init__(self, instrument_token="NSE_INDEX|Nifty 50"):
        super().__init__(instrument_token, strategy_id="L99_GAMMA_BLAST")
        
        # --- Core State ---
        self.state = L99State.PRE_MARKET
        
        # --- Critical Levels (Calculated dynamically) ---
        self.orb_high = float('-inf')
        self.orb_low = float('inf')
        
        # --- Trap Variables ---
        self.trigger_direction = None # 'UPSIDE' or 'DOWNSIDE'
        self.fakeout_start_time = None
        
        # Note: True VWAP requires Volume. Since our current 'ltpc' feed only 
        # gives price, we will use the pure Price Action High/Low of the first 15 mins.
        # We can upgrade to a Volume feed later if needed.

    def on_tick(self, tick_data):
        """
        This is the main router. Every time a Nifty tick arrives, 
        it checks the current state and routes it to the correct logic block.
        """
        ltp = tick_data.get('lastTradedPrice', 0.0)
        timestamp_ms = tick_data.get('timestamp', 0)
        
        # Convert timestamp to human-readable IST time
        tick_time = datetime.datetime.fromtimestamp(timestamp_ms / 1000.0)
        
        # Ensure we only process market hours (9:15 AM to 3:30 PM)
        # (For weekend testing, you can comment this block out later)
        if tick_time.hour < 9 or (tick_time.hour == 9 and tick_time.minute < 15):
            self.state = L99State.PRE_MARKET
            return None
            
        if tick_time.hour >= 15 and tick_time.minute >= 15:
            if self.state != L99State.DONE_FOR_DAY:
                print(f"[{self.strategy_id}] 🛑 Market closing. Shutting down for the day.")
                self.state = L99State.DONE_FOR_DAY
            return None

        # Route the tick based on the current state
        if self.state == L99State.PRE_MARKET:
            self.state = L99State.CALCULATING_ORB
            print(f"[{self.strategy_id}] 🟢 Market Open! Entering Phase 1: CALCULATING ORB.")
            
        elif self.state == L99State.CALCULATING_ORB:
            self._handle_calculating_orb(ltp, tick_time)
            
        elif self.state == L99State.HUNTING:
            self._handle_hunting(ltp, tick_time)
            
        elif self.state == L99State.FAKEOUT_WATCH:
            self._handle_fakeout_watch(ltp, tick_time)
            
        elif self.state == L99State.ARMED:
            return self._handle_armed(ltp, tick_time)

        return None
    
    # ---------------------------------------------------------
    # STATE LOGIC HANDLERS
    # ---------------------------------------------------------

    def _handle_calculating_orb(self, ltp, tick_time):
        """
        PHASE 1: 9:15 to 9:30. Find the absolute High and Low of the Opening Range.
        """
        # Update the High and Low of the day so far
        if ltp > self.orb_high: self.orb_high = ltp
        if ltp < self.orb_low:  self.orb_low = ltp

        # Check if 15 minutes have passed
        if tick_time.minute >= 30:
            self.state = L99State.HUNTING
            print(f"[{self.strategy_id}] 🎯 ORB Established! High: {self.orb_high} | Low: {self.orb_low}")
            print(f"[{self.strategy_id}] 🐺 Transitioning to HUNTING state. Waiting for fakeout...")


    def _handle_hunting(self, ltp, tick_time):
        """
        PHASE 2A: Price breaks the ORB. Most retail buys here. We watch and wait.
        """
        # Upside Breakout Detected
        if ltp > self.orb_high:
            self.trigger_direction = 'UPSIDE'
            self.fakeout_start_time = tick_time
            self.state = L99State.FAKEOUT_WATCH
            print(f"[{self.strategy_id}] ⚠️ UPSIDE BREAKOUT at {ltp}. Option buyers rushing in. Watching for reversal.")
            
        # Downside Breakout Detected
        elif ltp < self.orb_low:
            self.trigger_direction = 'DOWNSIDE'
            self.fakeout_start_time = tick_time
            self.state = L99State.FAKEOUT_WATCH
            print(f"[{self.strategy_id}] ⚠️ DOWNSIDE BREAKOUT at {ltp}. Option buyers rushing in. Watching for reversal.")


    def _handle_fakeout_watch(self, ltp, tick_time):
        """
        PHASE 2B: The breakout happened. Did it fail?
        L99 Rule: Price must reverse back *inside* the range within a short time (e.g., 10 mins).
        """
        time_elapsed = (tick_time - self.fakeout_start_time).total_seconds() / 60.0

        # If it stays outside the range for more than 10 minutes, it's a real trend. Not a trap.
        if time_elapsed > 10.0:
            print(f"[{self.strategy_id}] ❌ Trend confirmed. Not a fakeout. Resetting to HUNTING.")
            self.state = L99State.HUNTING
            return

        # Check for the Reversal (The Trap is Set)
        if self.trigger_direction == 'UPSIDE' and ltp < self.orb_high:
            self.state = L99State.ARMED
            print(f"[{self.strategy_id}] 🪤 CE BUYERS TRAPPED! Price fell back below {self.orb_high}. System ARMED.")
            
        elif self.trigger_direction == 'DOWNSIDE' and ltp > self.orb_low:
            self.state = L99State.ARMED
            print(f"[{self.strategy_id}] 🪤 PE BUYERS TRAPPED! Price rose back above {self.orb_low}. System ARMED.")


    def _handle_armed(self, ltp, tick_time):
        """
        PHASE 2C: The Ignition. The option sellers are comfortable. 
        If price crosses the trigger line *again*, it triggers a massive short-covering squeeze.
        """
        if self.trigger_direction == 'UPSIDE' and ltp > self.orb_high:
            self.state = L99State.FIRED
            print(f"[{self.strategy_id}] 🔥 GAMMA BLAST IGNITED! Upside trigger {self.orb_high} breached again.")
            print(f"[{self.strategy_id}] 👉 (In Phase 2, we will buy the CE Option here!)")
            # return self.create_order_intent(...)  <- We will add this in Sprint 2
            
        elif self.trigger_direction == 'DOWNSIDE' and ltp < self.orb_low:
            self.state = L99State.FIRED
            print(f"[{self.strategy_id}] 🔥 GAMMA BLAST IGNITED! Downside trigger {self.orb_low} breached again.")
            print(f"[{self.strategy_id}] 👉 (In Phase 2, we will buy the PE Option here!)")
            # return self.create_order_intent(...)  <- We will add this in Sprint 2
            
        return None