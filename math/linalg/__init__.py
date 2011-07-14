# $Id: __init__.py,v 1.1 2011-07-14 19:00:59 wirawan Exp $
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

def matmul(*Mats):
  """Do successive matrix product. For example,
     matmul(A,B,C,D)
  will evaluate a matrix multiplication ((A*B)*C)*D .
  The matrices must be of matching sizes."""
  p = numpy.dot(Mats[0], Mats[1])
  for M in Mats[2:]:
    p = numpy.dot(p, M)
  return p


