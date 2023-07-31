from utils import *
from managers.stocks import read_stock, add_stock, remove_stock, update_preferences, get_preferences
from handlers import Response
from managers.api import API

class Analysis:

    response = None
    api = None

    def __init__(self):
        self.response = Response()
        self.api = API()

    async def __analyse(self, stock_list, template, candle_size = None, duration = None):
        previous_stocks = await read_stock()

        if candle_size == None or duration == None:
            rows = await get_preferences()
            candle_size = rows[0]
            duration = rows[1]
        else:
            await update_preferences(candle_size, duration)

        stock_data = []

        for stock in stock_list:

            output = await self.__get_historical_data(candle_size, duration, stock)

            if not output['success']:
                msg = str(output['error'])
                return self.response.json_response(output, output['status'])

            await add_stock(stock)
            stock_data.append(output['historical_data'])

        context = {
            "stock_data": stock_data,
            "preferences": [candle_size, duration],
            "previous_stocks": previous_stocks
        }

        return await self.response.render_response(template, context)

    async def __get_historical_data(self, candle_size, duration, stock):
        
        res = await self.api.fetch_stock_data(candle_size, stock)

        if not res['success']:
            return res
        
        stock_instance = res['stock_instance']
        old_date = get_old_date(duration)

        historical_data = prepare_historical_data(stock=stock_instance, old_date=old_date)
        
        return {
            "success": True,
            "historical_data": historical_data,
        }

    async def historical_data(self, request, stock):

        candle_size = request.args.get('candle_size_dropdown')
        duration = request.args.get('duration_dropdown')

        working_services = request.app.ctx.working_services
        self.api.set_working_services(working_services)

        return await self.__analyse([stock], "historical_data.html", candle_size, duration)
    
    async def comparison(self, request, stocks):

        stock_list = stocks.split("&")
        if len(stock_list) != 2:
            return self.response.text_response("Invalid format of stocks passed. Please pass <stock_1>&<stock_2> after 'compare' route.")

        candle_size = request.args.get('candle_size_dropdown')
        duration = request.args.get('duration_dropdown')

        working_services = request.app.ctx.working_services
        self.api.set_working_services(working_services)

        return await self.__analyse(stock_list, "comparison.html", candle_size, duration)