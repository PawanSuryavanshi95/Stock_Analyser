from enum import Enum

from aiohttp_client_cache import CachedSession, SQLiteBackend
import asyncio
import aiohttp

from managers.parser import Parser
from managers.validator import Validator
from utils import break_string, make_request
from common import *
from models.stock import Stock

class Services(Enum):
    ALPHA_VANTAGE = 1
    TWELVE_DATA = 2

class API:

    alpha_vantage_url = None
    alpha_vantage_headers = {}

    twelve_data_url = None
    twelve_data_headers = {}

    parser = None
    validator = None

    def __init__(self):
        self.alpha_vantage_url = ALPHA_VANTAGE_URL
        self.twelve_data_url = TWELVE_DARA_URL

        self.twelve_data_headers  = {
            "X-RapidAPI-Key": X_RapidAPI_Key,
            "X-RapidAPI-Host": X_RapidAPI_Host
        }

        self.parser = Parser()
        self.validator = Validator()
    
    def __select_api(self):
        # Check performance then send service to be used
        return Services.TWELVE_DATA
    
    def __create_params_alpha_vantage(self, candle_size, stock):
        candle_size_prefix, candle_size_suffix = break_string(candle_size)
        function_type = aplha_vantage_function_map.get(candle_size_suffix, "TIME_SERIES_DAILY")

        return {
            "function": function_type,
            "symbol": stock,
            "interval": candle_size,
            "apikey": ALPHA_VANTAGE_API_KEY
        }
    
    def __create_params_twelve_data(self, candle_size, stock):
        candle_size_prefix, candle_size_suffix = break_string(candle_size)
        interval_suffix = twelve_data_interval_map.get(candle_size_suffix, None)

        interval = "1day"

        if interval_suffix is not None:
            interval = candle_size_prefix + interval_suffix
    
        return {
            "symbol": stock,
            "interval": interval,
            "outputsize": "5000",
            "format": "json"
        }

    async def fetch_stock_data(self, candle_size, stock):

        url = None
        headers = {}
        query_params = {}

        service = self.__select_api()

        match service:

            case Services.ALPHA_VANTAGE:
                query_params = self.__create_params_alpha_vantage(candle_size, stock)
                url = self.alpha_vantage_url

            case Services.TWELVE_DATA:
                headers = self.twelve_data_headers
                query_params = self.__create_params_twelve_data(candle_size, stock)
                url = self.twelve_data_url
            
            case None:
                return {
                    'success': False,
                    'error': "Error message TBD"
                }

        try:
            async with CachedSession(cache=SQLiteBackend()) as session:
                async with session.get(url, headers = headers, params = query_params) as resp:
                    res = await resp.json()

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        
        match service:

            case Services.ALPHA_VANTAGE:
                val_res = self.validator.validate_alpha_vantage_response(res)
                if not val_res['success']:
                    return val_res
                data = self.parser.parse_alpha_vantage_response(res)
                stock_instance = Stock.create_instance_from_alpha_vantage(data, stock)

            case Services.TWELVE_DATA:
                val_res = self.validator.validate_twelve_data_response(res)
                if not val_res['success']:
                    return val_res
                data = self.parser.parse_twelve_data_response(res)
                stock_instance = Stock.create_instance_from_twelve_data(data, stock)
            
            case None:
                return {
                    'success': False,
                    'error': "Error message TBD"
                }
        
        return {
            "success": True,
            "stock_instance": stock_instance
        }
