from Crypto.Hash import SHA
import datetime
import urllib2
import tree

BEACON = 'http://127.0.0.1:8080/'

class Block:
	'A class representing the DriveCoin block specification'

	def __init__(self):
		self.next_block = None
		self.block_number = 1
		self.distance = 0
		self.beacon_time = '1970-01-01 00:00:00'
		self.tree_root = ''
		self.tree_path = ''
		self.block_information = {
			'previous_block_hash' : '5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9',
			'transaction_list' : [],
			'coinbase_address' : 'CC592680DB3A8677852C406CE4735FDD1A32470AC1FE119D1E3E7B83B98FD60555A577C6E4C4FEF099629F92E0482F44BBCEC4914F5657FAE240D10981C4B547D9F3EF0A84540E614250A46E8E4DE6BC35A6E556E52AF87E2C2F836DA8C9DE9C38025DD8F9DCADC6930BAEEE1C32146169B32551076932ABBE9E09BBDCA519B9'
		}

	def add_next_block(self, block):
		block.next_block = None
		block.block_number = self.block_number+1
		target = block.get_target_value()
		proposed_value = tree.leafFromPath(block.tree_root, block.tree_path)
		distanceString = tree.binaryDistance(target, proposed_value)
		block.distance = self.distance
		self.next_block = block

	def hash(self):
		transaction_hash = ''
		for transaction in self.block_information['transaction_list']:
			transaction_hash = SHA.new(transaction.hash().hexdigest()+transaction_hash).hexdigest()
		return SHA.new(self.block_information['previous_block_hash']+transaction_hash+self.block_information['coinbase_address']).hexdigest()

	def get_target_value(self):
		try:
			response = urllib2.urlopen(BEACON+self.beacon_time+'.txt')
			response = response.read()
		except:
			response = ''
		return SHA.new(response+self.block_information['previous_block_hash']+self.hash()).hexdigest()[0:32]

	def verify(self, previous_block, balances, transaction_set):
		if previous_block == None:
			# Verify a genesis block
			return (self.__dict__ == Block().__dict__)
		else:
			balances = balances.clone()
			
			# Verify the block information
			block_verified = True
			if len(self.block_information['transaction_list']) == 0 or len(self.block_information['transaction_list']) > 100:
				block_verified = False
			if previous_block.hash() != self.block_information['previous_block_hash']:
				block_verified = False
			if self.string_to_unix_time(previous_block.beacon_time) >= self.string_to_unix_time(self.beacon_time):
				block_verified = False
			try:
				response = urllib2.urlopen(BEACON+self.beacon_time+'.txt')
				response.read()
			except:
				block_verified = False

			# Verify the transactions
			transactions_verified = True
			for transaction in self.block_information['transaction_list']:
				transactions_verified = transactions_verified and transaction.verify(balances, True) and (transaction.transaction_id not in transaction_set)
			return transactions_verified and block_verified

	def string_to_unix_time(self, s):
		return int(datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S').strftime("%s"))
