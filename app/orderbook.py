import datetime
from operator import attrgetter
import paho.mqtt.publish as publish

from app import models, db
import config


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


class Exchange():
	"""
	Match orders in the database and handle trades
	"""
	def __init__(self, traded_stocks, messenger):
		self.traded_stocks = traded_stocks
		self.messenger = messenger
	
	def trade(self, stock):
		"""
		Attempt to match best bid/ best ask pairs and complete trades.  Return None if
		no matching pair found.
		"""
		# get best bid & best ask for selected stock
		orders = models.Order.query.filter_by(stock=stock)
		bid = orders.filter_by(side='bid').order_by(models.Order.limit.desc()).first()
		ask = orders.filter_by(side='ask').order_by(models.Order.limit).first()

		# match best bid/ best ask for trade if possible			
		if (bid and ask) and (bid.limit >= ask.limit):
			order_pair = sorted([bid, ask], key=attrgetter('volume'))
			volume = order_pair[0].volume
			order_pair.sort(key=attrgetter('timestamp'))
			price = order_pair[0].limit
			# check in case bidder has insufficient funds			
			if bid.owner.balance < (price * volume):
				# cancel trade and try again
				return True
			else:
				# execute trade
				bid.owner.balance = bid.owner.balance - (volume * price)
				ask.owner.balance = ask.owner.balance + (volume * price)
				for order in (bid, ask):
					order.volume = order.volume - volume
					if order.volume == 0:
						db.session.delete(order)
				db.session.commit()							
				# send messages to buyer and seller
				buy_msg = "{} bought {} {} at ${} each!".format(bid.owner.name,
					volume, bid.stock, price)
				sell_msg = "{} sold {} {} at ${} each!".format(ask.owner.name, 
					volume, ask.stock, price)
				self.messenger.send_message(buy_msg)
				self.messenger.send_message(sell_msg)
				# log trade in ticker
				t = models.Trade(stock=bid.stock, volume=volume, price=price)
				db.session.add(t)
				db.session.commit()
				return True
		
		# no more matched orders, return
		return None

