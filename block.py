class Block:
	'A class representing the DriveCoin block specification'

	def __init__(self):
		self.previous_block = None
		self.next_block = None
		self.block_number = 1
		self.block_information = {
			'previous_block_hash' : '5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9',
			'transaction_list' : [],
			'coinbase_address' : '88AE74EF9CBAE03E4371E450C4F82A9D11FC6656199E4D30278520D26AC1719843A0E5B7264318BC4FF78BF10E4E0237DF720219EC3DFEC79E0B19824ABEBE9CB982991E5EE642EC10EE5D857E5156FB0FC2F48A8AF4DF67653736EEC8BED59661E68A62EB93F6D9FEABF7C384A6413D60C9C8B38C25A9324C6B31B3349AD8C1',
			'merkle_tree_root' : '',
			'merkle_tree_path' : ''
		}

	def add_next_block(self, block):
		block.next_block = None
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

