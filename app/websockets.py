from app import message_queue, sockets, app
import logging

clients = []

@sockets.route('/stream')
def stream_socket(ws):
	clients.append(ws)
	app.logger.info('New websocket client connected')
	while True:
		message = message_queue.get()
		for client in clients:
			try:
				client.send(message)
			except:
				clients.remove(client)
