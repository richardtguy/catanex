from app import message_queue, sockets

clients = []

@sockets.route('/stream')
def stream_socket(ws):
	clients.append(ws)
	while True:
		message = message_queue.get()
		for client in clients:
			try:
				client.send(message)
			except:
				clients.remove(client)
