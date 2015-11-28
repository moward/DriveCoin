from twisted.internet import reactor, protocol
from twisted.internet.defer import DebugInfo
import telnetlib
import random
from singleton import Singleton
import os
import sys
import signal

SEED_PEER = '127.0.0.1'
DRIVECOIN_PORT = 8123

class DriveCoinServerProtocol(protocol.Protocol):
	'Manages DriveCoin incoming requests from peers'

	peers = set()

	def connectionMade(self):
		self.peers.add(self.transport.getPeer().host)

	def dataReceived(self, data):
		# Strip new lines
		data=data.strip()
		getattr(self, 'do_'+data, 'do_nop')()

	def do_nop(self):
		pass

	def do_peers(self):
		for peer in self.peers:
			self.transport.write(peer+'\n')
		self.transport.write('end-peers')

@Singleton
class DriveCoinClient():
	'Broadcasts outgoing requests to peers'

	SEED_PEER = '127.0.0.1'

	def __init__(self):
		# Bootstrap peers from a seed peer
		self.tn = telnetlib.Telnet(self.SEED_PEER, DRIVECOIN_PORT)
		peer_ips =  self._parse_telnet_array_response(self.telnet_seed_command('peers').split())
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

	def telnet_peers_command(command):
		error = True
		for i in range(30):
			try:
				error = False
				random_peer = random.choice(self.peers)
				self.tn.close()
				self.tn = telnetlib.Telnet(random_peer, DRIVECOIN_PORT)
				self.tn.write(command+"\n")
				break
			except:
				error = True
		if error:
			raise RuntimeError
		return self.telnet_read_until('end-'+command)

	def _parse_telnet_array_response(self,response):
		return map(lambda x: x.strip(), response)

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