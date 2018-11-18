from datetime import datetime

from app import db


class Account(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), index=True, unique=True)
	balance = db.Column(db.Integer)
	orders = db.relationship('Order', backref='owner', lazy='dynamic')

	def __repr__(self):
		return '<Account {}>'.format(self.name)

class Order(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
	stock = db.Column(db.String(64), index=True)
	type = db.Column(db.String(8))
	side = db.Column(db.String(8), index=True)
	volume = db.Column(db.Integer)
	limit = db.Column(db.Integer, index=True)
	
	def __repr__(self):
		return '<Order {}>'.format(self.id)
		
class Trade(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	stock = db.Column(db.String(64), index=True)
	volume = db.Column(db.Integer)
	price = db.Column(db.Integer)
	
	def __repr__(self):
		return '<Trade {}>'.format(self.id)