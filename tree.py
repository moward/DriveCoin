import mmap
import struct
from Crypto.Hash.SHA256 import SHA256Hash
from Utils import *

# Height of Merkle Tree
N = 16

# This value is xored with a hash node's value to generate the generate
# the hash input for its left child
MAGIC_VALUE = '\x99' * 32

# This class is used for hashing throughout
hash = SHA256Hash()

# From a root value and a binary path down the tree, give the leaf value
# Can be used for verification
def leafFromPath(root, intPath):
  nodeValue = root
  for i in reversed(range(0, N)):
    if (intPath >> i) & 1:
      nodeValue = hash.new(strxor(nodeValue, MAGIC_VALUE)).digest()
    else:
      nodeValue = hash.new(nodeValue).digest()
  return nodeValue

class BSTNode:
  'Represents a node (solution) in a solution set'

  '''
  Representation on disk:
  Index | Description             | Byte Length
  ----------------------------------------------
  0     | Node Value              | 32 B
  1     | Hash Tree Root          | 32 B
  2     | Binary Merkle Path      | 2 B
  3     | L Child Location        | 8 B
  4     | R Child Location        | 8 B
  '''
  nodeStruct = struct.Struct('>32s32sHll')
  byteSize = nodeStruct.size

  def __init__(self, solnSet, location):
    self.solnSet = solnSet
    self.location = location

  def read(self):
    self.values = list(self.nodeStruct.unpack(
      self.solnSet.read(self.location, self.byteSize)))

  def write(self):
    if not hasattr(self, 'values'):
      raise ValueError('BSTNode not assigned values')
    self.solnSet.write(self.location, self.nodeStruct.pack(*self.values))

  def getValue(self):
    if not hasattr(self, 'values'):
      self.read()
    return self.values[0]

  def getLeftChild(self):
    if not hasattr(self, 'values'):
      self.read()
    childLocation = self.values[3]
    if childLocation == 0:
      return None
    else:
      return BSTNode(self.solnSet, childLocation)

  def getRightChild(self):
    if not hasattr(self, 'values'):
      self.read()
    childLocation = self.values[4]
    if childLocation == 0:
      return None
    else:
      return BSTNode(self.solnSet, childLocation)

class SolutionSet:
  'Store and lookup PoS solutions in a file'

  treeSize = (2 ** N) * BSTNode.byteSize

  def __init__(self, filename):
    # open file handler
    self.f = open(filename, 'rb+')
    self.mm = mmap.mmap(self.f.fileno(), 0, prot = mmap.PROT_READ | mmap.PROT_WRITE)

  def nodeIndexToLocation(self, index):
    return 8 + index * BSTNode.byteSize

  def getRoot(self):
    return BSTNode(self, 8)

  def getNodeCount(self):
    return struct.unpack('l', self.mm[:8])[0]

  def setNodeCount(self, count):
    self.mm[:8] = struct.pack('l', count)

  def _insert(self, newNode):
    curr = self.getRoot()
    while curr.getValue() != newNode.getValue():
      if curr.getValue() < newNode.getValue():
        # insert into right
        next = curr.getRightChild()
        if next == None:
          curr.values[4] = newNode.location
          curr.write()
          break
        else:
          curr = next
      elif curr.getValue() > newNode.getValue():
        # insert into left
        next = curr.getLeftChild()
        if next == None:
          curr.values[3] = newNode.location
          curr.write()
          break
        else:
          curr = next
      else:
        raise ValueError('Node value already exists')

  '''
  Looks up in the binary tree to find a node closest to the target
  Returns the closest Node's
    0. Value (binary string)
    1. Merkle Tree Root (binary string)
    2. Binary Merkle Path (number)
    3. Distance to the target (binary string)
  in a list.
  '''
  def lookup(self, target):
    curr = lastLeftParent = lastRightParent = self.getRoot()
    while True:
      if curr.getValue() == target:
        # copy list and add distance
        return curr.values[0:3] + (['\x00'] * 32)
      elif curr.getValue() < target:
        # descend right
        next = curr.getRightChild()
        if next == None:
          # reached leaf
          parentDistance = binaryDistance(target, curr.getValue())
          lastRightParentDistance = binaryDistance(target, lastRightParent.getValue())
          if parentDistance < lastRightParentDistance:
            return curr.values[0:3] + [parentDistance]
          else:
            return lastRightParent.values[0:3] + [lastRightParentDistance]
        else:
          lastLeftParent = curr
          curr = next
      else:
        # descend left
        next = curr.getLeftChild()
        if next == None:
          # reached leaf
          parentDistance = binaryDistance(target, curr.getValue())
          lastLeftParentDistance = binaryDistance(target, lastLeftParent.getValue())
          if parentDistance < lastLeftParentDistance:
            return curr.values[0:3] + [parentDistance]
          else:
            return lastLeftParent.values[0:3] + [lastLeftParentDistance]
        else:
          lastRightParent = curr
          curr = next

  def _addTree(self, root, bottomRow):
    assert len(bottomRow) == 2 ** N
    currCount = self.getNodeCount()
    newSize = self.nodeIndexToLocation(currCount + 2 ** N)
    if newSize > self.mm.size():
      # resize if needed
      raise ValueError('Not enough space to add tree')

    i = 0 # Index used to calculate binary path
    for val in bottomRow:
      newNode = BSTNode(self, self.nodeIndexToLocation(currCount))
      newNode.values = [val, root, i, 0, 0]
      newNode.write()
      self._insert(newNode)
      currCount += 1
      i += 1

    self.setNodeCount(currCount)

  def write(self, location, s):
    self.mm[location : location + len(s)] = s

  def read(self, location, length):
    return self.mm[location: location + length]

  def close(self):
    self.mm.flush()
    self.mm.close()
    self.f.close()

  def fillFile(self):
    freeSpace = self.mm.size() - self.nodeIndexToLocation(self.getNodeCount())
    newTrees = freeSpace / self.treeSize
    for i in range(0, newTrees):
      self._addTree(*self.generateTree())
      print('Added %d trees' % (i + 1))
    
    print('Done: Added %d trees' % newTrees)

  # Generate our Merkle tree
  def generateTree(self):
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

    return (root, bottomRow)

def generateFile(filename, size):
  with open(filename, 'wb+') as f:
    f.seek(size - 1)
    f.write('\x00')
  solnSet = SolutionSet(filename)
  solnSet.fillFile()
  return solnSet

'''
Takes in two 32-Byte binary strings and returns the numeric difference
'''
def binaryDistance(x, y):
  assert len(x) == 32
  assert len(y) == 32

  # guarantee x is larger than or equal to y
  if x < y:
    temp = x
    x = y
    y = temp

  xs = map(ord, list(x))
  ys = map(ord, list(y))
  out = [0] * 32
  borrows = [0] * 32
  for i in reversed(range(0,32)):
    colDiff = xs[i] - borrows[i] - ys[i]
    if colDiff < 0:
      # need to borrow
      assert i != 0 # should be true from x < y check above
      borrows[i - 1] = 1
      out[i] = colDiff + 256
    else:
      out[i] = colDiff

  # output binary-string distance
  return ''.join(map(chr, out))
