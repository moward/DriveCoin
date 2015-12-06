class Block:
	'A class representing the DriveCoin block specification'

	def __init__(self):
		self.previous_block = None
		self.next_block = None
		self.block_number = 1
		self.block_information = {
			'previous_block_hash' : '5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9',
			'transaction_list' : [],
			'coinbase_address' : '',
			'merkle_tree_root' : '',
			'merkle_tree_path' : ''
		}

	def addNextBlock(self, block):
		self.next_block.previous_block = self
		self.next_block = block
		self.next_block.block_number = self.block_number+1


	def verify(self, balances):
		if self.previous_block == None:
			# Verify a genesis block
			return (self.__dict__ == Block().__dict__)
		else:
			balances = balances.clone()
			
			# Verify the block information

			# Verify the transactions
			transactions_verified = True
			for transaction in self.block_information['transaction_list']:
				transactions_verified = transactions_verified and transaction.verify(balances, True)
			return transactions_verified

