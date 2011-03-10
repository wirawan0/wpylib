# $Id: params_struct.py,v 1.1 2011-03-10 17:17:48 wirawan Exp $
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
* Do not prepend and append two underscores at the same time.


"""


class Struct(object):
  """A simplistic structured datatype.
  No particular structure is assumed.
  Results are fetchable by either X.member or X['member'] syntax.
  Limited dict-like operations are supported."""
  def __getitem__(self, item):
    if hasattr(self, item):
      return getattr(self, item)
    else:
      raise KeyError, "Invalid result name: %s" % (item)
  def __contains__(self, item):
    #return item in dir(self)
    return hasattr(self, item)
