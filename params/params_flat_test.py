# $Id: params_flat_test.py,v 1.2 2011-09-09 18:58:48 wirawan Exp $
# 20100930

from wpylib.params import flat as params

global_defaults = params(
  nbasis= 275,
  npart= 29,
  deltau= 0.01,
)

def test1():
  defaults = {
    'nbasis': 320,
    'npart': 37,
    'deltau': 0.025,
  }
  p = params(defaults, nbasis=332)
  nbasis = 327

  print "test1()"
  print "self-defined values = ", p
  print "nbasis = ", p.nbasis
  print "npart = ", p.npart
  print "deltau = ", p.deltau
  p.deltau = 0.01
  print "new deltau = ", p.deltau


def test2(**_opts_):
  p = global_defaults._create_(_localvars_=1)
  nbasis = 327

  print "test2()"
  print "self-defined values = ", p
  print "nbasis = ", p.nbasis  # gives 275 -- although _localvars_ already requested.
  print "npart = ", p.npart
  print "deltau = ", p.deltau
  p.deltau = 0.01
  print "new deltau = ", p.deltau


def test2b(**_opts_):
  nbasis = 327
  p = global_defaults._create_(_localvars_=1)

  nbasis = 3270

  print "test2()"
  print "self-defined values = ", p
  print "nbasis = ", p.nbasis   # gives 327. Changes to local vars won't alter anything.
  print "npart = ", p.npart
  print "deltau = ", p.deltau
  p.deltau = 0.01
  print "new deltau = ", p.deltau




if __name__ == "__main__":
  test1()
  test2()
  test2b()
