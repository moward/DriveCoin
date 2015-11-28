class Block:
	'A class representing the DriveCoin block specification'

	def __init__(self, filename=None):
		self.previousBlockHash = None
		if filename != None:
			self.readFromFile(filename)

	def readFromFile(self, filename):
		pass

	def writeToFile(self, file):
		pass


