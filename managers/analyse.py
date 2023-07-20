from dotenv import load_dotenv
import os
import requests
import re

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

URL = "https://www.alphavantage.co/query?function={}&symbol={}&interval={}&apikey={}"

pattern = r'(\d+)(\D+)'

period_function_mapping = {
    'min': "TIME_SERIES_INTRADAY",
    'D': "TIME_SERIES_DAILY",
    'W': "TIME_SERIES_WEEKLY",
    'M': "TIME_SERIES_MONTHLY"
}

def get_historical_data(period, stock):

    matches = re.match(pattern, period)

    number = matches.group(1)
    characters = matches.group(2)

    print(characters)

    if characters in period_function_mapping.keys():

        function_type = period_function_mapping[characters]
    else:
        function_type = "TIME_SERIES_DAILY"
    symbol = stock
    interval = period
    url = URL.format(function_type, symbol, interval, ALPHA_VANTAGE_API_KEY)


    print(url)

    res = requests.get(url)

    res = res.json()

    data = res[list(res.keys())[1]]

    labels = []
    closing = []

    m1 = float('inf')
    m2 = float('-inf')
    avg = 0


    for k in list(data.keys())[:100]:
        
        close = float(data[k]["4. close"])
        
        labels.append(k)
        closing.append(close)
        m1 = min(m1, close)
        m2 = max(m2, close)
        avg += close
    
    avg = avg/len(labels)

    stock_data = {
        "labels": labels,
        "closing": closing,
        "min": m1,
        "max": m2,
        "average": avg
    }

    return stock_data



get_historical_data("1m", "AAPL")
