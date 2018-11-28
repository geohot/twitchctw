#!/usr/bin/env python3 
import sys
import math

# P(x_i == 1 | x_0:i-1)

# enwik6: 1000000
#   gzip: 356711

# enwik4: 10000 -> 3728


def bitgen(x):
  for c in x:
    for i in range(8):
      yield int((c & (0x80>>i)) != 0)

from collections import defaultdict

NUMBER_OF_BITS = 8

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

from coder import Coder

def run(fn="enwik4", compress=True):
  global nodes

  if compress:
    enw = open(fn, "rb").read()
    bg = bitgen(enw)
    enc = Coder()
  else:
    dec = Coder(open(fn+".out", "rb").read())

  nodes = []
  root = Node()
  H = 0.0
  cnt = 0 
  stream = []
  try:
    prevx = [0]*(NUMBER_OF_BITS+1)
    while 1:
      cnt += 1

      p_0 = root.getp(prevx, 0)

      if compress:
        x = next(bg)
        enc.code(p_0, x)
      else:
        x = dec.code(p_0)
      stream.append(x)

      p_x = p_0 if x == 0 else (1.0 - p_0)
      H += -math.log2(p_x)

      # increment tables
      root.add(prevx, x)
      prevx.append(x)
      prevx = prevx[-NUMBER_OF_BITS-1:]
      if cnt % 5000 == 0:
        print("ratio %.2f%%, %d nodes, %f bytes" % (H*100.0/cnt, len(nodes), H/8.0))

      # TODO: make this generic
      if not compress and cnt == 80000:
        break
  except StopIteration:
    pass

  print("%.2f bytes of entropy, %d nodes, %d bits" % (H/8.0, len(nodes), len(stream)))

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

