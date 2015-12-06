from Crypto.PublicKey import RSA
from network import DriveCoinNetwork
from network import DriveCoinClient
from blockchain import Blockchain
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
	except:
		print "ERROR: Failed to connect to DriveCoin seed peer"
		server.stop()

	blockchain = Blockchain()
	server.set_blockchain(blockchain)

	def menu(items, item_values):
		response = None
		possible_responses = {}
		menu_list = ''
		for index, item in enumerate(items):	
			possible_responses[str(index+1)] = item_values[index]
			menu_list += " \n\t"+str(index+1)+") "+item
		seperator = "\n========================================\n"
		while response not in possible_responses:
			if type(response) == str:
				print "Invalid Choice!"
			response = raw_input("\n"+seperator+"Select an option:"+menu_list+seperator)
		return possible_responses[response]

	def main_menu():
		choice =  menu(["Create Wallet", "Select Wallet", "Check Balance", "Send Money", "Exit App"],
						[create_wallet, select_wallet, check_balance, send_money, exit_app])
		choice()

	def create_wallet():
		key = RSA.generate(2048)
		key.key_data
		main_menu()

	def select_wallet():
		main_menu()

	def check_balance():
		main_menu()

	def send_money():
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