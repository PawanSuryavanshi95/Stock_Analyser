from utils import *
from managers.stocks import read_stock, add_stock, remove_stock, update_preferences, get_preferences
from models.response import Response
from models.request import Request

response = Response()
request = Request()

async def analysis_manager(stock_list, template, candle_size = None, duration = None):
    previous_stocks = await read_stock()

    if candle_size == None or duration == None:
        rows = await get_preferences()
        candle_size = rows[0]
        duration = rows[1]
    else:
        await update_preferences(candle_size, duration)

    stock_data = []

    for stock in stock_list:

        output = await get_historical_data(candle_size, duration, stock)

        if not output['success']:
            msg = str(output['error'])
            return response.text_response(msg)

        await add_stock(stock)
        stock_data.append(output['historical_data'])

    context = {
        "stock_data": stock_data,
        "preferences": [candle_size, duration],
        "previous_stocks": previous_stocks
    }

    return await response.render_response(template, context)

async def get_historical_data(candle_size, duration, stock):
    
    res = await request.make_get_request(candle_size, stock)

    if not res['success']:
        return response.text_response(res['error'])
    
    time_series_data = None

    for key in list(res['data'].keys()):
        if "Time Series" in key:
            time_series_data = res['data'][key]

    if time_series_data is None:
        message = str(res['data'])
        print(message)
        return {
            'success': False,
            'error': message
        }
    
    historical_data = parse_time_series(time_series_data, duration, stock)
    
    return {
        "success": True,
        "historical_data": historical_data,
    }