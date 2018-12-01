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

from coder import Coder

CTS = False

def run(fn="enwik4", compress=True):
  if compress:
    enw = open(fn, "rb").read()
    if CTS:
      bg, SYMBOLS = bytegen(enw), 256
    else:
      bg, SYMBOLS = bitgen(enw), 2
    enc = Coder()
  else:
    enc = Coder(open(fn+".out", "rb").read())

  if CTS:
    from cts import model
    ctw = model.ContextualSequenceModel(context_length=8)
  else:
    from model import CTW
    ctw = CTW()

  H = 0.0
  cnt = 0 
  stream = []
  try:
    while 1:
      cnt += 1

      # what if a wild 0 appeared? this is wrong because creation might happen...
      p_s = []
      for s in range(SYMBOLS):
        p_s.append(math.exp(ctw.log_prob(s)))
      assert (sum(p_s)-1.0) < 1e-6

      if compress:
        x = next(bg)
        enc.code(p_s[0], x)
      else:
        x = enc.code(p_s[0])

      stream.append(x)
      H += -math.log2(p_s[x])
      ctw.update(x)

      if cnt % (5000//math.log2(SYMBOLS)) == 0:
        if CTS:
          print("%5d: ratio %.2f%%, %.2f bytes" % (cnt, H*100.0/(cnt*math.log2(SYMBOLS)), H/8.0))
        else:
          print("%5d: ratio %.2f%%, %d nodes, %.2f bytes, %.2f ctw" % (cnt//8, H*100.0/cnt, len(ctw.nodes), H/8.0, (ctw.root.pw/math.log(2))/-8))

      # TODO: make this generic
      if not compress and cnt == 80000:
        break
  except StopIteration:
    pass

  print("%.2f bytes of entropy, %d bits, %d bytes" % (H/8.0, len(stream), len(enc.ob)))

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

