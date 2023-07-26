from aiohttp_client_cache import CachedSession, SQLiteBackend
import asyncio
import aiohttp

from utils import break_string, make_request
from common import *

class Request:

    url = None

    def __init__(self):
        self.url = URL

    def prepare_url(self, candle_size, stock):
        candle_size_prefix, candle_size_suffix = break_string(candle_size)
        function_type = period_function_mapping.get(candle_size_suffix, "TIME_SERIES_DAILY")
        url = self.url.format(function_type, stock, candle_size, ALPHA_VANTAGE_API_KEY)

        return url

    async def make_get_request(self, candle_size, stock):
        url = self.prepare_url(candle_size, stock)
        try:
            res =  await make_request(url)

            return {
                "success": True,
                "data": res
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
