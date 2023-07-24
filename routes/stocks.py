from sanic import Blueprint, json
from sanic.response import text

from managers.stocks import read_stock, add_stock, remove_stock

stocks = Blueprint('stock_list', version = 1,  url_prefix="/stocks")

@stocks.get("/")
async def show(request):
    
    return text("Stocks Blueprint Root")

@stocks.get("/show-list")
async def show_list(request):
    rows = await read_stock()
    return json({"stock_list": rows})

@stocks.post("/add-stock")
async def add_stock(request):
    body = request.json
    
    result = await add_stock(body['stock_name'])

    if result:
        return text("Success")
    
    return text("Failed")

@stocks.post("/remove-stock")
async def remove_stock(request):
    body = request.json
    
    result = await remove_stock(body['stock_name'])
    
    if result:
        return text("Success")
    
    return text("Failed")
