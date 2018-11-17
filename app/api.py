"""
REST API for CatanEX exchange
"""

from app import app
from app import book

from app import orderbook
from app import ledger

from flask import abort, make_response, jsonify, request
import datetime
import json

# Add a new order to the order book
@app.route('/api/orders', methods=['POST'])
def place_order():
	r = request.get_json()
	order = orderbook.Order(
		account=r['account'],
		stock=r['stock'],
		type=r['type'],
		side=r['side'],
		volume=r['volume'],
		limit=r['limit'])
	new_id = book.add_order(order)
	o = book.get_order_by_id(new_id)
	if o:
		# order added to order book
		response = {
			"id": o.id,
			"side": o.side,
			"volume":o.volume,
			"limit":o.limit,
			"status":"open"
		}
		return make_response(jsonify({"response":response}), 200)
	else:
		# order not entered into order book as it was settled immediately
		return make_response(jsonify({"response":{
			"id":new_id,
			"status":"complete"	
		}}), 200)

# Cancel an order in the order book
@app.route('/api/orders/<id>', methods=['DELETE'])
def cancel_order_by_id(id):
	book.cancel_order(id)
	return make_response(jsonify({"response": id}), 200)

# Return a list of all orders in the book for a specified account
@app.route('/api/orders/<account>', methods=['GET'])
def list_orders_by_account(account):
	# should return 404 if account not found
	return make_response(jsonify(book.orders_by_account_toJSON(account)), 200)

# Return a list of all orders in the book
@app.route('/api/orders', methods=['GET'])
def list_orders():
	return make_response(jsonify(book.all_orders_toJSON()), 200)
	
# Return list of stocks traded on the exchange
@app.route('/api/stocks', methods=['GET'])
def get_traded_stocks():
	return make_response(jsonify({"stocks": book.traded_stocks}), 200)

# Get best bid/ask and latest executed price for all stocks traded on exchange
@app.route('/api/prices', methods=['GET'])
def get_best_prices():
	prices = []
	latest_prices = book.get_latest_prices()
	for stock in book.traded_stocks:
		best_bid, best_ask = book.get_best_prices_by_stock(stock)
		prices.append({'stock': stock,
			'best_bid': best_bid,
			'best_ask': best_ask,
			'last':			latest_prices[stock]
		})
	return make_response(jsonify(prices), 200)

# Add an account
@app.route('/api/accounts', methods=['POST'])
def add_account():
	r = request.get_json()
	response = ledger.add_account(r['name'])
	if response: 
		return make_response(jsonify({"response":response}), 200)
	else:
		return make_response(jsonify({"response":"account already exists"}), 403)
			
# Get balance on an account
@app.route('/api/accounts/<name>', methods=['GET'])
def get_balance(name):
	balance = ledger.get_balance(name)
	if balance == None:
		return make_response(jsonify({"response":"account does not exist"}), 404)
	else:
		return make_response(jsonify({"balance": ledger.get_balance(name)}), 200)
	
# Delete all orders and accounts from the order book and ledger
@app.route('/api', methods=['DELETE'])
def delete_all():
	book.delete_all()
	return make_response(jsonify({"response":"deleted all orders and accounts"}), 200)
