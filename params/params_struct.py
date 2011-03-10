# $Id: params_struct.py,v 1.2 2011-03-10 19:21:33 wirawan Exp $
#
# wpylib.params.params_struct module
# Created: 20110310
# Wirawan Purwanto
#
"""
params_struct.py

This module hosts `Struct', the simplest structured datatype,
which in python is basically the same as dict.
However this syntactic sugar will make your code very much like other
high-level language (less mess with a['member'] kind of thing).
Also this class will allow us to provide a base class to more specialized
classes of similar nature.

Other classes that are similar in purpose:

* wpylib.params.params_flat.Parameters
  For assisting parameter lookup in functions.

* wpylib.db.result_base
  For storing result from program output file.



CHARACTERISTICS/USAGE PATTERN

* Just like dict, it does not enforce a particular structure.
* Use words only as keys (i.e. keys are valid python identifiers).
* User fields should not use keywords prepended and appended by two underscores
  (those names are reserved by python).


"""


class Struct(object):
  """A simplistic structured datatype.
  No particular structure is assumed.
  Results are fetchable by either X.member or X['member'] syntax.
  Limited dict-like operations are supported."""
  def __init__(self, __src__=None, **p):
    """Initializes the structure.
    The arguments will be copied into the structure as the initial values
    of the structure.
    They can be a dict-like object (first argument), or "key=value"-type
    argument passing.
    """
    if __src__: self.__dict__.update(__src__)
    self.__dict__.update(p)
  def __getitem__(self, item):
    return self.__dict__[item]
  def __setitem__(self, item, val):
    self.__dict__[item] = val
  def __contains__(self, item):
    return item in self.__dict__
  def __iter__(self):
    return self.__dict__.__iter__()

