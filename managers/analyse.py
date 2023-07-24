import datetime
import time
from dateutil.relativedelta import relativedelta
from sanic.response import text
from sanic_ext import render
import pandas as pd

from utils import *
from managers.stocks import read_stock, add_stock, remove_stock, update_preferences, get_preferences
from common import period_function_mapping, URL, ALPHA_VANTAGE_API_KEY

async def historical_analysis_manager(request, stock_list, template, post = True):
    
    previous_stocks = await read_stock()

    candle_size = None
    duration = None

    if post:
        candle_size = request.form.get('candle_size_dropdown')
        duration = request.form.get('duration_dropdown')
        await update_preferences(candle_size, duration)
    else:
        rows = await get_preferences()
        candle_size = rows[0]
        duration = rows[1]

    stock_data = []

    for stock in stock_list:

        success, historical_data = await get_historical_data(candle_size, duration, stock)

        if not success:
            return text("Something Went Wrong :( \nRefer to the below message\n" + str(stock_data))
        
        await add_stock(stock)

        stock_data.append(historical_data)

    return await render(
        template,
        context = {
            "stock_data": stock_data,
            "preferences":[ candle_size, duration],
            "previous_stocks": previous_stocks
        },
        status=200
    )

async def get_historical_data(candle_size, duration, stock):

    candle_size_prefix, candle_size_suffix = break_string(candle_size)

    function_type = period_function_mapping.get(candle_size_suffix, "TIME_SERIES_DAILY")
    symbol = stock
    interval = candle_size
    url = URL.format(function_type, symbol, interval, ALPHA_VANTAGE_API_KEY)

    try:
        res = await make_request(url)
    except Exception as e:
        return (False, str(e))
    
    time_series_data = None

    for key in list(res.keys()):
        if "Time Series" in key:
            time_series_data = res[key]

    if time_series_data == None:
        message = str(res)
        print(message)
        return (False, message)

    stock_data = parse_time_series(time_series_data, duration)
    stock_data['symbol'] = stock

    return (True, stock_data)

def parse_time_series(data, duration):
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
        minimum_stock_price = min(minimum_stock_price, close)
        maximum_stock_price = max(maximum_stock_price, close)
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
        "labels": list(reversed(labels)),
        "closing": list(reversed(closing)),
        "min": minimum_stock_price,
        "max": maximum_stock_price,
        "average": avg,
        "rsi": list(reversed(rsi)),
        "ma": list(reversed(ma))
    }

    return stock_data

async def get_historical_data_df(candle_size, duration, stock):

    candle_size_prefix, candle_size_suffix = break_string(candle_size)

    function_type = period_function_mapping.get(candle_size_suffix, "TIME_SERIES_DAILY")
    symbol = stock
    interval = candle_size
    url = URL.format(function_type, symbol, interval, ALPHA_VANTAGE_API_KEY)

    try:
        res = await make_request(url)
    except Exception as e:
        return (False, str(e))
    
    time_series_data = None

    for key in list(res.keys()):
        if "Time Series" in key:
            time_series_data = res[key]

    if time_series_data == None:
        message = str(res)
        print(message)
        return (False, message)

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

async def calculate_rsi(prices, period=14):
    delta = prices.diff().dropna()
    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)
    avg_gains = gains.rolling(window=period).mean()
    avg_losses = losses.rolling(window=period).mean()
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))
    return rsi