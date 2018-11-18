from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask.json import JSONEncoder

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import orderbook
catan_ex = orderbook.Exchange(["sheep", "bricks", "wood"], orderbook.Messenger())

from app import api, views, models
