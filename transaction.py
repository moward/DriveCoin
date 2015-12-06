from Crypto.Random.random import getrandbits

class Transaction:
	'A class representing a transaction'

	def __init__(self, sender, recipient, reference_transactions):
		self.transaction_id = hex(getrandbits(2048))
		self.sender = sender
		self.recipient = recipient
		self.reference_transactions = reference_transactions

	def verify(self):
		#TODO verify the transaction as being a valid RSA signature, and the balance being available
		pass