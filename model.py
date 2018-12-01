import math
import numpy as np

def logaddexp(a,b):
  return np.logaddexp(a,b)

nodes = []
class Node():
  def __init__(self, parent=None, symbols=2):
    global nodes
    self.c = [0]*symbols
    self.n = [None]*symbols
    self.symbols = symbols
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
    if self.n[prevx[-1]] is None:
      if create:
        self.n[prevx[-1]] = Node(self, self.symbols)
      else:
        return self
    return self.n[prevx[-1]].find(prevx[:-1], create)

  def update(self, x, reverse=False):
    peadj = math.log(self.c[x]+0.5) - math.log(sum(self.c)+1.0)
    if reverse == False:
      self.pe += peadj
      self.c[x] += 1
    else:
      self.c[x] -= 1
      self.pe -= peadj

    # propagate
    tpw = 0
    for nn in self.n:
      if nn is not None:
        tpw += nn.pw
    if tpw == 0:
      self.pw = self.pe
    else:
      self.pw = math.log(0.5) + logaddexp(self.pe, tpw)
    if self.parent is not None:
      self.parent.update(x, reverse)

class CTW(object):
  def __init__(self, context_length=8):
    global nodes
    nodes = []
    self.context_length = context_length
    self.root = Node(symbols=2)
    self.prevx = [0]*self.context_length

  @property
  def nodes(self):
    return nodes

  def log_prob(self, s):
    pn = self.root.find(self.prevx, True)
    prev = pn.pw
    pn.update(s)
    after_s = pn.pw
    pn.update(s, True)
    return after_s - prev

  def update(self, x):
    # increment tables
    tn = self.root.find(self.prevx, create=True)
    tn.update(x)

    self.prevx.append(x)
    self.prevx = self.prevx[-self.context_length:]



