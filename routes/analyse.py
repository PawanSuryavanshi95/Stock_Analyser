from sanic import Blueprint, json
from sanic.response import text
from sanic_ext import render

from managers.analyse import Analysis
from common import ALPHA_VANTAGE_API_KEY

analyse = Blueprint('analyse', version=1, url_prefix="/analyse")

analysis_manager = Analysis()

@analyse.get("/")
async def show(request):
    return text("Analyse Blueprint Root")

@analyse.get("/historical-data/<stock>")
async def historical_analysis_get(request, stock):
    return await analysis_manager.historical_data(request, stock)

@analyse.get("/compare/<stocks>")
async def compare_get(request, stocks):
    return await analysis_manager.comparison(request, stocks)

@analyse.get("/real-time/<stock>")
async def real_time(request, stock):
    return await render(
        "real_time_data.html", context={"data": {"stock": stock, "api_key": ALPHA_VANTAGE_API_KEY}}, status=200
    )
