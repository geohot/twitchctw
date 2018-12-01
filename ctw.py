#!/usr/bin/env python3 
import sys
import math

def bitgen(x):
  for c in x:
    for i in range(8):
      yield int((c & (0x80>>i)) != 0)

def bytegen(x):
  for c in x:
    yield c

from model import CTW
from coder import Coder

def run(fn="enwik4", compress=True):
  if compress:
    enw = open(fn, "rb").read()
    bg = bitgen(enw)
    #bg = bytegen(enw)
    enc = Coder()
  else:
    enc = Coder(open(fn+".out", "rb").read())

  ctw = CTW()
  H = 0.0
  cnt = 0 
  stream = []
  try:
    while 1:
      cnt += 1

      # what if a wild 0 appeared? this is wrong because creation might happen...
      p_0 = ctw.log_prob(0)

      if compress:
        x = next(bg)
        enc.code(p_0, x)
      else:
        x = enc.code(p_0)

      stream.append(x)

      p_x = p_0 if x == 0 else (1.0 - p_0)
      H += -math.log2(p_x)

      ctw.update(x)

      if cnt % 5000 == 0:
        ctw_bytes = (ctw.root.pw/math.log(2))/-8
        print("%5d: ratio %.2f%%, %d nodes, %.2f bytes, %.2f ctw" % (cnt//8, H*100.0/cnt, len(ctw.nodes), H/8.0, ctw_bytes))

      # TODO: make this generic
      if not compress and cnt == 80000:
        break
  except StopIteration:
    pass

  print("%.2f bytes of entropy, %d nodes, %d bits, %d bytes" % (H/8.0, len(ctw.nodes), len(stream), len(enc.ob)))

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

