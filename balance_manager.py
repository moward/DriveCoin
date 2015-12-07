import copy

class BalanceManager:
	'A class representing a balance lookup'

	def __init__(self):
		self.balances = {}

	def add_to_address(self, address, value):
		if address in self.balances:
			self.balances[address] = self.balances[address] + value
		else: 
			self.balances[address] = value

	def lookup_address(self, address):
		if address in self.balances:
			return self.balances[address]
		else:
			return 0

	def clone(self):
		bm = BalanceManager()
		bm.balances = copy.deepcopy(self.balances)
		return bm
