#
# wpylib.math.linalg.gram_schmidt module
# Created: 20150401
# Wirawan Purwanto
#
"""
wpylib.math.linalg.gram_schmidt

Provides Gram-Schmidt orthogonalization of a vector set (a 2-D array).

We will use the modified algorithm that is more stable numerically.

Reference: http://en.wikipedia.org/wiki/Gram%E2%80%93Schmidt_process
"""


def modgs_classic(V):
  """Gram-Schmidt orthonormalization for the column vectors in matrix V.

  Classic routine, all hand-written, no acceleration.
  This is the reference implementation.
  """
  from numpy import array, vdot, empty, outer, sqrt, real
  V = array(V, copy=True)
  assert len(V.shape) == 2
  numcols = V.shape[1]
  N_orig = empty((numcols,), dtype=V.dtype)
  for i in xrange(numcols):
    Vi = V[:,i]
    N_orig[i] = real(vdot(Vi, Vi))  # always a real number
    # FIXME: below could blow up if the norm is exactly zero
    Vi /= sqrt(N_orig[i])
    Ui = Vi  # now Ui has been orthonormalized
    for j in xrange(i+1, numcols):
      Vj = V[:,j]
      proj_Ui_Vj = vdot(Ui, Vj)
      Vj -= proj_Ui_Vj * Ui

  return V, N_orig.real


def modgs_fast1(V):
  """Gram-Schmidt orthonormalization for the column vectors in matrix V.

  Fast(er) routine, replaced inner loop with mat-vec and outer products.
  """
  from numpy import array, dot, vdot, empty, outer, sqrt, real
  V = array(V, copy=True)
  assert len(V.shape) == 2
  numcols = V.shape[1]
  N_orig = empty((numcols,), dtype=V.dtype)
  for i in xrange(numcols):
    Vi = V[:,i]
    N_orig[i] = real(vdot(Vi, Vi))  # always a real number
    # FIXME: below could blow up if the norm is exactly zero
    Vi /= sqrt(N_orig[i])
    Ui = Vi  # now Ui has been orthonormalized
    # Now Vi is normalized -> renamed to Ui
    if i+1 < numcols:
      Vjj = V[:,i+1:]
      proj_u_Vjj = dot(Ui.conj(), Vjj)
      Vjj -= outer(Ui, proj_u_Vjj)

  return V, N_orig.real


def modgs_einsum(V):
  """Gram-Schmidt orthonormalization for the column vectors in matrix V.

  Fast(er) routine, using einsum.
  """
  from numpy import array, vdot, einsum, empty, sqrt, real
  V = array(V, copy=True)
  assert len(V.shape) == 2
  numcols = V.shape[1]
  N_orig = empty((numcols,), dtype=V.dtype)
  for i in xrange(numcols):
    Vi = V[:,i]
    N_orig[i] = real(vdot(Vi, Vi))  # always a real number
    # FIXME: below could blow up if the norm is exactly zero
    Vi /= sqrt(N_orig[i])
    Ui = Vi  # now Ui has been orthonormalized
    # Now Vi is normalized -> renamed to Ui
    if i+1 < numcols:
      Vjj = V[:,i+1:]
      Vjj -= einsum('i,j,jk', Ui, Ui.conj(), Vjj)

  return V, N_orig.real


modgs = modgs_fast1
