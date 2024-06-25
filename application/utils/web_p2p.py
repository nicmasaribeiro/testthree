#!/usr/bin/env python3

import asyncio
import websockets
import json

class P2P():
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.peers = set()
		self.messages = []
		
	async def handler(self, websocket, path):
		self.peers.add(websocket)
		try:
			async for message in websocket:
				print(f"Received: {message}")
				self.messages.append(message)
				await self.broadcast(message)
		finally:
			self.peers.remove(websocket)
			
	async def broadcast(self, message):
		if self.peers:  # asyncio.wait doesn't accept an empty list
			await asyncio.wait([peer.send(message) for peer in self.peers])
		
	def start_server(self):
		return websockets.serve(self.handler, self.host, self.port)
	
	async def connect_to_peer(self, peer_host, peer_port):
		async with websockets.connect(f"ws://{peer_host}:{peer_port}") as websocket:
			self.peers.add(websocket)
			async for message in websocket:
				print(f"Received from peer: {message}")
				self.messages.append(message)
				
	def get_messages(self):
		return self.messages
	
	async def send_message(self, message):
		await self.broadcast(message)
##		
#if __name__ == "__main__":
#	host = "0.0.0.0"
#	port = 5050
#	
#	node = P2P(host, port)
#	server = node.start_server()
#	
#	asyncio.get_event_loop().run_until_complete(server)
#	asyncio.get_event_loop().run_forever()
