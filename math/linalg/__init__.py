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

from .gram_schmidt import modgs

MATMUL_USE_BLAS = False

def matmul(*Mats, **opts):
  """Do successive matrix product. For example,
     matmul(A,B,C,D)
  will evaluate a matrix multiplication ((A*B)*C)*D .
  The matrices must be of matching sizes."""
  from numpy import asarray, dot, iscomplexobj
  use_blas = opts.get('use_blas', MATMUL_USE_BLAS)
  debug = opts.get('debug', True)
  if debug:
    def dbg(msg):
      print msg,
  else:
    def dbg(msg):
      pass
  if use_blas:
    try:
      from scipy.linalg.blas import zgemm, dgemm
    except:
      # Older scipy (<= 0.10?)
      from scipy.linalg.blas import fblas
      zgemm = fblas.zgemm
      dgemm = fblas.dgemm

  if not use_blas:
    p = dot(Mats[0], Mats[1])
    for M in Mats[2:]:
      p = dot(p, M)
  else:
    dbg("Using BLAS\n")
    # FIXME: Right now only supporting double precision arithmetic.
    M0 = asarray(Mats[0])
    M1 = asarray(Mats[1])
    if iscomplexobj(M0) or iscomplexobj(M1):
      p = zgemm(alpha=1.0, a=M0, b=M1)
      Cplx = True
      dbg("- zgemm ")
    else:
      p = dgemm(alpha=1.0, a=M0, b=M1)
      Cplx = False
      dbg("- dgemm ")
    for M in Mats[2:]:
      M2 = asarray(M)
      if Cplx or iscomplexobj(M2):
        p = zgemm(alpha=1.0, a=p, b=M2)
        Cplx = True
        dbg(" zgemm")
      else:
        p = dgemm(alpha=1.0, a=p, b=M2)
        dbg(" dgemm")
    dbg("\n")
  return p


