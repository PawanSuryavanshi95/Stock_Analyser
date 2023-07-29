from aiohttp_client_cache import CachedSession, SQLiteBackend
import asyncio
import aiohttp
import re
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta

from models.stock import Stock, Candle

def break_string(x):
    pattern = r'(\d+)(\D+)'
    matches = re.match(pattern, x)
    number = matches.group(1)
    characters = matches.group(2)

    return number, characters

async def make_request(url):
    async with CachedSession(cache=SQLiteBackend()) as session:
        async with session.get(url) as resp:
            return await resp.json()
        
def parse_time_series(data, duration, stock):
    today_date = datetime.datetime.now().date()

    duration_prefix, duration_suffix = break_string(duration)

    old_date = today_date
    if duration_suffix == 'Y':
        old_date -= relativedelta(years=1)
    else:
        old_date -= relativedelta(months=int(duration_prefix))

    labels = []
    closing = []

    minimum_stock_price = float('inf')
    maximum_stock_price = float('-inf')
    avg = 0

    i = 0

    gain = 0
    loss = 0
    rsi_window = []
    rsi = []
    prev = 0

    ma = []
    ma_window = []
    sum = 0

    for index, k in enumerate(list(data.keys())):

        if i >= 10:
            i = 0
        kk = k.split(' ')[0]
        k_date = datetime.datetime.strptime(kk, "%Y-%m-%d").date()
        if old_date > k_date:
            break

        close = float(data[k]["4. close"])

        sum += close
        ma_window.append(close)

        if len(ma_window) >= 7:
            ma.append(sum / 7)
            sum -= ma_window[0]
            ma_window.pop(0)

        if index > 0:
            change = 100 * (close - prev) / prev
            rsi_window.append(change)
            if change >= 0:
                gain += change
            else:
                loss -= change
            if len(rsi_window) >= 14:
                if rsi_window[0] >= 0:
                    gain -= rsi_window[0]
                else:
                    loss += rsi_window[0]

                rsi_window.pop(0)
                rs = gain / loss
                rsi.append(100 * (1 - (1 / (1 + rs))))
        prev = close

        if i == 0:
            labels.append(kk)
        else:
            labels.append("")
        closing.append(close)
        minimum_stock_price = min(minimum_stock_price, close)
        maximum_stock_price = max(maximum_stock_price, close)
        avg += close

        i = i + 1

    for i in rsi_window:
        rsi.append(0)

    j = len(ma_window)
    for i in ma_window:
        ma.append(sum / j)
        sum -= i
        j -= 1

    avg = avg / len(labels)

    return {
        "symbol": stock,
        "labels": list(reversed(labels)),
        "closing": list(reversed(closing)),
        "min": minimum_stock_price,
        "max": maximum_stock_price,
        "average": avg,
        "rsi": list(reversed(rsi)),
        "ma": list(reversed(ma))
    }

def parse_time_series_df(data, duration, stock):
    data_df = pd.DataFrame(data).T

    today_date = datetime.datetime.now().date()
    duration_prefix, duration_suffix = break_string(duration)
    final_date = today_date
    if duration_suffix == 'Y': # upper
        final_date -= relativedelta(years=1)
    else:
        final_date -= relativedelta(months=int(duration_prefix))

    start_date = final_date.strftime('%Y-%m-%d')
    end_date = today_date.strftime('%Y-%m-%d')
    data_df['4. close'] = data_df['4. close'].astype(float)

    data_df = data_df[::-1]
    data_df['MA'] = data_df['4. close'].rolling(window=7, min_periods=1).mean()
    data_df['RSI'] = calculate_rsi(data_df['4. close'])
    data_df['RSI'] = data_df['RSI'].fillna(0)
    data_df['MA'] = data_df['MA'].fillna(0)

    data_df = data_df.loc[(data_df.index >= start_date) & (data_df.index <= end_date)]
    min_close = data_df['4. close'].min()
    max_close = data_df['4. close'].max()
    avg_close = data_df['4. close'].mean()

    return {
        "symbol": stock,
        "labels": data_df.index.tolist(),
        "closing": data_df['4. close'].tolist(),
        "min": float(min_close),
        "max": float(max_close),
        "average": float(avg_close),
        "ma": data_df['MA'].tolist(),
        "rsi": data_df['RSI'].tolist()
    }

def calculate_rsi(prices, period=14):
    delta = prices.diff().dropna()
    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)
    avg_gains = gains.rolling(window=period, min_periods=1).mean()
    avg_losses = losses.rolling(window=period, min_periods=1).mean()
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))
    return rsi

def check_date(candle: Candle, old_date):
    return candle.label > old_date

def get_old_date(duration: str):
    today_date = datetime.datetime.now().date()

    duration_prefix, duration_suffix = break_string(duration)

    old_date = today_date
    if duration_suffix == 'Y':
        old_date -= relativedelta(years=1)
    else:
        old_date -= relativedelta(months=int(duration_prefix))

    return old_date

def prepare_historical_data(stock: Stock, old_date: datetime.date):

    filtered_candles = list(filter(lambda candle: check_date(candle, old_date), stock.candles))

    gain = 0
    loss = 0
    rsi_window = []
    rsi = []
    prev = 0

    ma = []
    ma_window = []
    sum = 0
    
    labels = []
    closing = []

    for index, candle in enumerate(filtered_candles):

        close = candle.close

        sum += close
        ma_window.append(close)

        if len(ma_window) >= 7:
            ma.append(sum / 7)
            sum -= ma_window[0]
            ma_window.pop(0)

        if index > 0:
            change = 100 * (close - prev) / prev
            rsi_window.append(change)
            if change >= 0:
                gain += change
            else:
                loss -= change
            if len(rsi_window) >= 14:
                if rsi_window[0] >= 0:
                    gain -= rsi_window[0]
                else:
                    loss += rsi_window[0]

                rsi_window.pop(0)
                rs = gain / loss
                rsi.append(100 * (1 - (1 / (1 + rs))))
        prev = close

        labels.append(candle.label.strftime("%Y-%m-%d"))
        closing.append(close)

    for i in rsi_window:
        rsi.append(0)

    j = len(ma_window)
    for i in ma_window:
        ma.append(sum / j)
        sum -= i
        j -= 1

    return {
        "symbol": stock.name,
        "labels": list(reversed(labels)),
        "closing": list(reversed(closing)),
        "min": 0,
        "max": 0,
        "average": 0,
        "rsi": list(reversed(rsi)),
        "ma": list(reversed(ma))
    }