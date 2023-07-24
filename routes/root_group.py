from sanic import Blueprint

from routes.stocks import stocks
from routes.analyse import analyse

root_group = Blueprint.group(stocks, analyse, version=1, url_prefix="/")