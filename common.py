import os
from dotenv import load_dotenv

load_dotenv()

aplha_vantage_function_map = {
    'min': "TIME_SERIES_INTRADAY",
    'D': "TIME_SERIES_DAILY",
    'M': "TIME_SERIES_MONTHLY"
}

twelve_data_interval_map = {
    'min': "min",
    'D': "day",
    'M': "month"
}

STOCK_FILE_PATH = "db/stocks.csv"
PREFERENCES_FILE_PATH = "db/preferences.csv"

URL = "https://www.alphavantage.co/query?function={}&symbol={}&interval={}&apikey={}"
ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"
TWELVE_DARA_URL = "https://twelve-data1.p.rapidapi.com/time_series"

X_RapidAPI_Key = "8df590c5ecmsh987bf572c322f98p12fb4bjsn5b4fc10f6825"
X_RapidAPI_Host = "twelve-data1.p.rapidapi.com"

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY4")