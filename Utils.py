# CIS 556 HW 3
# Fall 2015
# Matthew Howard
# Data handling utils

from Crypto.Random import random

def toHex(input):
  return ''.join(['%0.2X' % ord(c) for c in input])

# xor two strings (trims the longer input)
def strxor(a, b):
  return ''.join([chr(ord(x) ^ ord(y)) for (x, y) in zip(a, b)])

# inefficient but only used on small integer types in practice (<8 Bytes)
def intToStr(x, len):
  if len == 0:
    return ''
  else:
    return intToStr(x >> 8, len - 1) + chr(x & 0xff)

def strToInt(s):
  if len(s) == 0:
    return 0
  else:
    return ord(s[-1]) + 256 * strToInt(s[:-1])

def string_to_long(s):
	return int(s.encode('hex'), 16)

def long_to_string(l):
	return hex(l)[2:].decode('hex')

# Our "MPI" format consists of 4-byte integer length l followed by l bytes of binary key
def int_to_mpi(z):
    s = int_to_binary(z)
    return struct.pack('<I',len(s))+s

# Horrible hack to get binary representation of arbitrary-length long int
def int_to_binary(z):
    s = ("%x"%z); s = (('0'*(len(s)%2))+s).decode('hex')
    return s

# Read one MPI-formatted value beginning at s[index]
# Returns value and index + bytes read.
def parse_mpi(s,index):
    length = struct.unpack('<I',s[index:index+4])[0]
    z = Integer(s[index+4:index+4+length].encode('hex'),16)
    return z, index+4+length

def randomString(n):
  return ''.join([chr(random.randint(0, 255)) for _ in range(0, n)])
