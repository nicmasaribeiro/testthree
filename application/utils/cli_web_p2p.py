#!/usr/bin/env python3

import asyncio
import json
from web_p2p import P2P
import socket

async def main(host,port):
	host = host
	port = port
	node = P2P(host, port)
	server = node.start_server()
	
	# Start the server
	asyncio.get_event_loop().run_until_complete(server)
	
	# Connect to a peer
	peer_host = host
	peer_port = port
	await node.connect_to_peer(peer_host, peer_port)
	
	# Send a message
	message = json.dumps({'from':'nmr','to':'gzago','value':100})
	
	await node.send_message(message)
	
	# Keep the event loop running
	await asyncio.get_event_loop().run_forever()
	
if __name__ == "__main__":
	main('0.0.0.0',5050)
	