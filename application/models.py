from flask import Flask, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
import enum
from flask_bcrypt import Bcrypt
from application.utils.BC import Blockchain, Block, PrivateTransaction
from application.utils.wallet import PrivateWallet
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from application.utils.my_client import PrivateClient
import socket

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blockchain.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize SQLAlchemy
db = SQLAlchemy(app)
# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt(app)
login_manager.login_view = 'login'

class WalletDatabase(db.Model):
    __tablename__ = 'wallets'
    
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String, unique=True, nullable=False)
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    token = db.Column(db.String(3072))

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    private_wallet = PrivateWallet()
    private_client = PrivateClient()
    personal_token = db.Column(db.LargeBinary(3072))
    rsa_key = db.Column(db.String(3072))
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=True)
    wallet = db.relationship('Wallet', backref='user', uselist=False)
#   random_bits_string = get_random_bytes(3072)
    

class TransactionType(enum.Enum):
    send = "send"
    receive = "receive"
    
class TransactionDatabase(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    txid = db.Column(db.String, unique=True, nullable=False)
    from_address = db.Column(db.String, db.ForeignKey('wallets.address'))
    to_address = db.Column(db.String, db.ForeignKey('wallets.address'))
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.Enum(TransactionType), nullable=False)
    
    from_wallet = db.relationship('Wallet', foreign_keys=[from_address])
    to_wallet = db.relationship('Wallet', foreign_keys=[to_address])
    
class Peer(db.Model):
    __tablename__ = 'peers'
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String, unique=True, nullable=False)
    port = db.Column(db.Integer, nullable=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    client = PrivateClient()
    
class Block(db.Model):
    __tablename__ = 'blocks'
    
    id = db.Column(db.Integer, primary_key=True)
    index = db.Column(db.Integer, unique=True, nullable=False)
    previous_hash = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    nonce = db.Column(db.Integer, nullable=False)
    hash = db.Column(db.String, unique=True, nullable=False)
    
class MiningStatus(enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    
class MiningJob(db.Model):
    __tablename__ = 'mining_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id'), nullable=False)
    miner_address = db.Column(db.String, db.ForeignKey('wallets.address'), nullable=False)
    status = db.Column(db.Enum(MiningStatus), default=MiningStatus.pending)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    block = db.relationship('Block')
    miner = db.relationship('Wallet')

    