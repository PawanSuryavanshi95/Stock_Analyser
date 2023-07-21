from dotenv import load_dotenv
import os
import requests
import re
import datetime
import time

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

duration_month_mapping = {
    '1M': 1,
    '3M': 3,
    '6M': 6,
    '1Y': 12
}

def get_historical_data(candle_size, duration, stock):

    matches = re.match(pattern, candle_size)

    number = matches.group(1)
    characters = matches.group(2)

    if characters in period_function_mapping.keys():

        function_type = period_function_mapping[characters]
    else:
        function_type = "TIME_SERIES_DAILY"
    symbol = stock
    interval = candle_size
    url = URL.format(function_type, symbol, interval, ALPHA_VANTAGE_API_KEY)

    res = requests.get(url)

    res = res.json()

    if len(res.keys()) == 1:
        time.sleep(60)
        res = requests.get(url)
        res = res.json()

    data = res[list(res.keys())[1]]

    today_date = datetime.datetime.now().date()

    final_date = today_date.replace(month = today_date.month - duration_month_mapping[duration])


    labels = []
    closing = []

    m1 = float('inf')
    m2 = float('-inf')
    avg = 0

    i = 0
    for k in list(data.keys()):
        if i >= 10:
            i = 0
        kk = k.split(' ')[0]
        k_date = datetime.datetime.strptime(kk, "%Y-%m-%d").date()
        if final_date > k_date:
            print("yoo")
            break
        
        close = float(data[k]["4. close"])
        
        if i == 0:
            labels.append(kk)
        else:
            labels.append("")
        closing.append(close)
        m1 = min(m1, close)
        m2 = max(m2, close)
        avg += close

        i = i + 1
    
    avg = avg/len(labels)

    stock_data = {
        "labels": labels,
        "closing": closing,
        "min": m1,
        "max": m2,
        "average": avg
    }

    return stock_data
