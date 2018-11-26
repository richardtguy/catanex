from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_sockets import Sockets
import logging
from queue import Queue

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config.from_object('config')
sockets = Sockets(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

message_queue = Queue(10)

from app import orderbook
catan_ex = orderbook.Exchange(["sheep", "bricks", "wood"], 
	orderbook.Messenger(message_queue))

from app import api, views, models, websockets