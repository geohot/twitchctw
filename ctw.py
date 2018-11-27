#!/usr/bin/env python3 
import math

# P(x_i == 1 | x_0:i-1)

# enwik6: 1000000
#   gzip: 356711

# enwik4: 10000 -> 3728

enw = open("enwik4", "rb").read()

def bitgen(x):
  for c in x:
    for i in range(8):
      yield int((c & (0x80>>i)) != 0)

from collections import defaultdict

NUMBER_OF_BITS = 16

nodes = []
class Node():
  def __init__(self):
    global nodes
    self.c = [0,0]
    self.n = [None, None]
    nodes.append(self)

  def __str__(self):
    return "[%d,%d]" % (self.c[0], self.c[1])
    
  def getp_recurse(self, x, p):
    np = (self.c[p] + 0.5) / (self.c[0] + self.c[1] + 1)
    if x != [] and self.n[x[-1]] is not None:
      ret = self.n[x[-1]].getp_recurse(x[:-1], p)
      return ret + [np]
    return [np]

  def getp(self, x, p):
    l = self.getp_recurse(x, p)
    ret = l[-1]
    for x in l[:-1][::-1]:
      ret = 0.5 * ret + 0.5*x
    return ret

  def add(self, x, p):
    self.c[p] += 1
    if x == []:
      return
    t = x[-1]
    if self.n[t] is None:
      self.n[t] = Node()
    self.n[t].add(x[:-1], p)

def quantize(x):
  x = int(x*256.0 + 0.5)
  if x == 0:  
    x = 1
  if x == 255:
    x = 254
  return x

class Encoder():
  def __init__(self, f):
    self.l = 0
    self.h = 256

  def code(self, p, x):
    print(p, x)

enc = Encoder(open("enwik4.out", "wb"))

root = Node()
bg = bitgen(enw)
H = 0.0
cnt = 0 
try:
  prevx = [0]*(NUMBER_OF_BITS+1)
  while 1:
    cnt += 1
    x = next(bg)

    # finite precision bro
    p_0 = root.getp(prevx, 0)
    p_x = p_0 if x == 0 else (1.0 - p_0)
    H += -math.log2(p_x)

    # increment tables
    root.add(prevx, x)
    prevx.append(x)
    prevx = prevx[-NUMBER_OF_BITS-1:]
    if cnt % 5000 == 0:
      print("ratio %.2f%%, %d nodes" % (H*100.0/cnt, len(nodes)))
except StopIteration:
  pass

print("%.2f bytes of entropy, %d nodes" % (H/8.0, len(nodes)))
#for n in nodes:
#  print(n)

exit(0)

lookup = defaultdict(lambda: [0,0])
bg = bitgen(enw)
H = 0.0
cnt = 0 
try:
  prevx = [0]*NUMBER_OF_BITS
  while 1:
    cnt += 1
    x = next(bg)

    # use tables
    px = tuple(prevx)

    # lookup[px] = P(x_i == 1 | x_i-5:i-1)
    # https://en.wikipedia.org/wiki/Krichevsky–Trofimov_estimator
    p_x = (lookup[px][x] + 0.5) / (lookup[px][0] + lookup[px][1] + 1)
    H += -math.log2(p_x)

    # encode
    #p_0 = (lookup[px][0] + 0.5) / (lookup[px][0] + lookup[px][1] + 1)
    #enc.code(quantize(p_0), x)

    # increment tables
    lookup[px][x] += 1
    prevx.append(x)
    prevx = prevx[-NUMBER_OF_BITS:]

except StopIteration:
  pass

#print(lookup)
print("%.2f bytes of entropy" % (H/8.0))


