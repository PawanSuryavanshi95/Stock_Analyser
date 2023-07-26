from sanic import json
from sanic.response import text
from sanic_ext import render

class Response:

    def __init__(self):
        pass

    def text_response(self, content):
        return text(content)
    
    def json_response_failed(self, data):
        return json({"data": data})
    
    async def render_response(self, template, context):
        return await render(
            template,
            context=context,
            status=200
        )