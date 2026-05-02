import numpy as np
import pandas as pd

def add_adx_indicators(df, length=14):
    """
    Calculates Wilder's ADX, DI+, and DI- and adds them as columns to the dataframe.
    Expects a Pandas DataFrame with 'High', 'Low', and 'Close' columns.
    """
    df = df.copy()
    
    # 1. Calculate True Range (TR)
    df['tr1'] = df['High'] - df['Low']
    df['tr2'] = (df['High'] - df['Close'].shift(1)).abs()
    df['tr3'] = (df['Low'] - df['Close'].shift(1)).abs()
    df['TR'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)

    # 2. Calculate Directional Movement (+DM and -DM)
    up_move = df['High'] - df['High'].shift(1)
    down_move = df['Low'].shift(1) - df['Low']
    df['+DM'] = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    df['-DM'] = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

    # 3. Wilder's Smoothing Function
    def smooth(series, length):
        smoothed = np.zeros(len(series))
        vals = series.fillna(0).values
        smoothed[0] = vals[0]
        for i in range(1, len(series)):
            smoothed[i] = smoothed[i-1] - (smoothed[i-1] / length) + vals[i]
        return smoothed

    df['smooth_TR'] = smooth(df['TR'], length)
    df['smooth_+DM'] = smooth(df['+DM'], length)
    df['smooth_-DM'] = smooth(df['-DM'], length)

    # 4. Calculate DI+, DI-, DX, and ADX
    # Adding a small epsilon (1e-10) to prevent division by zero errors
    df['DI+'] = (df['smooth_+DM'] / (df['smooth_TR'] + 1e-10)) * 100
    df['DI-'] = (df['smooth_-DM'] / (df['smooth_TR'] + 1e-10)) * 100
    df['DX'] = (df['DI+'] - df['DI-']).abs() / (df['DI+'] + df['DI-'] + 1e-10) * 100
    
    # ADX is the Simple Moving Average of DX
    df['ADX'] = df['DX'].rolling(window=length).mean()
    
    # Clean up intermediate calculation columns to keep the dataframe lightweight
    cols_to_drop = ['tr1', 'tr2', 'tr3', 'TR', '+DM', '-DM', 'smooth_TR', 'smooth_+DM', 'smooth_-DM', 'DX']
    return df.drop(columns=cols_to_drop)