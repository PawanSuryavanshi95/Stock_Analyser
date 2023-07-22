from aiohttp_client_cache import CachedSession, SQLiteBackend
import asyncio
import aiohttp
import re

period_function_mapping = {
    'min': "TIME_SERIES_INTRADAY",
    'D': "TIME_SERIES_DAILY",
    'W': "TIME_SERIES_WEEKLY",
    'M': "TIME_SERIES_MONTHLY"
}


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