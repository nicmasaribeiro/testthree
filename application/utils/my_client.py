#!/usr/bin/env python3

from .wallet import PrivateWallet
import socket
from cryptography.hazmat.primitives.asymmetric import rsa as _rsa
from cryptography.hazmat.primitives import serialization
from Crypto.PublicKey import RSA
import json
import rsa
from .classes import Client

#public ,private = rsa.newkeys(2048)
#print(public)

class PrivateClient(Client):
	def __init__(self):
		self.HOST = socket.gethostname()
		self.pending_peers = []
		self.wallet = PrivateWallet()
		self.network_address = {'webhost':[],'signature':[],"key":[],'rsa_address':[]}
		self.receipts = []
		self.private_key_pass = b'1247783'
		self.permanent_pvk = _rsa.generate_private_key(public_exponent=65537,key_size=3072)
		self.public, self.private = rsa.newkeys(3072)
		self.stream = []
		self.wallet = PrivateWallet()
		self.create_genisis()
		
	def generate_key(self):
#		public, private = rsa.newkeys(3072)
		private_key = _rsa.generate_private_key(public_exponent=65537,key_size=3072)
#		self.set_public_key()
		return private_key #RSA.generate(3072)#private_key
	
	def create_genisis(self):
		self.network_address['webhost'].append(socket.gethostname())
		self.network_address['signature'].append(self.wallet.generate_new_address())
		self.network_address['key'].append(self.get_new_key())
		self.network_address['rsa_address'].append(self.get_rsa_address())
		
	def get_rsa_address(self):
		
		private_key = _rsa.generate_private_key(public_exponent=3, key_size=2048)#
		private_key_pass = self.private_key_pass #b"1247783"
		
		encrypted_pem_private_key = private_key.private_bytes(
			encoding=serialization.Encoding.PEM,
			format=serialization.PrivateFormat.PKCS8,
			encryption_algorithm=serialization.BestAvailableEncryption(private_key_pass))
		print(encrypted_pem_private_key.splitlines()[0])
		
		pem_public_key = private_key.public_key().public_bytes(
			encoding=serialization.Encoding.PEM,
			format=serialization.PublicFormat.SubjectPublicKeyInfo
		)
		print(pem_public_key.splitlines()[0])
		return encrypted_pem_private_key
	
	def get_new_key(self):
		return RSA.generate(3072)
	
	def p2p_token(self):
		return str(self.get_new_key())
	
	def handshake(self,port):
		sock = socket.socket()
		sock.connect((self.HOST,port))
		sock.send(b"Send IntraWeb Address")
		data = sock.recv(2048)
		sock.close()
		return data
	
	def decrypt(self):
		unencrypted_pem_private_key = rsa.newkeys(3072).private_bytes(
			encoding=serialization.Encoding.PEM,
			format=serialization.PrivateFormat.TraditionalOpenSSL,
			encryption_algorithm=serialization.NoEncryption())
		return unencrypted_pem_private_key
	
	def encrypt_socket(self,msg,publickey):
		message = msg.encode()
		ciphertext = rsa.encrypt(message, publickey)
		return ciphertext
	
	
	def activate_encrypted_communication(self,port):
		host = socket.gethostname()
		port = port #random.randint(700, 800)  # initiate port no above 1024
		server_socket = socket.socket()  # get instance
		server_socket.bind((self.HOST, port))  # bind host 
		server_socket.listen(100)
		conn, address = server_socket.accept()  # accept new connection
		print("Connection from: " + str(address))
		while True:
			data = conn.recv(1024).decode()
			self.stream.append(data)
			if not data:
				break
			print("from connected user: " + str(data))
			data = input('[+]===> ')
			conn.send(data.encode())  # send data to the client
		conn.close()  # close the connection
		return conn,address
	
	def activate_peer_communication(self,port):
		host = self.HOST
		port = port
		server_socket = socket.socket() 
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server_socket.bind((self.HOST, port))  # bind host 
		server_socket.listen(100)
		conn, address = server_socket.accept()  # accept new connection
		print("Connection from: " + str(address))
		while True:
			conn, address = server_socket.accept()
			data = conn.recv(1024).decode()
			self.stream.append(data)
			if not data:
				break
			print("from connected user: " + str(data))
			data = input(' [+] ===>\n')
			conn.send(data.encode())  # send data to the client
		conn.close()  # close the connection
		return conn,address
	
	def connect_to_peer_communication(self,port):
		sock = socket.socket()
		sock.connect((self.HOST,port))
		while True:
			data = input(" [+] ===>\n").encode()
			sock.send(data)
			print("-->\t",sock.recv(2048).decode())
			
			
	def activate_peer_handshake(self,port,cli):
		token = cli.p2p_token()
		host = socket.gethostname()
		port = port 
		server_socket = socket.socket()  # get instance
		server_socket.bind((self.HOST, port))  # bind host 
		server_socket.listen(100)
		conn, address = server_socket.accept()  # accept new connection
		print("Connection from: " + str(address))
		blob = {'remote_address':address,'connection':conn,'token':token}
		self.stream.append(blob)
		data = token.encode()
		conn.send(data)
		return conn, address
