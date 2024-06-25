#!/usr/bin/env python3

import hashlib
import time
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from .classes import *

class PrivateTransaction:
    def __init__(self, from_address, to_address, amount):
        self.web = {"to":[],"from":[]}
        self.from_address = from_address
        self.to_address = to_address
        self.amount = amount
        self.signature = None
		
    def make_transaction(self,cli):
        self.web["to"].append(cli.get_new_key())
        self.web['from'].append(cli.p2p_token())
		
    def calculate_hash(self):
        return hashlib.sha256((str(self.from_address) + str(self.to_address) + str(self.amount)).encode('utf-8')).hexdigest()
	
    def sign_transaction(self, signing_key):
        if signing_key.verifying_key.to_string().hex() != self.from_address:
            raise ValueError('You cannot sign transactions for other wallets!')
			
        hash_tx = self.calculate_hash()
        self.signature = signing_key.sign(hash_tx.encode('utf-8')).hex()
		
    def is_valid(self):
        if not self.from_address:
            return True  # No signature needed for mining reward transaction
		
        if not self.signature:
            raise ValueError('No signature in this transaction')
			
        public_key = VerifyingKey.from_string(bytes.fromhex(self.from_address), SECP256k1)
        return public_key.verify(bytes.fromhex(self.signature), self.calculate_hash().encode('utf-8'))
	
class Block:
    def __init__(self, index, previous_hash, timestamp, transactions, hash=None):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.transactions = transactions
        self.hash = hash or self.calculate_hash()
		
    def calculate_hash(self):
        return hashlib.sha256((str(self.index) + self.previous_hash + str(self.timestamp) + str([tx.__dict__ for tx in self.transactions])).encode('utf-8')).hexdigest()
	
class Blockchain(Network):
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.difficulty = 4
        self.mining_reward = 100
        
    def get_pending(self):
        return self.pending_transactions
            
    def get_approved(self):
        return self.chain
                
    def create_genesis_block(self):
        return Block(0, "0", int(time.time()), [], "0")
	
    def get_latest_block(self):
        return self.chain[-1]
	
    def mine_pending_transactions(self, mining_reward_address):
        reward_tx = Transaction(None, mining_reward_address, self.mining_reward)
        self.pending_transactions.append(reward_tx)
		
        block = Block(len(self.chain), self.get_latest_block().hash, int(time.time()), self.pending_transactions)
        block.hash = block.calculate_hash()  # Simple hash assignment
        self.chain.append(block)
		
        self.pending_transactions = []
		
    def add_transaction(self, transaction):
        if not transaction.from_address or not transaction.to_address:
            raise ValueError('Transaction must include from and to address')
			
        if not transaction.is_valid():
            raise ValueError('Cannot add invalid transaction to chain')
			
        self.pending_transactions.append(transaction)
		
    def get_balance_of_address(self, address):
        balance = 0
        
        for block in self.chain:
            for trans in block.transactions:
                if trans.from_address == address:
                    balance -= trans.amount
					
                if trans.to_address == address:
                    balance += trans.amount
					
        return balance
	
    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
			
            if current_block.hash != current_block.calculate_hash():
                return False
			
            if current_block.previous_hash != previous_block.hash:
                return False
			
            for transaction in current_block.transactions:
                if not transaction.is_valid():
                    return False
				
        return True
    