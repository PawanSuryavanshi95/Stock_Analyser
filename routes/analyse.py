from sanic import Blueprint, json
from sanic.response import text
from sanic_ext import render

from managers.stocks import read_db, add_db, remove_db, update_preferences, get_preferences
from managers.analyse import get_historical_data

analyse_bp = Blueprint('analyse', version = 1,  url_prefix="/analyse")

@analyse_bp.get("/")
async def show(request):    
    return text("Analyse Blueprint Root")

@analyse_bp.route("/historical-analysis/<stock>", methods=['GET', 'POST'])
async def historical_analysis(request, stock):

    rows = await get_preferences()
    stock_list = await read_db()

    candle_size = rows[0]
    duration = rows[1]

    if request.method == 'POST':
        candle_size = request.form.get('candle_size_dropdown')
        duration = request.form.get('duration_dropdown')

        await update_preferences(candle_size, duration)

    success, stock_data = await get_historical_data(candle_size, duration, stock)

    if success:
        await add_db(stock)
        return await render(
            "historical_data.html",
            context = {
                "stock_data": stock_data,
                "preferences":[ candle_size, duration],
                "previous_stocks": stock_list
            },
            status=200
        )
    
    return text("Something Went Wrong :( \nRefer to the below message\n" + str(stock_data))

@analyse_bp.route("/compare/<stocks>", methods=['GET', 'POST'])
async def compare(request, stocks):

    rows = await get_preferences()
    stock_list = await read_db()

    candle_size = rows[0]
    duration = rows[1]

    if len(stocks.split("&")) != 2:
        return text("Invalid format of stocks passed. Please pass <stock_1>&<stock_2> after 'compare' route.")

    stock1 = stocks.split("&")[0]
    stock2 = stocks.split("&")[1]

    await add_db(stock1)
    await add_db(stock2)

    if request.method == 'POST':
        candle_size = request.form.get('candle_size_dropdown')
        duration = request.form.get('duration_dropdown')

        await update_preferences(candle_size, duration)

    success1, stock_data1 = await get_historical_data(candle_size, duration, stock1)
    success2, stock_data2 = await get_historical_data(candle_size, duration, stock2)

    if not success1:
        return text("Something Went Wrong :( \nRefer to the below message\n" + str(stock_data1))
    
    if not success2:
        return text("Something Went Wrong :( \nRefer to the below message\n" + str(stock_data2))
    
    return await render(
        "comparison.html",
        context = {
            "stock_data": [stock_data1, stock_data2],
            "preferences":[ candle_size, duration],
            "previous_stocks": stock_list
        },
        status=200
    )

@analyse_bp.route("/real-time/<stock>", methods=['GET', 'POST'])
async def real_time(request, stock):

    return await render(
        "real_time_data.html", context={"data": {"stock": stock}}, status=200
    )