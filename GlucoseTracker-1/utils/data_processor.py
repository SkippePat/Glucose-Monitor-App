import pandas as pd
import numpy as np
from datetime import datetime

class DataProcessor:
    @staticmethod
    def process_glucose_data(df):
        """Process raw glucose data"""
        if df.empty:
            return df
        
        # Convert timestamp to datetime
        df['datetime'] = pd.to_datetime(df['date'], unit='ms')
        
        # Calculate basic statistics
        df['rolling_avg'] = df['sgv'].rolling(window=12).mean()
        df['rolling_std'] = df['sgv'].rolling(window=12).std()
        
        return df

    @staticmethod
    def calculate_statistics(df):
        """Calculate glucose statistics"""
        if df.empty:
            return {}
        
        stats = {
            'current': df['sgv'].iloc[0],
            'average': df['sgv'].mean(),
            'std': df['sgv'].std(),
            'max': df['sgv'].max(),
            'min': df['sgv'].min(),
            'in_range': ((df['sgv'] >= 70) & (df['sgv'] <= 180)).mean() * 100
        }
        return stats

    @staticmethod
    def get_trend_arrow(direction):
        """Convert Nightscout direction to arrow symbol"""
        arrows = {
            'DoubleUp': '↑↑',
            'SingleUp': '↑',
            'FortyFiveUp': '↗',
            'Flat': '→',
            'FortyFiveDown': '↘',
            'SingleDown': '↓',
            'DoubleDown': '↓↓',
            'NONE': '-'
        }
        return arrows.get(direction, '-')
