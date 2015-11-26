import mmap
from Crypto.Random import random
from Crypto.Hash.SHA256 import SHA256Hash
from Utils import *

N = 8
MAGIC_VALUE = '\x99' * 32

hash = SHA256Hash()

class SolutionSet:
  'Store and lookup PoS solutions in a file'

  def __init__(self, filename):
    # open file handler
    self.file = open(filename, "rw")
  def add(self, value, root, path):
    print 'Adding value %s from root %s with path %s' % (toHex(value), toHex(root), toHex(path))


def randomString(n):
  return ''.join([chr(random.randint(0, 255)) for _ in range(0, n)])

# Generate our Merkle tree
def generateTree(solnSet):
  bottomRow = []

  # Recurse down tree to efficiently find Merkle leaves
  def descend(nodeValue, depth):
    if depth == N:
      bottomRow.append(nodeValue)
    else:
      # Left subtree
      descend(hash.new(nodeValue).digest(), depth + 1)
      # Right subtree
      descend(hash.new(strxor(nodeValue, MAGIC_VALUE)).digest(), depth + 1)

  root = randomString(32)
  descend(root, 0)

  # Add hashes to SolutionSet
  for i in range(0, len(bottomRow)):
    solnSet.add(bottomRow[i], root, intToStr(i, 2))