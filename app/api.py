"""
REST API for CatanEX exchange
"""
import config
from app import app, models, db, catan_ex

from flask import abort, make_response, jsonify, request
import datetime
import json
import itertools

# Add a new order to the order book
@app.route('/api/orders', methods=['POST'])
def place_order():
	r = request.get_json()
	account = models.Account.query.filter_by(name=r['account']).first()
	o = models.Order(
		owner=account,
		stock=r['stock'],
		type=r['type'],
		side=r['side'],
		volume=r['volume'],
		limit=r['limit']
	)
	db.session.add(o)
	db.session.commit()
	response = {
		"id": o.id,
		"side": o.side,
		"volume":o.volume,
		"limit":o.limit,
		"status":"open"
	}
	catan_ex.trade(r['stock'])
	return make_response(jsonify({"response":response}), 200)

# Cancel an order in the order book
@app.route('/api/orders/<id>', methods=['DELETE'])
def cancel_order_by_id(id):
	o = models.Order.query.get(id)
	db.session.delete(o)
	db.session.commit()
	return make_response(jsonify({"response": id}), 200)

# Return a list of all orders in the book for a specified account
@app.route('/api/orders/<account>', methods=['GET'])
def list_orders_by_account(account):
	account = models.Account.query.filter_by(name=account).first()
	orders = account.orders.all()
	response = []
	for order in orders:
		response.append({
			'timestamp':order.timestamp,
			'stock':order.stock,
			'side':order.side,
			'volume':order.volume,
			'limit':order.limit,
			'id':order.id
		})
	return make_response(jsonify(response), 200)

# Return a list of all orders in the book
@app.route('/api/orders', methods=['GET'])
def list_orders():
	orders = models.Order.query.all()
	for order in orders:
		response.append({
			'timestamp':order.timestamp,
			'stock':order.stock,
			'side':order.side,
			'volume':order.volume,
			'limit':order.limit,
			'id':order.id
		})
	return make_response(jsonify(response), 200)
	
# Return list of stocks traded on the exchange
@app.route('/api/stocks', methods=['GET'])
def get_traded_stocks():
	return make_response(jsonify({"stocks": catan_ex.traded_stocks}), 200)

# Get best bid/ask and latest executed price for all stocks traded on exchange
@app.route('/api/prices', methods=['GET'])
def get_best_prices():
	prices = []
	for stock in catan_ex.traded_stocks:
		orders = models.Order.query.filter_by(stock=stock)
		best_bid = orders.filter_by(side='bid').order_by(models.Order.limit.desc()).first()
		if best_bid == None:
			best_bid_price = None
		else:
			best_bid_price = best_bid.limit
		best_ask = (orders.filter_by(stock=stock).filter_by(side='ask').
			order_by(models.Order.limit).first()
		)
		if best_ask == None:
			best_ask_price = None
		else:
			best_ask_price = best_ask.limit
		last_trade = (models.Trade.query.filter_by(stock=stock).
			order_by(models.Trade.timestamp.desc()).first()
		)
		if last_trade ==  None:
			last_price = None
		else:
			last_price = last_trade.price
		prices.append({'stock': stock,
			'best_bid': best_bid_price,
			'best_ask': best_ask_price,
			'last':			last_price
		})
	return make_response(jsonify(prices), 200)

# Add an account
@app.route('/api/accounts', methods=['POST'])
def add_account():
	r = request.get_json()
	a = models.Account(name=r['name'], balance=config.OPENING_BALANCE)
	db.session.add(a)
	db.session.commit()
	return make_response(jsonify({"response":{
		'name': a.name, 'balance': a.balance
	}}), 200)

# Get balance on an account
@app.route('/api/accounts/<name>', methods=['GET'])
def get_balance(name):
	account = models.Account.query.filter_by(name=name).first()
	if account == None:
		return make_response(jsonify({"response":"account does not exist"}), 404)
	else:
		return make_response(jsonify({"balance": account.balance}), 200)

# Delete all orders, trades and accounts
@app.route('/api', methods=['DELETE'])
def delete_all():
	accounts = models.Account.query.all()
	orders = models.Order.query.all()
	trades = models.Trade.query.all()
	for item in itertools.chain(accounts, orders, trades):
		db.session.delete(item)
	db.session.commit()
	return make_response(jsonify({"response":"deleted all orders and accounts"}), 200)