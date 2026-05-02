import sys
import os
import pandas as pd

# This allows Python to find the indicators.py file located one folder up
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .indicators import add_adx_indicators
from .base_strategy import BaseStrategy

class L99Strategy(BaseStrategy):
    def __init__(self, instrument_token="DUMMY_TOKEN_FOR_BACKTEST"): 
        # Pass the token up to the BaseStrategy
        super().__init__(instrument_token) 
        self.name = "L99_ADX_Dynamic_Strategy"

    def generate_signals(self, market_data_df):
        """
        Analyzes the market data and generates buy/sell signals.
        Expects a dataframe with Date, Open, High, Low, Close.
        """
        if market_data_df.empty or len(market_data_df) < 15:
            return market_data_df # Not enough data to calculate ADX
            
        # 1. Calculate the ADX for the entire dataset in one extremely fast pass
        df = add_adx_indicators(market_data_df, length=14)
        
        # Create an empty column to store our trading decisions
        df['Signal'] = 'HOLD'
        df['Action'] = 'NONE'
        
        # 2. Iterate through the data to make day-by-day decisions
        for index in range(1, len(df)):
            # Look at YESTERDAY'S indicator values (T-1)
            yesterday_adx = df['ADX'].iloc[index - 1]
            yesterday_di_plus = df['DI+'].iloc[index - 1]
            yesterday_di_minus = df['DI-'].iloc[index - 1]
            
            # Look at TODAY'S price to decide entry
            today_close = df['Close'].iloc[index]
            
            # --- PROTECTIVE FILTERS (From your Forensic Analysis) ---
            
            # Filter 1: Total Failure Prevention (Strong Trend Against Us)
            if yesterday_adx > 25 and yesterday_di_minus > yesterday_di_plus:
                df.at[index, 'Signal'] = 'AVOID_LONG'
                df.at[index, 'Action'] = 'Market trending hard down. Skipping long trades.'
                continue # Skip the rest of the loop for this day
                
            # Filter 2: Whipsaw Prevention (Trend Exhaustion)
            elif yesterday_adx > 40:
                df.at[index, 'Signal'] = 'TRADE_WITH_TRAILING_STOP'
                df.at[index, 'Action'] = 'High volatility expected. Take quick profits.'
                
            # Filter 3: Late Bloomer Protocol (Trend Winding Up)
            elif yesterday_adx < 20:
                df.at[index, 'Signal'] = 'TRADE_WITH_EXTENDED_TIME_STOP'
                df.at[index, 'Action'] = 'Consolidation. Hold trade 45m longer.'
                
            # --- STANDARD L99 ENTRY LOGIC ---
            else:
                # Put your normal L99 buy/sell conditions here. 
                # For example:
                df.at[index, 'Signal'] = 'STANDARD_TRADE'
                df.at[index, 'Action'] = 'Normal conditions met.'

        return df

# For testing this specific file locally
if __name__ == "__main__":
    strategy = L99Strategy()
    print(f"Loaded {strategy.name}")