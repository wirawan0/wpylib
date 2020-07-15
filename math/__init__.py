# $Id: __init__.py,v 1.3 2010-09-10 21:23:59 wirawan Exp $
#
# wpylib.math main module
# Created: 20091204
# Wirawan Purwanto
#

from __future__ import print_function
from __future__ import division
import sys
import numpy


class MathWarning(Warning):
  """Base class for mathematics-related warnings for wpylib library.
  """



ZERO_TOL = 5.0e-16


# Handle quirks of python2 vs python3
if sys.version_info.major >= 3:
  # simulate "long" function to help write compatible code
  long = lambda X: X



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
    raise ValueError("Unsupported datatype: %s" % str(type(val)))


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
    small = dtype(small // 2)
  return small2


def roundup(value, unit):
  """Rounds up a value to the next integer multiple of a unit."""
  return numpy.ceil(float(value) / float(unit)) * unit


def choose(n,r):
  """Computes n! / {r! (n-r)!} . Note that the following condition must
  always be fulfilled:
      1 <= n
      1 <= r <= n
  Otherwise the result is not predictable!

  Optimization: To minimize the # of multiplications and divisions, we
  rewrite the expression as

        n!      n(n-1)...(n-r+1)
    --------- = ----------------
     r!(n-r)!          r!

  To avoid multiplication overflow as much as possible, we will evaluate
  in the following STRICT order, from left to right:

    n / 1 * (n-1) / 2 * (n-2) / 3 * ... * (n-r+1) / r

  We can show that integer arithmatic operated in this order is exact
  (i.e. no roundoff error).

  Note: this implementation is based on my C++ cp.inc library.
  For other implementations, see:
  http://stackoverflow.com/questions/3025162/statistics-combinations-in-python

  Published in stack overflow, see URL above.
  """
  assert n >= 0
  assert 0 <= r <= n

  c = long(1)
  denom = 1
  for (num,denom) in zip(xrange(n,n-r,-1), xrange(1,r+1,1)):
    c = (c * num) // denom
  return c


def complex_polar(r, theta):
  """Generates regular complex data (scalar or array) from
  an input magnitude and angle."""
  from numpy import sin, cos
  # This way will be friendly for arrays:
  return r * cos(theta) + 1j * r * sin(theta)
