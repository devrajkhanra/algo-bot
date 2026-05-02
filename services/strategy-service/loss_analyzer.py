# algo-bot/services/strategy-service/loss_analyzer.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import datetime
from fpdf import FPDF
from strategies.l99_strategy import L99Strategy, L99State

class ForensicsPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Quantitative Forensics: Losing Trade Postcondition Analysis', ln=1, align='C')
        self.ln(5)

def run_forensics(csv_path):
    print("🕵️‍♂️ Initializing Trade Forensics Engine...")
    df = pd.read_csv(csv_path)
    df.rename(columns={'Timestamp': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close'}, inplace=True)
    df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)
    df = df.sort_values('date').reset_index(drop=True)
    
    strategy = L99Strategy(instrument_token="NSE_INDEX|Nifty 50")
    
    entry_price = 0.0
    entry_time = None
    losing_trades = []
    
    current_date = None

    print("🔄 Simulating engine to isolate losses...")
    for index, row in df.iterrows():
        base_time = row['date']
        
        if current_date != base_time.date():
            current_date = base_time.date()
            strategy.state = L99State.PRE_MARKET
            strategy.orb_high = float('-inf')
            strategy.orb_low = float('inf')
            strategy.trigger_direction = None
            strategy.fakeout_start_time = None

        ticks = [
            (row['open'], base_time + datetime.timedelta(seconds=0)),
            (row['high'], base_time + datetime.timedelta(seconds=10)),
            (row['low'],  base_time + datetime.timedelta(seconds=20)),
            (row['close'], base_time + datetime.timedelta(seconds=30))
        ]

        for price, tick_time in ticks:
            strategy.on_tick({'lastTradedPrice': price, 'timestamp': int(tick_time.timestamp() * 1000)})
            
            if strategy.state == L99State.FIRED and entry_price == 0.0:
                entry_price = price
                entry_time = tick_time
                
            elif entry_price > 0.0 and (tick_time - entry_time).total_seconds() >= 900:
                points = (price - entry_price) if strategy.trigger_direction == 'UPSIDE' else (entry_price - price)
                
                # WE ONLY CARE ABOUT LOSSES
                if points < 0:
                    losing_trades.append({
                        'time': entry_time,
                        'dir': strategy.trigger_direction,
                        'entry': entry_price,
                        'loss': points,
                        'exit_time': tick_time
                    })
                
                entry_price = 0.0
                strategy.state = L99State.DONE_FOR_DAY 

    print(f"🔍 Found {len(losing_trades)} losing trades. Calculating Postconditions...")
    
    # --- DEEP FORENSICS ANALYSIS ---
    pdf = ForensicsPDF(orientation='L') # Landscape for wide tables
    pdf.add_page()
    pdf.set_font("Arial", 'B', 8)
    
    cols = ['Date/Time', 'Dir', 'Loss', 'Max Profit (During)', 'Post-Exit Profit', 'Forensic Conclusion']
    widths = [30, 15, 20, 30, 30, 140]
    for i, col in enumerate(cols): pdf.cell(widths[i], 10, col, border=1, align='C')
    pdf.ln()
    
    pdf.set_font("Arial", size=8)
    
    for trade in losing_trades:
        # Find the window DURING the trade (15 mins)
        during_mask = (df['date'] >= trade['time']) & (df['date'] <= trade['exit_time'])
        during_df = df.loc[during_mask]
        
        # Find the window AFTER the trade (next 45 mins)
        post_time_limit = trade['exit_time'] + datetime.timedelta(minutes=45)
        post_mask = (df['date'] > trade['exit_time']) & (df['date'] <= post_time_limit)
        post_df = df.loc[post_mask]
        
        # Calculate Max Favorable Excursion (MFE) During Trade
        max_profit_during = 0
        if not during_df.empty:
            if trade['dir'] == 'UPSIDE':
                max_profit_during = during_df['high'].max() - trade['entry']
            else:
                max_profit_during = trade['entry'] - during_df['low'].min()
                
        # Calculate Post-Condition (Did it win if held longer?)
        max_profit_after = 0
        if not post_df.empty:
            if trade['dir'] == 'UPSIDE':
                max_profit_after = post_df['high'].max() - trade['entry']
            else:
                max_profit_after = trade['entry'] - post_df['low'].min()

        # Generate Contextual Recommendation
        if max_profit_during > 30:
            conclusion = "WHIPSAW: Trade was up +30 pts but reversed. Fix: Implement Trailing Stop."
        elif max_profit_after > 50:
            conclusion = f"LATE BLOOMER: Blast occurred late. Holding 45m longer would yield +{max_profit_after:.1f} pts."
        else:
            conclusion = "TOTAL FAILURE: Market trended hard against us. Time-stop successfully saved capital."

        # Write to PDF
        pdf.cell(widths[0], 10, trade['time'].strftime("%Y-%m-%d %H:%M"), border=1)
        pdf.cell(widths[1], 10, trade['dir'][:3], border=1, align='C')
        pdf.set_text_color(220, 0, 0)
        pdf.cell(widths[2], 10, f"{trade['loss']:.1f}", border=1, align='C')
        pdf.set_text_color(0, 0, 0)
        pdf.cell(widths[3], 10, f"{max_profit_during:.1f}", border=1, align='C')
        pdf.cell(widths[4], 10, f"{max_profit_after:.1f}", border=1, align='C')
        pdf.cell(widths[5], 10, conclusion, border=1)
        pdf.ln()

    filename = "Loss_Anatomy_Report.pdf"
    pdf.output(filename)
    print(f"✅ Forensics complete. Generated '{filename}'.")

if __name__ == "__main__":
    run_forensics("nifty_5min.csv")