
import socket
import threading
from websocket import WebSocketApp
import asyncio

class WS(WebSocketApp):
	def __init__(self, port, host):
		self.signals = []
		self.messages = []
		self.PORT = port
		self.HOST = host
		
	async def websocket_handler(self, websocket, path):
		async for message in websocket:
			logger.info(f"WebSocket received: {message} from {websocket.remote_address}")
			await websocket.send("Hello from server")
			self.signals.append(websocket.remote_address)
			self.messages.append(message)
			return message
		
	async def run_websocket_server(self, host, port):
		async with serve(self.websocket_handler, host, port):
			await asyncio.Future()  # Run forever
		return self.websocket_handler
	
	def start_server(self):
		loop = asyncio.new_event_loop()
		asyncio.set_event_loop(loop)
		loop.run_until_complete(self.run_websocket_server(self.HOST, self.PORT))
		return self.run_websocket_server(self.HOST, self.PORT)
	