from sanic import Sanic, json
from sanic.response import text

from routes.root_group import root_group

app = Sanic("StockAnalyser")

app.blueprint(root_group)

@app.get("/")
async def hello_world(request):
    return text("Stock Analyser App \n\nMade By - Pawandeep Suryavanshi")

# if __name__ == '__main__':
#     app.run()