import requests
from datetime import datetime, timedelta
import pandas as pd
import random

class NightscoutAPI:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.dev_mode = base_url == "https://your-nightscout-url.herokuapp.com"

    def get_glucose_data(self, hours=24):
        """Fetch glucose data from Nightscout API"""
        if self.dev_mode:
            return self._generate_sample_data(hours)

        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(hours=hours)

            url = f"{self.base_url}/api/v1/entries/sgv"
            params = {
                'find[date][$gte]': int(start_date.timestamp() * 1000),
                'find[date][$lte]': int(end_date.timestamp() * 1000),
                'count': 1000
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            return pd.DataFrame(data)
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch data from Nightscout: {str(e)}")

    def get_current_glucose(self):
        """Fetch latest glucose reading"""
        if self.dev_mode:
            return self._generate_current_sample()

        try:
            url = f"{self.base_url}/api/v1/entries/sgv"
            params = {'count': 1}

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            return data[0] if data else None
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch current glucose: {str(e)}")

    def _generate_sample_data(self, hours):
        """Generate sample glucose data for development"""
        now = datetime.now()
        dates = [now - timedelta(minutes=5*i) for i in range(hours*12)]  # 5-minute intervals

        data = []
        base_glucose = 120

        for date in dates:
            # Generate realistic glucose variations
            glucose = base_glucose + random.randint(-20, 20)
            base_glucose = glucose  # Allow for trends

            # Keep within realistic ranges
            glucose = max(60, min(250, glucose))

            data.append({
                'sgv': glucose,
                'date': int(date.timestamp() * 1000),
                'direction': random.choice(['Flat', 'FortyFiveUp', 'FortyFiveDown'])
            })

        return pd.DataFrame(data)

    def _generate_current_sample(self):
        """Generate a sample current glucose reading"""
        return {
            'sgv': random.randint(80, 180),
            'date': int(datetime.now().timestamp() * 1000),
            'direction': random.choice(['Flat', 'FortyFiveUp', 'FortyFiveDown'])
        }