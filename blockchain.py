import shelve
import threading
import pickle
import network
from block import Block

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

		def updateBlockchainNextTick():
			self.update_blockchain()
		t = threading.Timer(1.0, updateBlockchainNextTick)
		t.start() 

	def get_last_block(self):
		return self.store['last_block']

	def update_blockchain(self):
		num_blocks = self.client.telnet_peers_command('num_blocks')
		if int(num_blocks) > self.get_last_block().block_number:
			# Go back and download blocks from this peer
			pass
		else:
			self.verified = True

		# Attempt to update the blockchain every minute
		t = threading.Timer(60.0, self.update_blockchain)
		t.start() 