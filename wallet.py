from network import DriveCoinNetwork
from network import DriveCoinClient
import sys
import shelve

def interactive_wallet():
	store = shelve.open('wallet.store', flag='c', protocol=None, writeback=True)
	if len(store) == 0:
		store['wallets'] = []
		store['current_wallet'] = None
	server = DriveCoinNetwork.Instance()

	try: 
		client = DriveCoinClient.Instance()
	except None:
		print "ERROR: Failed to connect to DriveCoin seed peer"
		server.stop()
		return

	def menu():
		response = None
		possible_responses = {'1': create_wallet, '2': select_wallet, '3':check_balance, '4': send_money}
		seperator = "\n========================================\n"
		while response not in possible_responses:
			if type(response) == str:
				print "Invalid Choice!"
			response = raw_input("\n"+seperator+"Select an option: \n\t1) Create Wallet \n\t2) Select Wallet \n\t3) Check Balance \n\t4) Send Money"+seperator)
		return possible_responses[response]

	def create_wallet():
		pass

	def select_wallet():
		pass

	def check_balance():
		pass

	def send_money():
		pass

	menu()
	print client.peers


def main():
	server = DriveCoinNetwork.Instance()
	server.attach_routine(interactive_wallet)
	server.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()