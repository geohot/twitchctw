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

def setgen(x, l):
  bg = bitgen(x)
  ret = []
  while 1:
    ret.append(next(bg))
    ret = ret[-l:]
    if len(ret) == l:
      yield ret


from collections import defaultdict

NUMBER_OF_BITS = 4

# https://en.wikipedia.org/wiki/Krichevsky–Trofimov_estimator
lookup = defaultdict(lambda: [0.5,1.0])

sg = setgen(enw, NUMBER_OF_BITS)

#bg = bitgen(enw)

# 10101
# 010101
# 110101

ncount = 0

class Node():
  def __init__(self):
    global ncount
    self.c = [0,0]
    self.n = [None, None]
    ncount += 1

  def getp1(self, x):
    if self.n[0] is not None and self.n[1] is not None:
      return self.n[x[-1]].getp1(x[:-1])
    return (self.c[1] + 0.5) / (self.c[0] + self.c[1] + 1)

  def add(self, x):
    t = x[-1]
    self.c[t] += 1
    if x[:-1] == []:
      return
    if self.n[t] is None:
      self.n[t] = Node()
    self.n[t].add(x[:-1])

root = Node()

H = 0.0
cnt = 0
try:
  while 1:
    cnt += 1
    x = next(sg)
    p_1 = root.getp1(x)
    p_x = p_1 if x[-1] == 1 else 1.0 - p_1
    H += -math.log2(p_x)
    if cnt%3000 == 0:
      print("%.2f%% packed, %d nodes" % ((H*100.0)/cnt, ncount))
    root.add(x)
except StopIteration:
  pass

print("%.2f bytes of entropy" % (H/8.0))

exit(0)

HH = 0.0
try:
  prevx = [-1]*NUMBER_OF_BITS
  while 1:
    x = next(bg)

    # use tables
    px = tuple(prevx)

    # lookup[px] = P(x_i == 1 | x_i-5:i-1)
    p_1 = lookup[px][0] / lookup[px][1]
    p_x = p_1 if x == 1 else 1.0 - p_1

    #H = -(p_0*math.log2(p_0) + p_1*math.log2(p_1))

    H += -math.log2(p_x)

    # increment tables
    lookup[px][0] += x == 1
    lookup[px][1] += 1
    prevx.append(x)
    prevx = prevx[-NUMBER_OF_BITS:]

except StopIteration:
  pass


