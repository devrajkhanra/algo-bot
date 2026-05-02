# algo-bot/services/strategy-service/backtester.py

import pandas as pd
import datetime
from strategies.l99_strategy import L99Strategy, L99State

def run_spot_backtest(csv_path):
    print(f"📊 Loading historical data from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Ensure date column is properly parsed
    df['date'] = pd.to_datetime(df['date'])
    
    # Sort chronologically just in case
    df = df.sort_values('date').reset_index(drop=True)
    
    strategy = L99Strategy(instrument_token="NSE_INDEX|Nifty 50")
    
    total_trades = 0
    winning_trades = 0
    total_spot_points = 0.0
    
    entry_price = 0.0
    entry_time = None
    
    print("🚀 Starting Event-Driven Backtest Simulation...\n")

    for index, row in df.iterrows():
        base_time = row['date']
        
        # Microstructure Hack: Interpolate 4 ticks out of the 5-min candle
        # We assume the path is Open -> High -> Low -> Close (or vice versa).
        # We add fake milliseconds so the strategy processes them in order.
        ticks = [
            (row['open'], base_time + datetime.timedelta(seconds=0)),
            (row['high'], base_time + datetime.timedelta(seconds=10)),
            (row['low'],  base_time + datetime.timedelta(seconds=20)),
            (row['close'], base_time + datetime.timedelta(seconds=30))
        ]

        for price, tick_time in ticks:
            tick_data = {
                'lastTradedPrice': price,
                'timestamp': int(tick_time.timestamp() * 1000)
            }
            
            # Feed the tick to the brain
            strategy.on_tick(tick_data)
            
            # --- BACKTEST EXECUTION INTERCEPTOR ---
            
            # 1. Detect an Entry (The Trap Ignited)
            if strategy.state == L99State.FIRED and entry_price == 0.0:
                entry_price = price
                entry_time = tick_time
                print(f"[{tick_time}] 🟢 ENTERED TRADE at {entry_price:.2f} (Direction: {strategy.trigger_direction})")
                
            # 2. Detect an Exit (Time Stop / Next Candle Exit)
            # Since we don't have option ROC data, we will simulate a simple 15-minute Time Stop for the Spot test.
            elif entry_price > 0.0 and (tick_time - entry_time).total_seconds() >= 900: # 15 minutes
                exit_price = price
                
                # Calculate PnL based on direction
                if strategy.trigger_direction == 'UPSIDE':
                    points = exit_price - entry_price # We went Long on breakout
                else:
                    points = entry_price - exit_price # We went Short on breakdown
                    
                total_spot_points += points
                total_trades += 1
                if points > 0:
                    winning_trades += 1
                    
                print(f"[{tick_time}] 🔴 EXITED TRADE at {exit_price:.2f} | Points: {points:.2f}")
                
                # Reset for next trade
                entry_price = 0.0
                strategy.state = L99State.DONE_FOR_DAY # Prevent re-entry on same day

    # --- PRINT FINAL STATS ---
    print("\n" + "="*40)
    print("🏆 SPOT VALIDATION RESULTS 🏆")
    print("="*40)
    print(f"Total Trap Triggers: {total_trades}")
    if total_trades > 0:
        win_rate = (winning_trades / total_trades) * 100
        print(f"Win Rate: {win_rate:.1f}%")
        print(f"Net Spot Points Captured: {total_spot_points:.2f}")
        print(f"Average Points Per Trade: {(total_spot_points / total_trades):.2f}")
    print("="*40)

if __name__ == "__main__":
    # Ensure you have your CSV file ready!
    run_spot_backtest("nifty_5min.csv")