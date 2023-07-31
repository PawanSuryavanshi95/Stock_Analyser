from aiohttp_client_cache import CachedSession, SQLiteBackend
import asyncio
import aiohttp

from models import Services
from managers.parser import Parser
from managers.validator import Validator
from utils import break_string
from common import *
from models.stock import Stock
from datetime import datetime, timedelta
import csv

class API:

    alpha_vantage_url = None
    alpha_vantage_headers = {}

    twelve_data_url = None
    twelve_data_headers = {}

    parser = None
    validator = None

    working_services = []

    def __init__(self):
        self.alpha_vantage_url = ALPHA_VANTAGE_URL
        self.twelve_data_url = TWELVE_DARA_URL

        self.twelve_data_headers  = {
            "X-RapidAPI-Key": X_RapidAPI_Key,
            "X-RapidAPI-Host": X_RapidAPI_Host
        }

        self.parser = Parser()
        self.validator = Validator()

        for service in Services:
            self.working_services.append(service)
    
    def set_working_services(self, working_services):
        self.working_services = working_services

    def __select_api(self):

        with open(SERVICE_LOG_FILE_PATH, 'r') as f:
            logs = f.readlines()
        logs = [x.split('\n')[0] for x in logs]

        performance_data = {}

        target_datetime = datetime.now() - timedelta(hours=3)

        for service in Services:
            performance_data[service] =  {'n_success':0, 'n_failed':0, 'time':0}

        for log in reversed(logs):
            values = log.split(',')
            log_datetime = datetime.strptime(values[0], "%Y-%m-%d %H:%M:%S.%f")
            service = Services[values[1]]
            service_data = performance_data.get(service, {})

            if log_datetime < target_datetime:
                break
            if service in self.working_services:
                break
            
            if values[2].upper() == 'SUCCESS':
                service_data['n_success'] = service_data.get('n', 0) + 1
                service_data['time'] = service_data.get('time', 0) + float(values[3])

            elif values[2].upper() == 'FAILED':
                service_data['n_failed'] = service_data.get('n_failed', 0) + 1
            
            performance_data[service] = service_data
        
        service_metrics = []
        for key in list(performance_data.keys()):
            n_success = performance_data[key].get('n_success', 0)
            n_failed = performance_data[key].get('n_failed', 0)
            success_time = performance_data[key].get('time', 0)
            
            try:
                success_percent = 100 * n_success / (n_success + n_failed)
                success_average_time = success_time / n_success
            except ZeroDivisionError:
                success_percent = 0
                success_average_time = 0

            service_metrics.append([key, success_percent, success_average_time])
        
        sorted_data = sorted(service_metrics, key=lambda x: (x[1], x[2]))
        
        service = sorted_data[0][0]
        # service = random.choice(service_metrics)[0]

        return service
    
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
    
    def __track_service_performance(self, service: Services, success: bool, time_taken):

        now = datetime.now()

        new_log = [str(now), service.value]

        if success:
            new_log.append("SUCCESS")
            new_log.append(str(time_taken))
        else:
            new_log.append("FAILED")

        with open(SERVICE_LOG_FILE_PATH, 'a') as f:

            write = csv.writer(f)
            write.writerows([new_log])

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
                    'error': "Error message TBD",
                    'status': 500
                }
            
        time_taken = datetime.now()
        try:
            async with CachedSession(cache=SQLiteBackend()) as session:
                async with session.get(url, headers = headers, params = query_params, timeout=10) as resp:
                    res = await resp.json()
        
        except Exception as e:
            return {
                'success': False,
                'status': 500,
                'error': "Error in Third Party({}) API call - {}".format(service.value, str(e))
            }
        
        time_taken = datetime.now() - time_taken
        time_taken = time_taken.total_seconds()

        if resp.status >= 500 and resp.status <= 599:
            self.__track_service_performance(service, False, 0)
            print("Third Party Service Failed")

        if resp.status >= 200 and resp.status <= 299:
            self.__track_service_performance(service, True, time_taken)
            print("Third Party Service Worked")
        
        match service:

            case Services.ALPHA_VANTAGE:
                val_res = self.validator.validate_alpha_vantage_response(res)
                if not val_res['success']:
                    return val_res
                stock_instance = self.parser.parse_alpha_vantage_response(res, stock)

            case Services.TWELVE_DATA:
                val_res = self.validator.validate_twelve_data_response(res)
                if not val_res['success']:
                    return val_res
                stock_instance = self.parser.parse_twelve_data_response(res, stock)
            
            case None:
                return {
                    'success': False,
                    'error': "Error message TBD"
                }
        
        return {
            "success": True,
            "stock_instance": stock_instance
        }
