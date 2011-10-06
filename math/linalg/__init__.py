# $Id: __init__.py,v 1.2 2011-10-06 19:14:49 wirawan Exp $
#
# wpylib.math.linalg main module
# Created: 20110714
# Wirawan Purwanto
#
"""
wpylib.math.linalg

Provides convenience functions for linear algebra things beyond what's
already provided by numpy.

"""

import numpy
import numpy.linalg

# My favorites:
from numpy import dot, trace
from numpy.linalg import det, inv


def matmul(*Mats):
  """Do successive matrix product. For example,
     matmul(A,B,C,D)
  will evaluate a matrix multiplication ((A*B)*C)*D .
  The matrices must be of matching sizes."""
  p = numpy.dot(Mats[0], Mats[1])
  for M in Mats[2:]:
    p = numpy.dot(p, M)
  return p


