from pydantic import BaseModel
from typing import List
from datetime import date, datetime, time

class Candle(BaseModel):

    open: float
    close: float
    high: float
    low: float
    label: date

class Stock(BaseModel):

    candles: List[Candle]
    name: str
    # last_refreshed: datetime

    @classmethod
    def create_instance_from_alpha_vantage(self, time_series_data, name):
        candles = []
        for index, k in enumerate(list(time_series_data.keys())):

            open = float(time_series_data[k]["1. open"])
            high = float(time_series_data[k]["2. high"])
            low = float(time_series_data[k]["3. low"])
            close = float(time_series_data[k]["4. close"])
            label = datetime.strptime(k.split(" ")[0], "%Y-%m-%d").date()

            new_candle = Candle(open=open, high=high, low=low, close=close, label=label)

            candles.append(new_candle)
        
        return Stock(candles=candles, name=name)
    
    @classmethod
    def create_instance_from_twelve_data(self, time_series_data, name):
        candles = []
        for index, candle_data in enumerate(time_series_data):

            open = float(candle_data["open"])
            high = float(candle_data["high"])
            low = float(candle_data["low"])
            close = float(candle_data["close"])
            label = datetime.strptime(candle_data["datetime"].split(" ")[0], "%Y-%m-%d").date()

            new_candle = Candle(open=open, high=high, low=low, close=close, label=label)

            candles.append(new_candle)
        
        return Stock(candles=candles, name=name)