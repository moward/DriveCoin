import sys
import shelve
import Utils
from Crypto.PublicKey import RSA
from network import DriveCoinNetwork
from network import DriveCoinClient
from blockchain import Blockchain
from transaction import Transaction

def interactive_miner():
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
	server.set_mining(True)

	if store["current_wallet"] == None:
		exit_app()
		return

	print "Mining on the currently selected wallet. You may exit at anytime."
	coinbase_address = Utils.encode_address(store["current_wallet"][0])
	print "Current coinbase address:"
	print coinbase_address
	server.set_coinbase_address(coinbase_address)

	def main_menu():
		choice =  Utils.menu(["Exit App"],
						[exit_app])
		choice()

	def exit_app():
		server.stop()

	main_menu()


def main():
	server = DriveCoinNetwork.Instance()
	server.attach_routine(interactive_miner)
	server.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()