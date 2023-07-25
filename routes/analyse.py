from sanic import Blueprint, json
from sanic.response import text
from sanic_ext import render

from managers.stocks import read_stock, add_stock, remove_stock, update_preferences, get_preferences
from managers.analyse import analysis_manager

analyse = Blueprint('analyse', version=1, url_prefix="/analyse")


@analyse.get("/")
async def show(request):
    return text("Analyse Blueprint Root")


@analyse.get("/historical-analysis/<stock>")
async def historical_analysis_get(request, stock):
    return await analysis_manager(request, [stock], "historical_data.html", False)


@analyse.post("/historical-analysis/<stock>")
async def historical_analysis_post(request, stock):
    return await analysis_manager(request, [stock], "historical_data.html")


@analyse.get("/compare/<stocks>")
async def compare_get(request, stocks):
    stock_list = stocks.split("&")
    if len(stock_list) != 2:
        return text("Invalid format of stocks passed. Please pass <stock_1>&<stock_2> after 'compare' route.")

    return await analysis_manager(request, stock_list, "comparison.html", False)


@analyse.post("/compare/<stocks>")
async def compare_post(request, stocks):
    stock_list = stocks.split("&")
    if len(stock_list) != 2:
        return text("Invalid format of stocks passed. Please pass <stock_1>&<stock_2> after 'compare' route.")

    return await analysis_manager(request, stock_list, "comparison.html")


@analyse.get("/real-time/<stock>")
async def real_time(request, stock):
    return await render(
        "real_time_data.html", context={"data": {"stock": stock}}, status=200
    )
