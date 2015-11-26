# CIS 556 HW 3
# Fall 2015
# Matthew Howard
# Data handling utils

def toHex(input):
  return ''.join(['%0.2X' % ord(c) for c in input])

# xor two strings (trims the longer input)
def strxor(a, b):
  return "".join([chr(ord(x) ^ ord(y)) for (x, y) in zip(a, b)])

def intToStr(x, len):
  if len == 0:
    return ''
  else:
    return intToStr(x >> 8, len - 1) + chr(x & 0xff)