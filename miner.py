import sys
import shelve
import Utils
import os
import threading
import time
import pickle
from Crypto.PublicKey import RSA
from network import DriveCoinNetwork
from network import DriveCoinClient
from block import Block
from blockchain import Blockchain
from transaction import Transaction
import tree
from tree import SolutionSet

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

	print "Waiting for blockchain to be verified..."
	while not blockchain.verified:
		pass

	if store["current_wallet"] == None:
		exit_app()
		return

	if not os.path.isfile('tree.txt'):
		print "Generating Proof-of-Space Tree... This may take some time, but it only needs to happen once"
		t = tree.generateFile('tree.txt', 100000000)
	else:
		t = SolutionSet('tree.txt')

	print "Mining on the currently selected wallet. You may exit at anytime."
	coinbase_address = Utils.encode_address(store["current_wallet"][0])
	print "Current coinbase address:"
	print coinbase_address
	server.set_coinbase_address(coinbase_address)

	def mine():
		new_block = Block()
		interval = 10 * 60 # Add a new value every 10 minutes
		latestValue = int(time.time() / interval) * interval
		new_block.beacon_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(latestValue))
		transaction_list = []
		pending_transactions = blockchain.store['pending_transactions']
		pending_transactions_list = list(pending_transactions)
		for transaction in pending_transactions_list:
			if transaction.transaction_id not in blockchain.transaction_set and transaction.verify(blockchain.balances):
				if len(transaction_list) < 100:
					transaction_list.append(transaction)
			else:
				pending_transactions.remove(transaction)
		new_block.block_information = {
			'previous_block_hash' : blockchain.get_last_block().hash(),
			'transaction_list' : transaction_list,
			'coinbase_address' : coinbase_address
		}
		result = t.lookup(new_block.get_target_value())
		new_block.tree_root = result[1]
		new_block.tree_path = result[2]
		old_blockchain_head = pickle.loads(pickle.dumps(blockchain.store["head_block"]))
		previous_block = blockchain.get_last_block()
		blockchain.add_block(new_block)
		if not blockchain.get_last_block().verify(previous_block, blockchain.balances, blockchain.transaction_set):
			print "Rejected..."
			blockchain.store["head_block"] = old_blockchain_head
		else:
			print "Added block to local block chain! Proposing solution to the network..."
			blockchain.calculate_balances()

		threading.Timer(10, mine).start()


	def main_menu():
		choice =  Utils.menu(["Exit App"],
						[exit_app])
		choice()

	def exit_app():
		server.stop()

	mine()
	main_menu()


def main():
	server = DriveCoinNetwork.Instance()
	server.attach_routine(interactive_miner)
	server.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()