from utils import do_ping
from common import *
from aiohttp_client_cache import CachedSession, SQLiteBackend

from functools import wraps

# async def get_working_services():

#     working_services = []
           
#     for service in Services:
#         host = service_host_mapping.get(service.value)
#         output = await do_ping(host)

#         if output:
#             working_services.append(service)

#     return working_services

def validate_historical(func):
    @wraps(func)
    async def decorated_function(request, *args, **kwargs):



        return await func(request, *args, **kwargs)

    return decorated_function

def validate_compare(func):
    @wraps(func)
    async def decorated_function(request, *args, **kwargs):

        

        return await func(request, *args, **kwargs)

    return decorated_function