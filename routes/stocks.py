from sanic import Blueprint, json
from sanic.response import text

from managers.stocks import read_db, add_db, remove_db

stocks_bp = Blueprint('stock_list', version = 1,  url_prefix="/stocks")

@stocks_bp.get("/")
async def show(request):
    
    return text("Stocks Blueprint Root")

@stocks_bp.get("/show-list")
async def show_list(request):
    rows = await read_db()
    return json({"stock_list": rows})

@stocks_bp.post("/add-stock")
async def add_stock(request):
    body = request.json
    
    result = await add_db(body['stock_name'])

    if result:
        return text("Success")
    
    return text("Failed")

@stocks_bp.post("/remove-stock")
async def remove_stock(request):
    body = request.json
    
    result = await remove_db(body['stock_name'])
    
    if result:
        return text("Success")
    
    return text("Failed")
