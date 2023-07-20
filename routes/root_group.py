from sanic import Blueprint

from routes.stocks import stocks_bp
from routes.analyse import analyse_bp

root_group = Blueprint.group(stocks_bp, analyse_bp, version=1, url_prefix="/")