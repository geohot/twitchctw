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

NUMBER_OF_BITS = 24

nodes = []
class Node():
  def __init__(self):
    global nodes
    self.c = [0,0]
    self.n = [None, None]
    nodes.append(self)

  def __str__(self):
    return "[%d,%d]" % (self.c[0], self.c[1])
    
  def getp(self, x):
    np = (self.c[x[-1]] + 0.5) / (self.c[0] + self.c[1] + 1)
    if self.n[x[-1]] is not None:
      return self.n[x[-1]].getp(x[:-1])
      #return 0.5 * np + 0.5 * self.n[x[-1]].getp(x[:-1])
    return np

  def add(self, x):
    t = x[-1]
    self.c[t] += 1
    if x[:-1] == []:
      # if there's no more string, don't make more nodes
      return
    if self.n[t] is None:
      self.n[t] = Node()
    self.n[t].add(x[:-1])

root = Node()
bg = bitgen(enw)
H = 0.0
cnt = 0 
try:
  prevx = [0]*(NUMBER_OF_BITS+1)
  while 1:
    cnt += 1
    x = next(bg)

    p_x = root.getp(prevx)
    H += -math.log2(p_x)

    # increment tables
    prevx.append(x)
    prevx = prevx[-NUMBER_OF_BITS-1:]
    root.add(prevx)
    if cnt % 5000 == 0:
      print("ratio %.2f%%, %d nodes" % (H*100.0/cnt, len(nodes)))

except StopIteration:
  pass

print("%.2f bytes of entropy, %d nodes" % (H/8.0, len(nodes)))
#for n in nodes:
#  print(n)

#exit(0)

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

    # increment tables
    lookup[px][x] += 1
    prevx.append(x)
    prevx = prevx[-NUMBER_OF_BITS:]

except StopIteration:
  pass

#print(lookup)
print("%.2f bytes of entropy" % (H/8.0))


