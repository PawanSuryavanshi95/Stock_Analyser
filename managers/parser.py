from datetime import datetime

from models.stock import Stock, Candle

class Parser:

    def __init__(self):
        pass

    def parse_alpha_vantage_response(self, res, name):
        time_series_data = None

        for key in list(res.keys()):
            if "Time Series" in key:
                time_series_data = res[key]

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

    def parse_twelve_data_response(self, res, name):

        candles = []
        for index, candle_data in enumerate(res['values']):

            open = float(candle_data["open"])
            high = float(candle_data["high"])
            low = float(candle_data["low"])
            close = float(candle_data["close"])
            label = datetime.strptime(candle_data["datetime"].split(" ")[0], "%Y-%m-%d").date()

            new_candle = Candle(open=open, high=high, low=low, close=close, label=label)

            candles.append(new_candle)
        
        return Stock(candles=candles, name=name)
