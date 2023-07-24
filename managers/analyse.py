from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
import datetime
import time
import os
import pandas as pd
from utils import *
from common import period_function_mapping, URL
load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY3')


async def calculate_rsi(prices, period=14):
    delta = prices.diff().dropna()
    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)
    avg_gains = gains.rolling(window=period).mean()
    avg_losses = losses.rolling(window=period).mean()
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))
    return rsi


async def get_historical_data_df(candle_size, duration, stock):
    num, chars = break_string(candle_size)

    function_type = period_function_mapping.get(chars, "TIME_SERIES_DAILY")

    symbol = stock
    interval = candle_size
    url = URL.format(function_type, symbol, interval, ALPHA_VANTAGE_API_KEY)
    print(url)
    try:
        res = await make_request(url)
    except Exception as e:
        return False, str(e)

    if len(res.keys()) == 1:
        message = res[list(res.keys())[0]]
        print(message)
        return False, message

    data = res[list(res.keys())[1]]
    data_df = pd.DataFrame(data).T

    today_date = datetime.datetime.now().date()
    num, chars = break_string(duration)
    if chars == 'Y':
        final_date = today_date + relativedelta(year=-1)
    else:
        final_date = today_date + relativedelta(months=-(int(num)))

    start_date = final_date.strftime('%Y-%m-%d')
    end_date = today_date.strftime('%Y-%m-%d')
    data_df['4. close'] = data_df['4. close'].astype(float)

    data_df = data_df[::-1]
    data_df['MA'] = data_df['4. close'].rolling(7).mean()
    data_df['RSI'] = await calculate_rsi(data_df['4. close'])
    data_df['RSI'] = data_df['RSI'].fillna(0)
    data_df['MA'] = data_df['MA'].fillna(0)
    data_df = data_df[::-1]

    data_df = data_df.loc[(data_df.index >= start_date) & (data_df.index <= end_date)]
    min_close = data_df['4. close'].min()
    max_close = data_df['4. close'].max()
    avg_close = data_df['4. close'].mean()

    stock_data = {
        "symbol": stock,
        "labels": data_df.index.tolist(),
        "closing": data_df['4. close'].tolist(),
        "min": float(min_close),
        "max": float(max_close),
        "average": float(avg_close),
        "ma": data_df['MA'].tolist(),
        "rsi": data_df['RSI'].tolist()
    }
    return True, stock_data


async def get_historical_data(candle_size, duration, stock):

    num, chars = break_string(candle_size)

    if chars in period_function_mapping.keys():
        function_type = period_function_mapping[chars]
    else:
        function_type = "TIME_SERIES_DAILY"
    symbol = stock
    interval = candle_size
    url = URL.format(function_type, symbol, interval, ALPHA_VANTAGE_API_KEY)

    try:
        res = await make_request(url)
    except Exception as e:
        return (False, str(e))

    if len(res.keys()) == 1:
        message = res[list(res.keys())[0]]
        print(message)
        return (False, message)

    data = res[list(res.keys())[1]]

    today_date = datetime.datetime.now().date()

    num, chars = break_string(duration)

    if chars == 'Y':
        final_date = today_date.replace(year = today_date.year - 1)
    else:
        final_date = today_date.replace(month = today_date.month - int(num))

    labels = []
    closing = []

    m1 = float('inf')
    m2 = float('-inf')
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
        if final_date > k_date:
            print("yoo")
            break
        
        close = float(data[k]["4. close"])

        sum += close
        ma_window.append(close)

        if len(ma_window) >= 7:
            ma.append(sum/7)
            sum -= ma_window[0]
            ma_window.pop(0)

        if index > 0:
            change = 100 * (close - prev)/prev
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
                rs = gain/loss
                rsi.append(100 * (1 - (1/(1 + rs))))
        prev = close
                
        
        if i == 0:
            labels.append(kk)
        else:
            labels.append("")
        closing.append(close)
        m1 = min(m1, close)
        m2 = max(m2, close)
        avg += close

        i = i + 1
    
    for i in rsi_window:
        rsi.append(0)
    
    j = len(ma_window)
    for i in ma_window:
        ma.append(sum/j)
        sum -= i
        j -= 1
    
    avg = avg/len(labels)

    stock_data = {
        "symbol": stock,
        "labels": list(reversed(labels)),
        "closing": list(reversed(closing)),
        "min": m1,
        "max": m2,
        "average": avg,
        "rsi": list(reversed(rsi)),
        "ma": list(reversed(ma))
    }

    return (True, stock_data)
