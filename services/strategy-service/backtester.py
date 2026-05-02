# algo-bot/services/strategy-service/backtester.py

import sys
import os
# Force Python to recognize the root directory for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import datetime
from strategies.l99_strategy import L99Strategy, L99State
from report_generator import generate_pdf_report

def run_spot_backtest(csv_path):
    print(f"📊 Loading historical data from {csv_path}...")
    df = pd.read_csv(csv_path)

    # Standardize column names to match what the script expects
    df.rename(columns={
        'Timestamp': 'date',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close'
    }, inplace=True)
    
    # Ensure date column is properly parsed AND strip the timezone tag
    df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)
    
    # Sort chronologically just in case
    df = df.sort_values('date').reset_index(drop=True)
    
    strategy = L99Strategy(instrument_token="NSE_INDEX|Nifty 50")
    
    total_trades = 0
    winning_trades = 0
    total_spot_points = 0.0
    
    entry_price = 0.0
    entry_time = None
    trade_log = []
    trade_setup = ""
    
    print("🚀 Starting Event-Driven Backtest Simulation...\n")

    current_date = None # Tracks the day to reset the State Machine

    for index, row in df.iterrows():
        base_time = row['date']
        
        # --- THE WAKE UP FIX ---
        # If it is a new day, reset the State Machine so it can trade again
        row_date = base_time.date()
        if current_date != row_date:
            current_date = row_date
            strategy.state = L99State.PRE_MARKET
            strategy.orb_high = float('-inf')
            strategy.orb_low = float('inf')
            strategy.trigger_direction = None
            strategy.fakeout_start_time = None
        # -----------------------

        # Microstructure Hack: Interpolate 4 ticks out of the 5-min candle
        # We assume the path is Open -> High -> Low -> Close.
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
            
            # 1. Detect an Entry
            if strategy.state == L99State.FIRED and entry_price == 0.0:
                entry_price = price
                entry_time = tick_time
                
                # Determine what kind of trade this is based on the elapsed time
                time_elapsed = (tick_time - strategy.fakeout_start_time).total_seconds() / 60.0
                trade_setup = "Trend Breakout" if time_elapsed >= 10.0 else "Gamma Trap"
                
                print(f"[{tick_time}] 🟢 ENTERED TRADE at {entry_price:.2f} ({trade_setup})")
                
            # 2. Detect an Exit (15-minute Time Stop)
            elif entry_price > 0.0 and (tick_time - entry_time).total_seconds() >= 900:
                exit_price = price
                
                # Calculate PnL
                if strategy.trigger_direction == 'UPSIDE':
                    points = exit_price - entry_price 
                else:
                    points = entry_price - exit_price 
                    
                total_spot_points += points
                total_trades += 1
                if points > 0: winning_trades += 1
                    
                print(f"[{tick_time}] 🔴 EXITED TRADE at {exit_price:.2f} | Points: {points:.2f}")
                
                # --- LOG FOR PDF ---
                trade_log.append({
                    'date': entry_time.strftime("%Y-%m-%d"),
                    'time': entry_time.strftime("%H:%M:%S"),
                    'setup': trade_setup,
                    'direction': strategy.trigger_direction,
                    'entry': entry_price,
                    'exit': exit_price,
                    'pnl': points
                })
                
                # Reset for next trade
                entry_price = 0.0
                strategy.state = L99State.DONE_FOR_DAY 

    # --- PRINT FINAL STATS ---
    print("\n" + "="*40)
    print("🏆 SPOT VALIDATION RESULTS 🏆")
    print("="*40)
    print(f"Total Triggers: {total_trades}")
    if total_trades > 0:
        win_rate = (winning_trades / total_trades) * 100
        print(f"Win Rate: {win_rate:.1f}%")
        print(f"Net Spot Points Captured: {total_spot_points:.2f}")
        print(f"Average Points Per Trade: {(total_spot_points / total_trades):.2f}")
    print("="*40)

    # Generate the PDF if trades were taken
    if trade_log:
        generate_pdf_report(trade_log)

if __name__ == "__main__":
    # Ensure you have your CSV file ready!
    run_spot_backtest("nifty_5min.csv")