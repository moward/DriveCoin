class Block:
	'A class representing the DriveCoin block specification'

	def __init__(self):
		self.previous_block = None
		self.next_block = None
		self.block_number = 1
		self.block_information = {
			'previous_block_hash' : '5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9',
			'transaction_list' : [],
			'coinbase_transaction' : '',
			'merkle_tree_root' : '',
			'merkle_tree_path' : ''
		}

	def addNextBlock(self, block):
		self.next_block.previous_block = self
		self.next_block = block
		self.next_block.block_number = self.block_number+1


	def verify(self):
		# TODO verify a valid gensis or chained block
		if self.previous_block == None:
			# verify it is the genesis block
			pass
		else:
			# verify the block
			pass
		return True

