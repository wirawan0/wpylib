# $Id: __init__.py,v 1.2 2010-05-28 18:43:59 wirawan Exp $
#
# wpylib.math main module
# Created: 20091204
# Wirawan Purwanto
#
pass

import numpy

ZERO_TOL = 5.0e-16

def ztol(val, tol=None, copy=True):
  """Rounds down values to zero if they are below tolerance."""
  if tol == None: tol = ZERO_TOL
  if "__iter__" not in dir(val):
    if numpy.abs(val) < tol:
      return 0
    else:
      return val
  elif isinstance(val, numpy.ndarray):
    if copy:
      rslt = val.copy()
    else:
      rslt = val
    numpy.putmask(rslt, numpy.abs(rslt) < tol, [0])
    return rslt
  else:
    raise ValueError, "Unsupported datatype: %s" % str(type(val))

