#
# wpylib.math.fitting.funcs_poly module
# Created: 20150520
# Wirawan Purwanto
#
# Split 20150520 from wpylib.math.fitting module
#

"""
Module wpylib.math.fitting.funcs_poly

Legacy examples for 2-D polynomial function ansatz for fitting.
Newer applications should
"""


class Poly_base(object):
  """Typical base class for a function to fit a polynomial. (?)

  The following members must be defined to use the basic features in
  this class---unless the methods are redefined appropriately:
  * order = the order (maximum exponent) of the polynomial.
  * dim = dimensionality of the function domain (i.e. the "x" coordinate).
    A 2-dimensional (y vs x) fitting will have dim==1.
    A 3-dimensional (z vs (x,y)) fitting will have dim==2.
    And so on.
  """
  # Must set the following:
  # * order = ?
  # * dim = ?
  #def __call__(C, x):
  #    raise NotImplementedError, "must implement __call__"
  def __init__(self, xdata=None, ydata=None, ndim=None):
    if xdata != None:
      self.dim = len(xdata)
    elif ndim != None:
      self.dim = ndim
    else:
      raise ValueError, "Either xdata or ndim argument must be supplied"
    if ydata: self.guess = [ numpy.mean(ydata) ] + [0.0] * (self.order*self.dim)
  def Guess(self, ydata):
    """The simplest guess: set the parameter for the constant term to <y>, and
    the rest to zero. In general, this may not be the best."""
    return [ numpy.mean(ydata) ] + [0.0] * (self.NParams() - 1)
  def NParams(self):
    '''Default NParams for polynomial without cross term.'''
    return 1 + self.order*self.dim


class Poly_order2(Poly_base):
  """Multidimensional polynomial of order 2 without cross terms."""
  order = 2
  def __call__(self, C, x):
    return C[0] \
      + sum([ C[i*2+1] * x[i] + C[i*2+2] * x[i]**2 \
              for i in xrange(len(x)) ])


class Poly_order2_only(Poly_base):
  """Multidimensional polynomial of order 2 without cross terms.
  The linear terms are deleted."""
  order = 1 # HACK: the linear term is deleted
  def __call__(self, C, x):
    return C[0] \
      + sum([ C[i+1] * x[i]**2 \
              for i in xrange(len(x)) ])


class Poly_order2x_only(Poly_base):
  '''Multidimensional order-2-only polynomial with all the cross terms.'''
  order = 2 # but not used
  def __call__(self, C, x):
    ndim = self.dim
    # Reorganize the coeffs in the form of symmetric square matrix
    # For 4x4 it will become like:
    #   [ 1,  5,  6,  7]
    #   [ 5,  2,  8,  9]
    #   [ 6,  8,  3, 10]
    #   [ 7,  9, 10,  4]
    Cmat = numpy.diag(C[1:ndim+1])
    j = ndim+1
    for r in xrange(0, ndim-1):
      jnew = j + ndim - 1 - r
      Cmat[r, r+1:] = C[j:jnew]
      Cmat[r+1:, r] = C[j:jnew]
      j = jnew
    #print Cmat
    #print x
    nrec = len(x[0]) # assume a 2-D array
    rslt = numpy.empty((nrec,), dtype=numpy.float64)
    for r in xrange(nrec):
      rslt[r] = C[0] \
              + numpy.sum( Cmat * numpy.outer(x[:,r], x[:,r]) )
    return rslt

  def NParams(self):
    # 1 is for the constant term
    return 1 + self.dim * (self.dim + 1) / 2


class Poly_order3(Poly_base):
  """Multidimensional polynomial of order 3 without cross terms.
  The linear terms are deleted."""
  order = 3
  def __call__(self, C, x):
    return C[0] \
         + sum([ C[i*3+1] * x[i] + C[i*3+2] * x[i]**2 + C[i*3+3] * x[i]**3 \
                 for i in xrange(len(x)) ])

class Poly_order4(Poly_base):
  """Multidimensional polynomial of order 4 without cross terms.
  The linear terms are deleted."""
  order = 4
  def __call__(self, C, x):
    return C[0] \
         + sum([ C[i*4+1] * x[i] + C[i*4+2] * x[i]**2 + C[i*4+3] * x[i]**3 + C[i*4+4] * x[i]**4 \
                 for i in xrange(len(x)) ])


