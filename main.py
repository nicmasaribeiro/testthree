import eventlet
from eventlet import wsgi
from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import pandas as pd
from tenacity import retry
from applescript import tell
import subprocess 
import applescript
import ssl
import json
from flask import Flask,render_template,session,request,redirect
from flask_sqlalchemy import SQLAlchemy
import asyncio
import threading
import logging
from websockets import serve
from websockets.uri import parse_uri
from websockets.client import connect
import socket
from flask_socketio import SocketIO, emit
import websockets
import socket
from application.utils.wallet import PrivateWallet
from flask_bcrypt import Bcrypt
import sys
import os
from application.utils.my_client import PrivateClient
import datetime as dt
from application.models import *
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from cryptography.hazmat.primitives.asymmetric import rsa as _rsa
from cryptography.hazmat.primitives import serialization
from application.utils.classes import Investment, Coin, Validator
from application.utils.BC import *
from blinker import signal, Signal,ANY
from routes import datastream


global Network
Network = Blockchain()
global Coin
Coin = Coin()

HOST = socket.gethostname()


#send = signal('send')
#
#@app.route('/signal')
#def receive_data():
#	sig = Signal()
#	sig.send()
#	print(f"Caught signal from {sig!r}, data")
#	return "Success"
#
#send_data = signal('send-data')
#
#@send_data.connect
#def receive_data(sender, **kw):
#	print(f"Caught signal from {sender!r}, data {kw!r}")
#	return 'received!'
#
#
#result = send_data.send('anonymous', abc=123)

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.route('/signup', methods=['POST','GET'])
def signup():
	if request.method =="POST":
		password = request.values.get("password")
		username = request.values.get("username")
		email = request.values.get("email")
		hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
		rsa_key = str(RSA.generate(3072))
		token = get_random_bytes(3072)
		new_wallet = WalletDatabase(address=PrivateClient().get_rsa_address(),token=PrivateClient().get_new_key())
		new_user = User(username=username, email=email, password=hashed_password,personal_token=token,rsa_key=rsa_key)
		db.session.add(new_user)
		db.session.commit()
		return jsonify({'message': 'User created!'}), 201
	return render_template("signup.html")

@app.route('/login', methods=['POST','GET'])
def login():
	if request.method == "POST":
		username = request.values.get("username")
		password = request.values.get("password")
		user = User.query.filter_by(username=username).first()
		if user and bcrypt.check_password_hash(user.password, password):
			login_user(user)
			return redirect('/users')# jsonify({'message': 'Logged in successfully!'}), 200
		else:
			return redirect('/signup')
	return render_template("login.html")


@app.route('/users', methods=['GET'])
@login_required
def get_users():
	users = User.query.all()
	users_list = [{'id': user.id, 'username': user.username, 'email': user.email,'publicKey':str(user.rsa_key)} for user in users]
	return jsonify(users_list)

@app.route('/users/<int:id>/<pswd>', methods=['GET'])
def get_user(id,pswd):
	user = User.query.get_or_404(id)
	w = user.private_wallet
#	if bcrypt.check_password_hash(user.password, pswd) == False:
	return jsonify({'id': user.id, 'username': user.username, 'email': user.email,'publicKey':user.private_wallet.public_key,'token':w.generate_new_address()})
#	else:
#		return redirect('/')

@app.route('/update/users/<int:id>', methods=['PUT'])
def update_user(id):
	data = request.get_json()
	user = User.query.get_or_404(id)
	user.username = data['username']
	user.email = data['email']
	db.session.commit()
	return jsonify({'message': 'User updated!'})

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
	user = User.query.get_or_404(id)
	db.session.delete(user)
	db.session.commit()
	return jsonify({'message': 'User deleted!'})

@app.route('/')
def start():
	return render_template('index.html')


@app.route('/transact',methods=['GET','POST'])
@login_required
def transact():
	if request.method == "POST":
		id_from = request.values.get("username_from")
		id_to = request.values.get("username_to")
		value = request.values.get("value")
#		
		user = User.query.get_or_404(id_from)
		user2 = User.query.get_or_404(id_to)
		
		from_addrs = user.rsa_key
		to_addrs = user2.rsa_key
		
		new_transaction = TransactionDatabase(txid=str(os.urandom(1024)),from_address = from_addrs, to_address = to_addrs, amount = value,type='send')
		db.session.add(new_transaction)
		db.session.commit()
		transaction = {'from_address': str(user.rsa_key),'to_address': str(user2.private_wallet.public_key),'amount': value}
		singnature = user2.private_wallet.sign_transaction(transaction)
		data = json.dumps({'from_addrs': str(from_addrs) ,'value': value,'to_addrs': str(to_addrs),'signature': str(singnature)})
		Network.add_transaction(transaction)
		Network.set_transaction(user.private_client.permanent_pvk, to_addrs, value)
		return  data
	return render_template("trans.html")

@app.route('/get/transactions',methods=['GET'])
@login_required
def get_transactions():
	transports = TransactionDatabase.query.all()
	transports_list = [{'id': t.id, 'from_address':str(t.from_address),'to_address':str(t.to_address),'txid':t.txid,'value':t.amount} for t in transports]
	return jsonify(transports_list)


##########################
# Usage Still Considering
##########################

@app.route('/atd/<int:port>')
def activate(port):
	from application.utils.p2p import P2P
	node_server = P2P(socket.gethostname(), 3030)
	thread = threading.Thread(target=node_server.start_server)
	thread.start()
	return "Success"

@app.route('/ctd/<int:port>')
def ctd(port):
	from application.utils.p2p import P2P
	node_server = P2P(socket.gethostname(), 3030)
	thread = threading.Thread(target=node_server.connect_to_peer,args=(socket.gethostname(), 3030))
	thread.start()
	node_server.broadcast("message")
	return "Success"

@app.route('/broadcast/<data>')
def broadcast(data):
	from application.utils.p2p import P2P
	node_server = P2P(socket.gethostname(), 3030)
	node_server.connect_to_peer(socket.gethostname(), 3030)
	node_server.broadcast(data)
	return redirect('/')#render_template('broadcast.html')
	
if __name__ == '__main__':
	with app.app_context():
		db.create_all()
	app.run(host="192.168.1.237",port=5050)
#	wsgi.server(eventlet.listen(("0.0.0.0", 8080)), app)