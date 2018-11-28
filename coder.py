class Coder():
  def __init__(self, ob=[]):
    self.l = 0
    self.h = 0xffffffff
    self.ob = ob

  def code(self, p_0, x=None):
    assert self.l <= self.h
    assert self.l >= 0 and self.l < 0x100000000
    assert self.h >= 0 and self.h < 0x100000000
    decode = (x == None)

    # key insight, the precision doesn't have to be perfect
    # just the same on encode and decode
    p_0 = int(254*p_0 + 1)
    split = self.l + (((self.h - self.l)*p_0) >> 8)

    if decode:
      if len(self.ob) < 4:
        raise StopIteration
      bob = (self.ob[0]<<24) | (self.ob[1]<<16) | (self.ob[2]<<8) | self.ob[3]
      #print("%8x" % bob)
      x = int(bob >= split)

    if x == 0:
      self.h = split
    else:
      self.l = split + 1

    #print("%d -- %8x %8x -- %8x" % (x, self.l, self.h, split)) 

    while self.l>>24 == self.h>>24:
      if decode:
        assert self.ob[0] == self.l >> 24
        self.ob = self.ob[1:]
      else:
        assert (self.l >> 24) < 256
        self.ob.append(self.l >> 24)
      #print("shift %X" % (self.l >> 24))
      self.l = ((self.l & 0xFFFFFF) << 8)
      self.h = ((self.h & 0xFFFFFF) << 8) | 0xFF

    return x

