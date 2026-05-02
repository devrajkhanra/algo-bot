import pandas as pd
import numpy as np
from datetime import timedelta
from strategies.l99_strategy import L99Strategy

class Backtester:
    def __init__(self, initial_capital=100000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = 0
        self.trade_log = []
        
    def run_backtest(self, historical_data, strategy):
        """
        Runs the provided strategy over the historical data.
        """
        print(f"Starting backtest for {strategy.name}...")
        
        # 1. Get the signals from the strategy (This calculates ADX and applies filters)
        df_with_signals = strategy.generate_signals(historical_data)
        
        if df_with_signals.empty:
            print("Error: No data to backtest.")
            return

        # 2. Step through time and simulate trading
        for index, row in df_with_signals.iterrows():
            date = row['Date']
            price = row['Close']
            signal = row['Signal']
            action_reason = row['Action']
            
            # --- SIMULATE TRADING LOGIC ---
            
            # If we get a "STANDARD_TRADE", we buy.
            if signal == 'STANDARD_TRADE' and self.positions == 0:
                self._enter_trade(date, price, action_reason, "Standard L99 Entry")
                
            # If we get a "TRADE_WITH_EXTENDED_TIME_STOP" (Late Bloomer condition)
            elif signal == 'TRADE_WITH_EXTENDED_TIME_STOP' and self.positions == 0:
                self._enter_trade(date, price, action_reason, "Late Bloomer Entry (Hold Longer)")
                
            # If we get "TRADE_WITH_TRAILING_STOP" (Whipsaw condition)
            elif signal == 'TRADE_WITH_TRAILING_STOP' and self.positions == 0:
               self._enter_trade(date, price, action_reason, "Whipsaw Entry (Tight Trailing Stop)")
               
            # Example Exit Logic (You would replace this with your actual L99 exit rules)
            elif self.positions > 0:
                # Dummy exit condition: exit after 3 days
                entry_date = self.trade_log[-1]['Entry Date']
                if date >= entry_date + timedelta(days=3):
                    self._exit_trade(date, price, "Time Stop Reached")

        self._print_results()
        
    def _enter_trade(self, date, price, signal_reason, strategy_type):
        """Helper to record trade entries."""
        # Calculate how many shares/contracts we can buy
        shares = int(self.capital / price)
        cost = shares * price
        
        if shares > 0:
            self.positions = shares
            self.capital -= cost
            self.trade_log.append({
                'Entry Date': date,
                'Entry Price': price,
                'Shares': shares,
                'Reason': signal_reason,
                'Type': strategy_type,
                'Exit Date': None,
                'Exit Price': None,
                'Profit/Loss': None
            })
            print(f"[BUY]  {date.strftime('%Y-%m-%d')} | Price: {price:.2f} | Type: {strategy_type}")

    def _exit_trade(self, date, price, reason):
        """Helper to record trade exits."""
        if self.positions > 0:
            revenue = self.positions * price
            self.capital += revenue
            
            # Update the last trade in the log
            last_trade = self.trade_log[-1]
            last_trade['Exit Date'] = date
            last_trade['Exit Price'] = price
            
            pnl = revenue - (last_trade['Shares'] * last_trade['Entry Price'])
            last_trade['Profit/Loss'] = pnl
            
            print(f"[SELL] {date.strftime('%Y-%m-%d')} | Price: {price:.2f} | PnL: {pnl:.2f} | {reason}")
            self.positions = 0

    def _print_results(self):
        """Prints a summary of the backtest."""
        print("\n" + "="*40)
        print(" BACKTEST RESULTS")
        print("="*40)
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        
        # Calculate final portfolio value
        final_value = self.capital
        if self.positions > 0 and len(self.trade_log) > 0:
            # Value remaining open positions at the last known entry price just for estimation
            final_value += (self.positions * self.trade_log[-1]['Entry Price'])
            
        print(f"Final Capital:   ${final_value:,.2f}")
        print(f"Total Return:    {((final_value - self.initial_capital) / self.initial_capital) * 100:.2f}%")
        
        completed_trades = [t for t in self.trade_log if t['Exit Date'] is not None]
        print(f"Total Trades:    {len(completed_trades)}")
        
        if completed_trades:
            winners = len([t for t in completed_trades if t['Profit/Loss'] > 0])
            print(f"Win Rate:        {(winners / len(completed_trades)) * 100:.2f}%")
        print("="*40 + "\n")

# ---------------------------------------------------------
# RUN THE SIMULATION
# ---------------------------------------------------------
if __name__ == "__main__":
    # 1. Generate some mock data (Replace this with pd.read_csv('nifty_5min.csv') later)
    # Note: If using nifty_5min.csv, ensure it is resampled to Daily OHLC before passing to the ADX calculator.
    dates = pd.date_range(start='2022-01-01', periods=250, freq='B')
    price_mock = pd.DataFrame({
        'Date': dates,
        'Open': np.random.uniform(33800, 34200, size=250),
        'High': np.random.uniform(34000, 34500, size=250),
        'Low': np.random.uniform(33500, 34000, size=250),
        'Close': np.random.uniform(33800, 34200, size=250),
        'Volume': np.random.uniform(10000, 50000, size=250)
    })
    
    # 2. Instantiate the strategy and the backtester
    my_strategy = L99Strategy()
    tester = Backtester(initial_capital=100000)
    
    # 3. Run it
    tester.run_backtest(price_mock, my_strategy)# ---------------------------------------------------------


# ---------------------------------------------------------
# RUN THE SIMULATION
# ---------------------------------------------------------
if __name__ == "__main__":
    import os
    
    # 1. Load your actual Nifty 5-minute data
    csv_path = "nifty_5min.csv"
    
    if not os.path.exists(csv_path):
        print(f"Error: Could not find {csv_path}. Make sure it is in the strategy-service folder.")
    else:
        print(f"Loading real market data from {csv_path}...")
        df_5min = pd.read_csv(csv_path)
        
        # 2. Standardize column names (make them lowercase temporarily to easily find them)
        df_5min.columns = [c.lower() for c in df_5min.columns]
        
        # Assume the date column is named 'date', 'datetime', or 'time'
        date_col = next((col for col in df_5min.columns if 'date' in col or 'time' in col), None)
        
        if date_col:
            # Convert to Pandas datetime and set as index for resampling
            df_5min[date_col] = pd.to_datetime(df_5min[date_col])
            df_5min.set_index(date_col, inplace=True)
            
            # 3. THE MAGIC: Resample 5-minute data into Daily OHLCV data
            print("Resampling 5-minute data to Daily candles for accurate ADX calculation...")
            daily_data = df_5min.resample('D').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).dropna() # Drop empty days (weekends/holidays)
            
            # Reset index and strictly rename columns so indicators.py can read them
            daily_data = daily_data.reset_index()
            daily_data.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            
            # 4. Instantiate the strategy and the backtester
            my_strategy = L99Strategy(instrument_token="NSE_INDEX|Nifty 50")
            tester = Backtester(initial_capital=100000)
            
            # 5. Run the simulation on your Daily data!
            tester.run_backtest(daily_data, my_strategy)
            
        else:
            print("Error: Could not find a date/time column in your CSV. Please check your CSV headers.")