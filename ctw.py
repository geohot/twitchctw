#!/usr/bin/env python3 
import sys
import math
import numpy as np

def logaddexp(a,b):
  return np.logaddexp(a,b)
  #return math.log(math.exp(a) + math.exp(b))

# P(x_i == 1 | x_0:i-1)

# enwik6: 1000000
#   gzip: 356711

# enwik4: 10000 -> 3728

def clip(x, mn, mx):
  if x < mn:
    x = mn
  if x > mx:
    x = mx
  return x

def bitgen(x):
  for c in x:
    for i in range(8):
      yield int((c & (0x80>>i)) != 0)

from collections import defaultdict

NUMBER_OF_BITS = 5+6

nodes = []
class Node():
  def __init__(self, parent=None):
    global nodes
    self.c = [0,0]
    self.n = None
    self.pe = self.pw = 0.0
    self.parent = parent
    if self.parent is not None:
      self.depth = self.parent.depth + 1
    else:
      self.depth = 0
    nodes.append(self)

  def __str__(self):
    return "[%d,%d]" % (self.c[0], self.c[1])

  def find(self, prevx, create=False):
    if prevx == []:
      return self
    if self.n is None:
      if create:
        self.n = [Node(self), Node(self)]
      else:
        return self
    return self.n[prevx[-1]].find(prevx[:-1], create)

  def update(self, x, reverse=False):
    if reverse == False:
      self.pe += math.log(self.c[x]+0.5) - math.log(self.c[0]+self.c[1]+1.0)
      self.c[x] += 1
    else:
      self.c[x] -= 1
      self.pe -= math.log(self.c[x]+0.5) - math.log(self.c[0]+self.c[1]+1.0)

    # propagate
    if self.n is not None:
      self.pw = math.log(0.5) + logaddexp(self.pe, self.n[0].pw + self.n[1].pw)
    else:
      self.pw = self.pe
    if self.parent is not None:
      self.parent.update(x, reverse)
    
from coder import Coder

def run(fn="enwik4", compress=True):
  global nodes

  if compress:
    enw = open(fn, "rb").read()
    bg = bitgen(enw)
    enc = Coder()
  else:
    enc = Coder(open(fn+".out", "rb").read())

  nodes = []
  root = Node()

  H = 0.0
  cnt = 0 
  stream = []
  try:
    prevx = [0]*NUMBER_OF_BITS
    while 1:
      cnt += 1

      #print(root.pw)
      pn = root.find(prevx)

      # what if a wild 0 appeared? this is wrong because creation might happen...
      prev = pn.pw

      pn.update(0)
      after_0 = pn.pw
      pn.update(0, True)
      p_0 = math.exp(after_0 - prev)

      """
      pn.update(1)
      after_1 = pn.pw
      pn.update(1, True)
      p_1 = math.exp(after_1 - prev)
      """

      if compress:
        x = next(bg)
        enc.code(p_0, x)
      else:
        x = enc.code(p_0)
      stream.append(x)

      p_x = p_0 if x == 0 else (1.0 - p_0)
      H += -math.log2(p_x)

      # increment tables
      tn = root.find(prevx, create=True)
      tn.update(x)

      prevx.append(x)
      prevx = prevx[-NUMBER_OF_BITS:]
      if cnt % 5000 == 0:
        ctw_bytes = (root.pw/math.log(2))/-8
        print("%5d: ratio %.2f%%, %d nodes, %.2f bytes, %.2f ctw" % (cnt//8, H*100.0/cnt, len(nodes), H/8.0, ctw_bytes))

      # TODO: make this generic
      if not compress and cnt == 80000:
        break
  except StopIteration:
    pass

  print("%.2f bytes of entropy, %d nodes, %d bits, %d bytes" % (H/8.0, len(nodes), len(stream), len(enc.ob)))

  if compress:
    with open(fn+".out", "wb") as f:
      f.write(bytes(enc.ob))
      f.write(bytes([enc.h>>24, 0, 0, 0]))
  else:
    ob = []
    for i in range(0, len(stream), 8):
      tb = stream[i:i+8]
      rr = 0
      for j in tb:
        rr <<= 1
        rr |= j
      ob.append(rr)
    with open(fn+".dec", "wb") as f:
      f.write(bytes(ob))

if __name__ == "__main__":
  if sys.argv[1] == "x":
    run(sys.argv[2], False)
  if sys.argv[1] == "c":
    run(sys.argv[2])

