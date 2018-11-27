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

# https://en.wikipedia.org/wiki/Krichevsky–Trofimov_estimator
lookup = defaultdict(lambda: [0.5,1.0])

bg = bitgen(enw)
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

    H = -math.log2(p_x)
    HH += H

    # increment tables
    lookup[px][0] += x == 1
    lookup[px][1] += 1
    prevx.append(x)
    prevx = prevx[-NUMBER_OF_BITS:]

except StopIteration:
  pass
print("%.2f bytes of entropy" % (HH/8.0))


