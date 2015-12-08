from twisted.internet import reactor, protocol
from twisted.internet.defer import DebugInfo
import telnetlib
import random
from singleton import Singleton
import os
import sys
import signal
from blockchain import Blockchain
import time
import pickle

SEED_PEER = '127.0.0.1'
DRIVECOIN_PORT = 8123

global_blockchain = None
global_mining = False
global_coinbase_address = ''

class DriveCoinServerProtocol(protocol.Protocol):
	'Manages DriveCoin incoming requests from peers'

	peers = set()

	def connectionMade(self):
		self.peers.add(self.transport.getPeer().host)

	def dataReceived(self, data):
		# Strip new lines
		data=data.strip()
		split_data = data.split('::')
		func = split_data[0]
		if len(split_data) > 1:
			values = pickle.loads(split_data[1].decode('hex'))
		else:
			values = []
		getattr(self, 'do_'+func, self.do_nop)(*values)

	def do_nop(self):
		pass

	def do_peers(self):
		for peer in self.peers:
			self.transport.write(peer+'\n')
		self.transport.write('end-peers')

	def do_num_blocks(self):
		self.transport.write(str(global_blockchain.get_last_block().block_number)+'\n')
		self.transport.write('end-num_blocks')

	def do_head_block(self):
		self.transport.write(pickle.dumps(global_blockchain.get_head_block())+'\n')
		self.transport.write('end-head_block')

	def do_transaction(self, transaction):
		if transaction.transaction_id not in global_blockchain.transaction_set:
			pending_transactions = global_blockchain.store['pending_transactions']
			if transaction.verify(global_blockchain.balances):
				pending_transactions.add(transaction)
			global_blockchain.store['pending_transactions'] = pending_transactions
		self.transport.write('end-transaction')


@Singleton
class DriveCoinClient():
	'Broadcasts outgoing requests to peers'

	SEED_PEER = '127.0.0.1'

	def __init__(self):
		# Bootstrap peers from a seed peer
		self.tn = telnetlib.Telnet(self.SEED_PEER, DRIVECOIN_PORT)
		peer_ips =  self.parse_telnet_response(self.telnet_seed_command('peers'))
		self.peers = list(set(peer_ips))

	def telnet_read_until(self, msg):
		if (msg[-len(msg):] !=  msg):
			raise IOError
		return self.tn.read_until(msg)[:-len(msg)]

	def telnet_seed_command(self, command):
		self.tn.close()
		self.tn = telnetlib.Telnet(self.SEED_PEER, DRIVECOIN_PORT)
		self.tn.write(command+"\n")
		return self.telnet_read_until('end-'+command)

	def telnet_peers_command(self, command, get_random_peer=True):
		error = True
		for i in range(30):
			try:
				error = False
				if get_random_peer:
					random_peer = random.choice(self.peers)
					self.tn.close()
					self.tn = telnetlib.Telnet(random_peer, DRIVECOIN_PORT)
				self.tn.write(command+"\n")
				break
			except:
				error = True
		if error:
			raise RuntimeError
		split_data = command.split('::')
		func = split_data[0]
		return self.telnet_read_until('end-'+func)

	def telnet_broadcast(self, msg, args):
		for peer in self.peers:
			self.tn.close()
			self.tn = telnetlib.Telnet(peer, DRIVECOIN_PORT)
			self.telnet_peers_command(msg+'::'+pickle.dumps(args).encode('hex'), False)


	def parse_telnet_response(self,response):
		return map(lambda x: x.strip(), response.split('\n'))

@Singleton
class DriveCoinNetwork:
	'Runs a server on TCP port 8123 implementing the DriveCoinServerProtocol'

	def __init__(self):
		factory = protocol.ServerFactory()
		factory.protocol = DriveCoinServerProtocol
		reactor.listenTCP(DRIVECOIN_PORT,factory)

	def attach_routine(self, routine):
		reactor.callInThread(routine)

	def run(self):
		reactor.run()

	def stop(self):
		reactor.stop()
		os.kill(os.getpid(), signal.SIGKILL)

	def set_blockchain(self, blockchain):
		global global_blockchain
		global_blockchain = blockchain

	def set_mining(self, mining):
		global global_mining
		global_mining = True
	
	def set_coinbase_address(self, coinbase_address):
		global global_coinbase_address
		global_coinbase_address = coinbase_address

