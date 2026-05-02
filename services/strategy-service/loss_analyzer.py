import pandas as pd
import numpy as np
from indicators import add_adx_indicators

def analyze_losing_trades(price_df, trades_df):
    """
    Merges historical price data with the trade log to analyze T-1 conditions.
    """
    print("Calculating ADX indicators for historical data...")
    # 1. Calculate indicators for the whole dataset using our math file
    data = add_adx_indicators(price_df)
    
    # 2. Shift indicators by 1 to get "Day Before" (T-1) metrics aligned with today
    data['T-1_ADX'] = data['ADX'].shift(1)
    data['T-2_ADX'] = data['ADX'].shift(2)
    data['T-1_DI+'] = data['DI+'].shift(1)
    data['T-1_DI-'] = data['DI-'].shift(1)
    
    # Determine if ADX was rising into the trade
    data['ADX_Rising'] = data['T-1_ADX'] > data['T-2_ADX']
    
    # 3. Merge the T-1 data with your trade log based on the Date
    analysis = pd.merge(trades_df, data, on='Date', how='inner')
    
    print("\n" + "="*50)
    print(" FORENSIC TRADE REPORT")
    print("="*50)
    
    # 4. Print the forensic report
    for index, trade in analysis.iterrows():
        print(f"Trade Date:  {trade['Date'].strftime('%Y-%m-%d')}")
        print(f"Failure:     {trade['Failure_Type']}")
        print(f"T-1 ADX:     {trade['T-1_ADX']:.2f} ({'Rising' if trade['ADX_Rising'] else 'Falling'})")
        print(f"T-1 DI+:     {trade['T-1_DI+']:.2f} | T-1 DI-: {trade['T-1_DI-']:.2f}")
        
        # Strategy Adjustments based on symptoms
        if trade['T-1_ADX'] > 25 and max(trade['T-1_DI+'], trade['T-1_DI-']) > 30:
            print(">> [SYSTEM FLAG]: High Trend. Avoid counter-trend entries today.")
        elif trade['T-1_ADX'] < 20 and trade['ADX_Rising']:
            print(">> [SYSTEM FLAG]: ADX Winding Up. Extend time-stop; breakout may be delayed.")
        elif trade['T-1_ADX'] > 40 and not trade['ADX_Rising']:
            print(">> [SYSTEM FLAG]: Trend Exhaustion. Implement tight trailing stop to prevent whipsaw.")
            
        print("-" * 50)

if __name__ == "__main__":
    # ---------------------------------------------------------
    # SETUP FOR TESTING
    # ---------------------------------------------------------
    # If you have converted your nifty_5min.csv to daily OHLC data, load it here.
    # For now, this generates mock data so the script runs perfectly out of the box.
    dates = pd.date_range(start='2022-01-01', periods=100, freq='B')
    price_mock = pd.DataFrame({
        'Date': dates,
        'High': np.random.uniform(34000, 34500, size=100) + np.arange(100)*10,
        'Low': np.random.uniform(33500, 34000, size=100) + np.arange(100)*10,
        'Close': np.random.uniform(33800, 34200, size=100) + np.arange(100)*10,
    })
    
    # Mock Trade Log based on a few entries from your PDF
    trades_mock = pd.DataFrame({
        'Date': pd.to_datetime(['2022-02-11', '2022-06-17', '2022-01-25']),
        'Asset': ['DOW', 'UPS', 'DOW'],
        'Failure_Type': ['LATE BLOOMER', 'WHIPSAW', 'TOTAL FAILURE']
    })
    
    # Run the analysis
    analyze_losing_trades(price_mock, trades_mock)