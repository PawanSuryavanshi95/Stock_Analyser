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

    period = '5min'

    if request.method == 'POST':
        period = request.form.get('period_dropdown')

    stock_data = get_historical_data(period, stock)
    
    return await render(
        "historical_data.html", context={"stock_data": stock_data}, status=200
    )