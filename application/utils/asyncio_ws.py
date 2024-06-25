import asyncio
import websockets

connected_clients = set()

async def handler(websocket, path):
	# Register client
	connected_clients.add(websocket)
	try:
		async for message in websocket:
			print(f"Received message: {message}")
			# Broadcast message to all connected clients
			for client in connected_clients:
				if client != websocket:
					await client.send(message)
	except websockets.ConnectionClosed:
		print("Client disconnected")
	finally:
		# Unregister client
		connected_clients.remove(websocket)
		
async def main(host,port):
	async with websockets.serve(handler, host, port):
		await asyncio.Future()  # Run forever
#		
#if __name__ == "__main__":
#	asyncio.run(main())
#	