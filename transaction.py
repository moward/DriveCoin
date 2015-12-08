from Crypto.Random.random import getrandbits
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
import Utils

class Transaction:
	'A class representing a transaction'

	def __init__(self, sender, recipient, amount):
		self.transaction_id = hex(getrandbits(2048))
		self.sender = sender
		self.recipient = recipient
		self.amount = amount
		self.signature = None

	def sign(self, wallet):
		self.signature = self.generate_key(wallet).sign(self.hash())

	def generate_key(self, wallet):
		key = RSA.construct(wallet)
		return PKCS1_v1_5.new(key)

	def hash(self):
		return SHA.new(str(self.transaction_id)+","+str(self.sender)+","+str(self.recipient)+","+str(self.amount))

	def __hash__(self):
		return Utils.string_to_long(self.hash().hexdigest())

	def __eq__(self, other):
		return self.__hash__() == other.__hash__()

	def verify(self, balances, mutate_balances = False):
		signature_check = self.generate_key(Utils.decode_address(self.sender)).verify(self.hash(), self.signature)
		balance_check = balances.lookup_address(self.sender) >= self.amount
		if signature_check and balance_check and mutate_balances:
			balances.add_to_address(self.sender, -1*self.amount)
			balances.add_to_address(self.recipient, self.amount)
		return (signature_check and balance_check)