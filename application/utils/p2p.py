#!/usr/bin/env python3

import socket
import threading
import json

class P2P():
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.peers = []
		self.messages = []
		
	def start_server(self):
		server_thread = threading.Thread(target=self.run_server)
		server_thread.start()
		
	def run_server(self):
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_socket.bind((self.host, self.port))
		server_socket.listen(5)
		print(f"Server started at {self.host}:{self.port}")
		
		while True:
			client_socket, addr = server_socket.accept()
			print(f"Connection from {addr}")
			client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
			client_thread.start()
			
	def handle_client(self, client_socket):
		while True:
			try:
				message = client_socket.recv(1024).decode()
				if message:
					print(f"Received: {message}")
					self.broadcast(message)
				else:
					break
			except:
				break
		client_socket.close()
		
	def connect_to_peer(self, peer_host, peer_port):
		peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		peer_socket.connect((peer_host, peer_port))
		self.peers.append(peer_socket)
		listen_thread = threading.Thread(target=self.listen_to_peer, args=(peer_socket,))
		listen_thread.start()
		return self.messages
	
	def listen_to_peer(self, peer_socket):
		while True:
			try:
				message = peer_socket.recv(1024).decode()
				self.messages.append(message)
				if message:
					print(f"Received from peer: {message}")
				else:
					break
			except:
				break
		peer_socket.close()
		
	def broadcast(self, message):
		for peer_socket in self.peers:
			try:
				peer_socket.sendall(message.encode())
			except:
				self.peers.remove(peer_socket)
	
	def get_messages(self):
		
		return self.messages
	
	def send_message(self, message):
		self.broadcast(message)


##if __name__ == "__main__":
#   host = "192.168.1.237"
#   port = 5050
##
#   node = P2P(host, port)
#   node.start_server()
##   node.connect_to_peer(host, 8097)
##   # Example to connect to another peer
##   peer_host = "192.168.1.237"
##   peer_port = 3030
##   node.connect_to_peer(peer_host, peer_port)
##
#   while True:
#       message = input("Enter message to broadcast: ")
#       node.send_message(message)
		