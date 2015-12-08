'''
A simple beacon which generates a random 256-bit random value every 10 minutes
And serves them via a web server
'''

import SimpleHTTPServer
import SocketServer
import time
from Utils import *

interval = 10 * 60 # Add a new value every 10 minutes
startTime = int(time.time() / interval) * interval

latestValue = startTime - interval

# Adds all values at 10 minute intervals up to current time
def add_values():
  global latestValue
  currTime = int(time.time() / interval) * interval
  while latestValue < currTime:
    latestValue += interval 
    filename = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(latestValue)) + '.txt'
    with open('beacon_files/' + filename, 'w+') as f:
      f.write(''.join(['%02x' % ord(c) for c in randomString(32)]))


class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
  def do_GET(self):
      add_values()
      self.path = '/beacon_files' + self.path
      return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

if __name__ == "__main__":

  Handler = MyRequestHandler
  server = SocketServer.TCPServer(('0.0.0.0', 8080), Handler)

  server.serve_forever()
