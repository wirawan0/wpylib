# $Id: result_base.py,v 1.2 2010-11-11 17:59:36 wirawan Exp $
#
# pyqmc.results.result_base.py
# Basic tool for storing the result of a calculation.
#
# Wirawan Purwanto
# Created: 20101025 (pyqmc.results.result_base)
# Moved: 20101111 (to wpylib.db.result_base)
#

"""
The class result_base is very similar to
wpylib.params.params_flat.Parameters ,
except that it does not contain multiple dict-like objects, thus is
much simpler.

class: result_base

The result_base class concerns itself with loading structured set of
values or parameters from external sources (e.g., from a text file or
other binary file) in order to make the data amenable to machine
processing.
"""

import os
import os.path

class result_base(dict):
  '''Structure to represent metadata or structured result.
  No particular structure is assumed.
  Results are fetchable by either X.member or X['member'] syntax, and
  these results are typically meant to be read-only.

  CAVEATS
  * Note: dict method names are left intact.
    Please be aware when programming using result_base object!
  * Please do not prefix or suffix dataset member names with underscore.
    Those names are reserved for internal purposes.
  * In some cases, additional methods are required to be defined in the
    derived class:
    - parse_file_(self, filename)
  * Additional possible field names set by this class:
    - filename_
    - absfilename_ -- full file name including absolute directory path.
  * __setattr__ is not set.
    Result-related attributes are supposed to be read-only.
    As a consequence, adding metadata or result *must* be done in the
    dict way, e.g.
        X['nblocks'] = 32
    instead of
        X.nblocks = 32.

  '''
  def __init__(self, _src_=None, **_extra_values_):
    """Initializes structured dataset.
    By default, the source can be one of the following:
    * a dict: then the values are copied over (shallow copy) to this
      object.
    * a string containing filename: then the virtual parse_file_ method
      is invoked.
    Other unrecognized keyword arguments will be stored in the
    object's dictionary as part of the result.
    """
    src = _src_
    if isinstance(src, dict):
      self.clear()
      self.update(src)
    elif isinstance(src, basestring):
      # WARNING: Awaiting future definition of parse_text_file_().
      # This must be specified in the derived class.
      self.parse_file_(src)
      self.filename_ = src
      self.absfilename_ = os.path.abspath(src)
    else:
      pass
    self.update(_extra_values_)
  def __getattr__(self, key):
    try:
      return self[key]
    except:
      return dict.__getattribute__(self, key)
  def __str__(self):
    return "<" +self.__module__ + "." + self.__class__.__name__ + \
      " object (" + dict.__str__(self) + ")>"


# Test programs
if __name__ == "__main__":

  def _test_result_base1():
    x = result_base()
    print x.keys()
    print x.values()
    x['nblocks'] = 32
    print x

    y = result_base({'lack': 352, 'Etrial': -32.764})
    print y.keys()
    print y.values()
    y['nblocks'] = 32
    print y
    print y.Etrial


  _test_result_base1()
