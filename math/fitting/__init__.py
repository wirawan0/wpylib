# $Id: fitting.py,v 1.4 2011-04-05 19:20:01 wirawan Exp $
#
# wpylib.math.fitting module
# Created: 20100120
# Wirawan Purwanto
#
# Imported 20100120 from $PWQMC77/expt/Hybrid-proj/analyze-Eh.py
# (dated 20090323).
#
# Some references on fitting:
# * http://stackoverflow.com/questions/529184/simple-multidimensional-curve-fitting
# * http://www.scipy.org/Cookbook/OptimizationDemo1 (not as thorough, but maybe useful)

import numpy
import scipy.optimize
from wpylib.db.result_base import result_base

last_fit_rslt = None
last_chi_sqr = None

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
  """Polynomial of order 2 without cross terms."""
  order = 2
  def __call__(self, C, x):
    return C[0] \
      + sum([ C[i*2+1] * x[i] + C[i*2+2] * x[i]**2 \
              for i in xrange(len(x)) ])

class Poly_order2_only(Poly_base):
  """Polynomial of order 2 without cross terms.
  The linear terms are deleted."""
  order = 1 # HACK: the linear term is deleted
  def __call__(self, C, x):
    return C[0] \
      + sum([ C[i+1] * x[i]**2 \
              for i in xrange(len(x)) ])

class Poly_order2x_only(Poly_base):
  '''Order-2-only polynomial with all the cross terms.'''
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
  """Polynomial of order 3 without cross terms.
  The linear terms are deleted."""
  order = 3
  def __call__(self, C, x):
    return C[0] \
         + sum([ C[i*3+1] * x[i] + C[i*3+2] * x[i]**2 + C[i*3+3] * x[i]**3 \
                 for i in xrange(len(x)) ])

class Poly_order4(Poly_base):
  """Polynomial of order 4 without cross terms.
  The linear terms are deleted."""
  order = 4
  def __call__(self, C, x):
    return C[0] \
         + sum([ C[i*4+1] * x[i] + C[i*4+2] * x[i]**2 + C[i*4+3] * x[i]**3 + C[i*4+4] * x[i]**4 \
                 for i in xrange(len(x)) ])


class fit_result(result_base):
  pass

def fit_func(Funct, Data=None, Guess=None, x=None, y=None,
             debug=0,
             outfmt=1,
             method='leastsq', opts={}):
  """
  Performs a function fitting.
  The domain of the function is a D-dimensional vector, and the function
  yields a scalar.

  Funct is a python function (or any callable object) with argument list of
  (C, x), where:
  * C is the cofficients (parameters) being adjusted by the fitting process
    (it is a sequence or a 1-D array)
  * x is a 2-D array (or sequence of like nature), say,
    of size "N rows times M columns".
    N is the dimensionality of the domain, while
    M is the number of data points, whose count must be equal to the
    size of y data below.
    For a 2-D fitting, for example, x should be a column array.

  The "y" array is a 1-D array of length M, which contain the "measured"
  value of the function at every domain point given in "x".

  Inspect Poly_base, Poly_order2, and other similar function classes in this
  module to see the example of the Funct function.

  The measurement (input) datasets, against which the function is to be fitted,
  can be specified in one of two ways:
  * via x and y arguments. x is a multi-column dataset, where each row is the
    (multidimensional) coordinate of the Funct's domain.
    y is a one-dimensional dataset.
    Or,
  * via Data argument (which is a multi-column dataset, where the first row
    is the "y" argument).

  """
  global last_fit_rslt, last_chi_sqr
  from scipy.optimize import fmin, fmin_bfgs, leastsq, anneal
  # We want to minimize this error:
  if Data != None: # an alternative way to specifying x and y
    y = Data[0]
    x = Data[1:] # possibly multidimensional!
  if hasattr(Funct, "Guess_xy"):
    # Try to provide an initial guess
    Guess = Funct.Guess_xy(x, y)
  elif hasattr(Funct, "Guess"):
    # Try to provide an initial guess
    # This is an older version with y-only argument
    Guess = Funct.Guess(y)
  elif Guess == None: # VERY OLD, DO NOT USE ANYMORE!
    Guess = [ y.mean() ] + [0.0, 0.0] * len(x)

  if debug < 20:
    fun_err = lambda CC, xx, yy: abs(Funct(CC,xx) - yy)
    fun_err2 = lambda CC, xx, yy: numpy.sum(abs(Funct(CC,xx) - yy)**2)
  else:
    def fun_err(CC, xx, yy):
      ff = Funct(CC,xx)
      r = abs(ff - yy)
      print "  err: %s << %s << %s, %s" % (r, ff, CC, xx)
      return r
    def fun_err2(CC, xx, yy):
      ff = Funct(CC,xx)
      r = numpy.sum(abs(ff - yy)**2)
      print "  err: %s << %s << %s, %s" % (r, ff, CC, xx)
      return r

  if debug >= 5:
    print "Guess params:"
    print Guess

  if method == 'leastsq':
    # modified Levenberg-Marquardt algorithm
    rslt = leastsq(fun_err,
                   x0=Guess, # initial coefficient guess
                   args=(x,y), # data onto which the function is fitted
                   full_output=1,
                   **opts
                   )
    keys = ('xopt', 'cov_x', 'infodict', 'mesg', 'ier') # ier = error message code from MINPACK
  elif method == 'fmin':
    # Nelder-Mead Simplex algorithm
    rslt = fmin(fun_err2,
                x0=Guess, # initial coefficient guess
                args=(x,y), # data onto which the function is fitted
                full_output=1,
                **opts
               )
    keys = ('xopt', 'fopt', 'iter', 'funcalls', 'warnflag', 'allvecs')
  elif method == 'fmin_bfgs' or method == 'bfgs':
    # Broyden-Fletcher-Goldfarb-Shanno (BFGS) algorithm
    rslt = fmin_bfgs(fun_err2,
                     x0=Guess, # initial coefficient guess
                     args=(x,y), # data onto which the function is fitted
                     full_output=1,
                     **opts
                    )
    keys = ('xopt', 'fopt', 'funcalls', 'gradcalls', 'warnflag', 'allvecs')
  elif method == 'anneal':
    rslt = anneal(fun_err2,
                  x0=Guess, # initial coefficient guess
                  args=(x,y), # data onto which the function is fitted
                  full_output=1,
                  **opts
                 )
    keys = ('xopt', 'fopt', 'T', 'funcalls', 'iter', 'accept', 'retval')
  else:
    raise ValueError, "Unsupported minimization method: %s" % method
  chi_sqr = fun_err2(rslt[0], x, y)
  last_chi_sqr = chi_sqr
  last_fit_rslt = rslt
  if (debug >= 10):
    #print "Fit-message: ", rslt[]
    print "Fit-result:"
    print "\n".join([ "%2d  %s" % (ii, rslt[ii]) for ii in xrange(len(rslt)) ])
  if debug >= 1:
    print "params = ", rslt[0]
    print "chi square = ", last_chi_sqr / len(y)
  if outfmt == 1:
    return rslt[0]
  else:
    rec = fit_result(dict(zip(keys, rslt)))
    rec['chi_square'] = chi_sqr
    rec['fit_method'] = method
    return rec

