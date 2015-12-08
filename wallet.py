import sys
import shelve
import Utils
from Crypto.PublicKey import RSA
from network import DriveCoinNetwork
from network import DriveCoinClient
from blockchain import Blockchain
from transaction import Transaction

def interactive_wallet():
	store = shelve.open('wallet.store', flag='c', protocol=None, writeback=True)
	if len(store) == 0:
		store['wallets'] = []
		store['current_wallet'] = None
	server = DriveCoinNetwork.Instance()

	try: 
		client = DriveCoinClient.Instance()
	except:
		print "ERROR: Failed to connect to DriveCoin seed peer"
		server.stop()

	blockchain = Blockchain()
	server.set_blockchain(blockchain)

	def main_menu():
		choice =  Utils.menu(["Create Wallet", "Select Wallet", "Check Balance", "Send Money", "Exit App"],
						[create_wallet, select_wallet, check_balance, send_money, exit_app])
		choice()

	def create_wallet():
		key = RSA.generate(1024)
		store['wallets'] = store['wallets']+[(key.n, key.e, key.d, key.p, key.q)]
		store['current_wallet'] = store['wallets'][-1]
		print "Created! Your address is:"
		print Utils.encode_address(key.n)
		main_menu()

	def select_wallet():
		if len(store['wallets']) > 0:
			item_values = store['wallets']
			items = []
			for wallet in item_values:
				items.append(Utils.encode_address(wallet[0]))
			choice =  Utils.menu(items, item_values)
			store['current_wallet'] = choice
		else:
			print "You haven't created any wallets yet!"
		main_menu()

	def check_balance():
		if blockchain.verified and store['current_wallet'] != None:
			print "Your balance for:"
			print Utils.encode_address(store["current_wallet"][0])
			print "is:"
			balance = blockchain.get_balances().lookup_address(Utils.encode_address(store["current_wallet"][0]))
			print balance/(10.0**9)
		elif store['current_wallet'] == None:
			print "You must select a wallet!"
		else:
			print "Still verifying the blockchain is updated! Try again later!"
		main_menu()

	def send_money():
		if blockchain.verified and store['current_wallet'] != None:
			amount = "None"
			if not amount.replace(".","",1).isdigit():
				amount = raw_input("Enter an amount: ")
			sender = Utils.encode_address(store["current_wallet"][0])
			recipient = raw_input("Enter a destination address: ").strip()
			amount = int(float(amount.strip())*(10**9))
			transaction = Transaction(sender, recipient, amount)
			transaction.sign(store['current_wallet'])
			if transaction.verify(blockchain.get_balances()):
				client.telnet_broadcast('transaction', [transaction])
				print "Success, the money was sent! There will be a delay in confirmation until the transaction is added to the blockchain by a miner."
			else:
				print "Your balances are not enough to cover this transaction!"
		elif store['current_wallet'] == None:
			print "You must select a wallet!"
		else:
			print "Still verifying the blockchain is updated! Try again later!"

		main_menu()

	def exit_app():
		server.stop()

	main_menu()


def main():
	server = DriveCoinNetwork.Instance()
	server.attach_routine(interactive_wallet)
	server.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()