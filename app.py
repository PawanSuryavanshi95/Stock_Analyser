from sanic import Sanic, json
from sanic.response import text

from models import Services

from routes import routes
from handlers import Request

app = Sanic("StockAnalyser", request_class=Request)

app.blueprint(routes)

@app.before_server_start
async def check_service_availability(app, _):
    working_services = await Services.get_working_services()
    app.ctx.working_services = working_services
    print("Working Services :", working_services)

@app.get("/")
async def hello_world(request):
    return text("Stock Analyser App \n\nMade By - Pawandeep Suryavanshi")

@app.get("/help")
async def help(request):
    return text("Stock Analyser App \n\nMade By - Pawandeep Suryavanshi")

if __name__ == '__main__':
    app.run()