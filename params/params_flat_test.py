# $Id: params_flat_test.py,v 1.3 2011-10-06 19:14:51 wirawan Exp $
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


def test3(**_opts_):
  """Testing _append_() method."""
  p = params(global_defaults)
  p.nbasis = 399

  print "test3()"
  print "self-defined values = ", p
  print "nbasis = ", p.nbasis   # gives 327. Changes to local vars won't alter anything.
  print "npart = ", p.npart
  print "deltau = ", p.deltau

  # Append new lookup
  dict2 = dict(
    nblk = 37,
    target = 'Titan',
  )
  dict3 = dict(
    nsppol = 2,
    target = '7745x',
  )
  p._append_(dict2, dict3)
  print "target = ", p.target
  print "nblk = ", p.nblk
  print "nsppol = ", p.nsppol


def test4(**_opts_):
  """Testing _prepend_() method."""
  p = params(global_defaults)
  p.nbasis = 399

  print "test4()"
  print "self-defined values = ", p

  # Append new lookup
  dict2 = dict(
    nblk = 37,
    nbasis = 9,
    target = 'Titan',
  )
  dict3 = dict(
    nsppol = 2,
    target = '7745x',
  )
  p._prepend_(dict3, dict2, override_me=1)
  print p._list_
  print "nbasis = ", p.nbasis   # gives 327. Changes to local vars won't alter anything.
  print "npart = ", p.npart
  print "deltau = ", p.deltau
  print "target = ", p.target
  print "nblk = ", p.nblk
  print "nsppol = ", p.nsppol

def test5(**_opts_):
  """Testing _all_keys_() method."""
  p = params(global_defaults)
  p.nbasis = 399

  print "test5()"
  print "self-defined values = ", p

  # Append new lookup
  dict1 = dict(
    nhgss = 300,
    Etrial = -38.948241,
  )
  dict2 = dict(
    nblk = 37,
    nbasis = 9,
    target = 'Titan',
  )
  dict3 = dict(
    nsppol = 2,
    target = '7745x',
  )
  p._append_(dict1)
  p._prepend_(dict3, dict2, override_me=0)
  print p._list_
  print "all keys: ", p._all_keys_()
  print "nbasis = ", p.nbasis   # gives 327. Changes to local vars won't alter anything.
  print "npart = ", p.npart
  print "deltau = ", p.deltau
  print "target = ", p.target
  print "nblk = ", p.nblk
  print "nsppol = ", p.nsppol


def dump_objects():
  """See what's in each dicts.
  """
  pass


if __name__ == "__main__":
  test1()
  test2()
  test2b()
  test5()
  exit()
  test3()
  test4()
