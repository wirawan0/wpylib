# $Id: params_flat_test.py,v 1.3 2011-10-06 19:14:51 wirawan Exp $
# 20100930

from wpylib.params import flat as params
from pprint import pprint

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
  """Testing _localvars_ option."""
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
  """Testing _localvars_ option."""
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


def test6():
  """Tests active method."""
  from wpylib.text_tools import str_snippet as snippet
  from wpylib.params.params_flat import ActiveReadValue as Act
  defaults = {
    'nbasis': 320,
    'npart': 37,
    'deltau': 0.025,
  }
  print "test6()"
  p = params(defaults, nbasis=332)
  p.input_template = Act(lambda P: snippet("""\
  input = {
    nbasis = %(nbasis)d
    npart = %(npart)d
    deltau = %(deltau)s
  };
  code = {
    %(code_template)s
  };
  """) % P)
  p.code_template = Act(lambda P: snippet("""\
    for (i = 1; %(nbasis)d; ++i) {
      print i, %(deltau)g
    }
  """) % P)
  print "\nInput template 1:"
  print p.input_template

  p.nbasis = 327
  print "\nInput template 2 after updating nbasis:"
  print p.input_template

  print "\nHere is the generator script:\n*%(input_template)s*" % p._create_(deltau=2.775)
  # FAILED: The deltau was not updated to 2.775 as it should have.
  # WHY? Because _create_ does NOT take any keyword argument like that
  # to override the values.


def test7():
  """Demonstrates the FAILURE of active method when the params is inherited
  elsewhere.
  Workaround: we must flatten the lookup dicts into one, then you the active method
  will work."""
  from wpylib.text_tools import str_snippet as snippet
  from wpylib.params.params_flat import ActiveReadValue as Act
  defaults = {
    'nbasis': 320,
    'npart': 37,
    'deltau': 0.025,
  }
  print "test7()"
  p = params(defaults, nbasis=332)
  p.input_template = Act(lambda P: snippet("""\
  input = {
    nbasis = %(nbasis)d
    npart = %(npart)d
    deltau = %(deltau)s
  };
  code = {
    %(code_template)s
  };
  """) % P)
  p.code_template = Act(lambda P: snippet("""\
    for (i = 1; %(nbasis)d; ++i) {
      print i, %(deltau)g
    }
  """) % P)
  print "\nInput template 1:"
  print p.input_template
  print "\n--- The case above was OK. ---\n"

  print "\n--- The case below was not OK. ---\nThe nbasis and deltau args were not updated in two printouts below"
  Q = params(p)
  Q.nbasis = 327
  print "\nInput template 2 after updating nbasis:"
  print Q.input_template


  print "\n--- The case below was OK, but it requires flattening of the search dicts. ---\n"

  R = params(p, _flatten_=True)
  R.nbasis = 327
  pprint(R)
  print len(R._list_)
  print "\nInput template 2 after flattening and updating nbasis:"
  print R.input_template

  print "\nHere is the generator script:\n*%(input_template)s*" % p._create_(_flatten_=True)._update_(dict(deltau=2.775))

def test8():
  dict1 = params(a=10, b=12)
  dict2 = params(dict1, b=333, c=421)
  dict3 = params(dict2, d=38, e="joey", a=32768)
  pprint(dict3._flatten_())


def dump_objects():
  """See what's in each dicts.
  """
  pass


if __name__ == "__main__":
  test8()
  exit()
  test1()
  test2()
  test2b()
  test5()
  exit()
  test3()
  test4()
