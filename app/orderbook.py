import datetime
from operator import attrgetter
from twilio.rest import Client as TwilioClient
import paho.mqtt.publish as publish


import app
import config

class Ledger():
	"""
	Manage participants account balances
	"""

	def __init__(self):
		self.accounts = []

	def add_account(self, name):
		# check if account already exists
		account = [a for a in self.accounts if a['name'] == name]
		if not account:
			self.accounts.append({'name': name, 'balance': config.OPENING_BALANCE
			})
			return {'name': name, 'balance': config.OPENING_BALANCE}
		else:
			return False

	def get_phone(self, name):
		try:
			account = [a for a in self.accounts if a['name'] == name][0]
		except IndexError:
			return None
		return account['phone']

	def get_balance(self, name):
		try:
			account = [a for a in self.accounts if a['name'] == name][0]
		except IndexError:
			return None
		return account['balance']
		
	def process_debit(self, name, amount):
		account = [a for a in self.accounts if a['name'] == name][0]
		account['balance'] -= amount

	def process_credit(self, name, amount):
		account = [a for a in self.accounts if a['name'] == name][0]
		account['balance'] += amount
		
	def delete_accounts(self):
		self.accounts = []


class Messenger():
	"""
	Dispatch messages about executed trades to participants by MQTT
	"""
	def send_message(self, message, phone=""):
		publish.single(
			"/exchange", 
			payload=message,
			qos=1,
			hostname=config.MQTT_HOST,
			port=config.MQTT_PORT,
			auth={"username":config.MQTT_USER, "password":config.MQTT_PASSWORD}
		)


class OrderBook():
	"""
	Maintain register of limit orders and execute trades
	"""
	def __init__(self, ledger, messenger, traded_stocks):
		if not (isinstance(ledger, Ledger) and 
			isinstance(messenger, Messenger)
		): raise TypeError
		self.ledger = ledger
		self.messenger = messenger
		self.ticker = []
		self.traded_stocks = traded_stocks
		self.bids = []
		self.asks = []
		self.latest_prices = {}
		for stock in self.traded_stocks:
			self.latest_prices[stock] = None

	def add_order(self, new_order):
		# add order to book
		if new_order.side == "ask":
			self.asks.append(new_order)
		elif new_order.side == "bid":
			self.bids.append(new_order)
		# match bid/ask pairs until no further trades possible
		while(self.process_orders(new_order.stock)):
			pass
		return new_order.id
		
	def pop_order_by_id(self, id):
		"""
		Remove selected order from order book and return a copy
		"""
		for list in (self.bids, self.asks):
			for o in list:
				if o.id == id:
					list.remove(o)
					return o
		return None

	def get_order_by_id(self, id):
		"""
		Find selected order in order book and return a copy
		"""
		for list in (self.bids, self.asks):
			for o in list:
				if o.id == id:
					return o
		return None

	def process_orders(self, stock):
		"""
		Attempt to match best bid/ best ask pairs and complete trades.  Return None if
		no matching pair found.
		"""
		# pop best bid/ best ask for selected stock from order book
		bids = [o for o in self.bids if o.stock == stock]
		bids.sort(key = lambda x: (x.limit * -1, x.timestamp))
		if len(bids) > 0:
			bid = self.pop_order_by_id(bids[0].id)
		else:
			bid = None
		asks = [o for o in self.asks if o.stock == stock]
		asks.sort(key = lambda x: (x.limit, x.timestamp))
		if len(asks) > 0:
			ask = self.pop_order_by_id(asks[0].id)
		else:
			ask = None
		
		# match best bid/ best ask for trade if possible			
		if (bid and ask) and (bid.limit >= ask.limit):
			order_pair = sorted([bid, ask], key=attrgetter('volume'))
			volume = order_pair[0].volume
			order_pair.sort(key=attrgetter('timestamp'))
			price = order_pair[0].limit
			if self.ledger.get_balance(bid.account) < (price * volume):
				# if buyer has insufficient funds, cancel bid, write ask back into order 
				# book unchanged, and return True to try again with next bid
				self.cancel_order(bid.id)
				self.asks.append(ask)
				return True
			else:
				# execute trade
				for order in order_pair:
					order.volume -= volume
				if bid.volume > 0:
					self.bids.append(bid)
				elif ask.volume > 0:
					self.asks.append(ask)
				self.ledger.process_debit(bid.account, volume * price)
				self.ledger.process_credit(ask.account, volume * price)
				# send messages to buyer and seller
				buy_msg = "{} bought {} {} at ${} each!".format(bid.account,
					volume, bid.stock, price)
				sell_msg = "{} sold {} {} at ${} each!".format(ask.account, 
					volume, ask.stock, price)
				self.messenger.send_message(buy_msg)
				self.messenger.send_message(sell_msg)
				# log trade in ticker
				self.ticker.append({'volume': volume,
					'stock': ask.stock,
					'price': price,
					'timestamp': datetime.datetime.now()
				})
				# update latest executed price
				self.latest_prices[stock] = price
				return True
		
		# return bid and/or ask to order book
		if bid: self.bids.append(bid)
		if ask: self.asks.append(ask)
		return None

	def cancel_order(self, id):
		# Remove an order from the order book using the id
		self.bids[:] = [o for o in self.bids if o.id != id]
		self.asks[:] = [o for o in self.asks if o.id != id]

	def get_best_prices_by_stock(self, stock):
		# return best bid and ask price for each stock type
		try:
			best_bid = max(o.limit for o in [o for o in self.bids if o.stock == stock])
		except ValueError:
			best_bid = None
		try:
			best_ask = min(o.limit for o in [o for o in self.asks if o.stock == stock])
		except:
			best_ask = None	
		return (best_bid, best_ask)

	def get_latest_prices(self):
		# return dictionary of latest price for each stock
		return self.latest_prices
		
	def all_orders_toJSON(self):
		# return list of all orders in JSON format	
		return {"bids": self.bids, "asks": self.asks}

	def orders_by_account_toJSON(self, account):
		# return list of orders for specified account in JSON format
		bids = [o for o in self.bids if o.account == account]
		asks = [o for o in self.asks if o.account == account]		
		return {"bids": bids, "asks": asks}
		# should return error if account not found

	def delete_all(self):
		# Delete all orders and accounts from the order book
		self.bids = []
		self.asks = []
		self.ledger.delete_accounts()


class Order():
	"""
	Represents an order to buy or sell a stock at a specified limit price
	"""

	def __init__(self, account, stock, type, side, volume, limit):

		# timestamp when order received
		self.timestamp = datetime.datetime.now()
		# construct id from timestamp & account name
		self.id = str(self.timestamp.isoformat()) + str(account)			
		self.account = account			# account id
		self.stock = stock				# stock
		self.type = type				# limit or market
		self.side = side		 		# bid or ask
		self.volume = volume			# quantity ordered
		self.limit = limit				# limit price (if applicable)

	def toJSON(self):
		return self.__dict__