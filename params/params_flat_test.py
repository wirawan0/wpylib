# $Id: params_flat_test.py,v 1.1 2010-09-30 16:16:38 wirawan Exp $
# 20100930

from wpylib.params import flat as params

def test1():
  defaults = {
    'nbasis': 320,
    'npart': 37,
    'deltau': 0.025,
  }
  p = params(defaults, nbasis=332)

  print "self-defined values = ", p
  print "nbasis = ", p.nbasis
  print "npart = ", p.npart
  print "deltau = ", p.deltau
  p.deltau = 0.01
  print "new deltau = ", p.deltau


if __name__ == "__main__":
  test1()

