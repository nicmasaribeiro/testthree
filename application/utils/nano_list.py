
import socket
import os
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
from secrets import token_bytes

token_bytes()
def  main(host,port):
	sock = socket.socket()
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind((host,port))
	sock.listen(5)
	i = 0
	connections=[]
	while True:
		con , addrs = sock.accept()
		connections.append(con)
		datastream = con.recv(2048)
		print(datastream)
		con.close()
main('0.0.0.0', 90)