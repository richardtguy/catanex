from flask import Flask
from flask.json import JSONEncoder
from app import orderbook

class OrderJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, orderbook.Order):
            return obj.toJSON()
        return super(OrderJSONEncoder, self).default(obj)
        

app = Flask(__name__)
app.config.from_object('config')
app.json_encoder = OrderJSONEncoder

ledger = orderbook.Ledger()
messenger = orderbook.Messenger()
stocks = ["sheep", "bricks", "wood"]
book = orderbook.OrderBook(ledger, messenger, stocks)

from app import api, views, orderbook