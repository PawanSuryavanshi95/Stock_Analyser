from sanic import Blueprint, json
from sanic.response import text
from sanic_ext import render

from managers.stocks import read_db, add_db, remove_db
from managers.analyse import get_historical_data

analyse_bp = Blueprint('analyse', version = 1,  url_prefix="/analyse")

@analyse_bp.get("/")
async def show(request):    
    return text("Analyse Blueprint Root")

@analyse_bp.route("/historical-analysis/<stock>", methods=['GET', 'POST'])
async def historical_analysis(request, stock):

    candle_size = '1D'
    duration = '1M'

    if request.method == 'POST':
        candle_size = request.form.get('candle_size_dropdown')
        duration = request.form.get('duration_dropdown')

    stock_data = await get_historical_data(candle_size, duration, stock)
    
    return await render(
        "historical_data.html", context={"stock_data": stock_data}, status=200
    )

@analyse_bp.route("/compare/<stocks>", methods=['GET', 'POST'])
async def compare(request, stocks):

    candle_size = '1D'
    duration = '1M' 

    stock1 = stocks.split("&")[0]
    stock2 = stocks.split("&")[1]

    if request.method == 'POST':
        candle_size = request.form.get('candle_size_dropdown')
        duration = request.form.get('duration_dropdown')

    stock_data1 = await get_historical_data(candle_size, duration, stock1)
    stock_data2 = await get_historical_data(candle_size, duration, stock2)

    return await render(
        "comparison.html", context={"stock_data": [stock_data1, stock_data2]}, status=200
    )

@analyse_bp.route("/real-time/<stock>", methods=['GET', 'POST'])
async def real_time(request, stock):

    return await render(
        "real_time_data.html", context={"stock_data": "stock_data"}, status=200
    )