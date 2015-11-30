class Block:
	'A class representing the DriveCoin block specification'

	def __init__(self, filename=None):
		self.previous_blocks = None
		self.next_block = None
		self.block_information = {
			'previous_block_hash' : None,
			'block_number' : None,
			'transaction_list' : None,
			'coinbase_transaction' : None,
			'merkle_tree_root' : None,
			'merkle_tree_path' : None
		}


		if filename != None:
			self.read_from_file(filename)

	def read_from_file(self, filename):
		pass

	def write_to_file(self, file):
		pass


