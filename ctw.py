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


class Coder():
  def __init__(self, ob=[]):
    self.l = 0
    self.h = 0xffffffff
    self.ob = ob

  def decode(self, p_0):
    assert self.l <= self.h
    assert self.l >= 0 and self.l < 0x100000000
    assert self.h >= 0 and self.h < 0x100000000

    p_0 = int(254*p_0 + 1)
    split = self.l + (((self.h - self.l)*p_0) >> 8)

    if len(self.ob) < 4:
      raise StopIteration

    x = (self.ob[0]<<24) | (self.ob[1]<<16) | (self.ob[2]<<8) | self.ob[3]

    if x <= split:
      ret = 0
      self.h = split
    else:
      ret = 1
      self.l = split + 1

    while self.l>>24 == self.h>>24:
      self.ob = self.ob[1:]
      self.l = ((self.l & 0xFFFFFF) << 8)
      self.h = ((self.h & 0xFFFFFF) << 8) | 0xFF

    return ret

  def code(self, p_0, x):
    assert self.l <= self.h
    assert self.l >= 0 and self.l < 0x100000000
    assert self.h >= 0 and self.h < 0x100000000

    # key insight, the precision doesn't have to be perfect
    # just the sqme on encode and decode
    p_0 = int(254*p_0 + 1)
    split = self.l + (((self.h - self.l)*p_0) >> 8)

    if x == 0:
      self.h = split
    else:
      self.l = split + 1

    while self.l>>24 == self.h>>24:
      b = self.l>>24
      assert b>=0 and b<256
      self.ob.append(b)
      self.l = ((self.l & 0xFFFFFF) << 8)
      self.h = ((self.h & 0xFFFFFF) << 8) | 0xFF

def run(compress=True):
  global nodes

  if compress:
    enc = Coder()
  else:
    dec = Coder(open("enwik4.out", "rb").read())

  nodes = []
  root = Node()
  bg = bitgen(enw)
  H = 0.0
  cnt = 0 
  stream = []
  try:
    prevx = [0]*(NUMBER_OF_BITS+1)
    while 1:
      cnt += 1

      # finite precision bro
      p_0 = root.getp(prevx, 0)

      if compress:
        x = next(bg)
        enc.code(p_0, x)
      else:
        x = dec.decode(p_0)
      stream.append(x)

      p_x = p_0 if x == 0 else (1.0 - p_0)
      H += -math.log2(p_x)

      # increment tables
      root.add(prevx, x)
      prevx.append(x)
      prevx = prevx[-NUMBER_OF_BITS-1:]
      if cnt % 5000 == 0:
        print("ratio %.2f%%, %d nodes, %f bytes" % (H*100.0/cnt, len(nodes), H/8.0))
  except StopIteration:
    pass

  print("%.2f bytes of entropy, %d nodes, %d bits" % (H/8.0, len(nodes), len(stream)))

  if compress:
    with open("enwik4.out", "wb") as f:
      f.write(bytes(enc.ob))
  else:
    ob = []
    for i in range(0, len(stream), 8):
      tb = stream[i:i+8]
      rr = 0
      for j in tb:
        rr <<= 1
        rr |= j
      ob.append(rr)
    with open("enwik4.dec", "wb") as f:
      f.write(bytes(ob))

run()
run(False)

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


