import shelve
import threading
import pickle
import network
from block import Block
from balance_manager import BalanceManager

class Blockchain:
	'A class representing the Blockchain'

	def __init__(self):
		self.store = shelve.open('blockchain.store', flag='c', protocol=None, writeback=True)
		if len(self.store) == 0:
			# Make the head block the genesis block
			self.store['head_block'] = Block()
			self.store['last_block'] = self.store['head_block']

		self.client = network.DriveCoinClient.Instance()
		self.verified = False
		self.balances = BalanceManager()

		def updateBlockchainNextTick():
			self.update_blockchain()
		t = threading.Timer(1.0, updateBlockchainNextTick)
		t.start() 

	def get_last_block(self):
		return self.store['last_block']

	def get_balances(self):
		return self.balances

	def calculate_balances(self):
		block = self.store['head_block']
		while block != None:
			transactions = block.block_information['transaction_list']
			for transaction in transactions:
				self.balances.add_to_address(transaction.sender, -1*transaction.amount)
				self.balances.add_to_address(transaction.recipient, transaction.amount)
			# Reward the miner with one DriveCoin
			self.balances.add_to_address(block.block_information['coinbase_address'], 1*(10**9))
			block = block.next_block

	def update_blockchain(self):
		num_blocks = self.client.telnet_peers_command('num_blocks')
		if int(num_blocks) > self.get_last_block().block_number:
			# TODO Go back and download blocks from this peer
			self.calculate_balances()
		else:
			self.calculate_balances()
			self.verified = True

		# Attempt to update the blockchain every minute
		t = threading.Timer(60.0, self.update_blockchain)
		t.start() 