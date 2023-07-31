from enum import Enum
import aiohttp
import asyncio

from common import *

class Services(Enum):
    ALPHA_VANTAGE = "ALPHA_VANTAGE"
    TWELVE_DATA = "TWELVE_DATA"

    async def __custom_ping(session, service):
        print("Custom Ping:", service)
        try:
            async with session.get(service_host_mapping[service.value], headers = service_headers_mapping[service.value], timeout=10) as resp:
                pass
            return (service, True)
        except Exception as e:
            return (service, False)

    @classmethod
    async def get_working_services(self):
        working_services = []

        async with aiohttp.ClientSession() as session:
            tasks = []
            for service in self:
                new_task = asyncio.get_event_loop().create_task(self.__custom_ping(session, service))
                tasks.append(new_task)
            
            group = await asyncio.gather(*tasks,return_exceptions=True)
          
        for output in group:
            if output[1]:
                working_services.append(output[0])
        
        return working_services