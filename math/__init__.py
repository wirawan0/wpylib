# $Id: __init__.py,v 1.3 2010-09-10 21:23:59 wirawan Exp $
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


def epsilon(dtype):
  """A simple way to determine (at runtime) the precision of a given type
  real number.
  Precision is defined such that (1.0 + epsilon(dtype) > 1.0).
  Below this number, the addition will not yield a different result.
  """
  one = dtype(1.0)
  small = one
  small2 = small
  while one + small > one:
    small2 = small
    small = dtype(small / 2)
  return small2


def roundup(value, unit):
  """Rounds up a value to the next integer multiple of a unit."""
  return numpy.ceil(float(value) / float(unit)) * unit


