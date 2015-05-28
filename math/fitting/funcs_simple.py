#
# wpylib.math.fitting.funcs_simple module
# Created: 20150520
# Wirawan Purwanto
#
# Imported 20150520 from Cr2_analysis_cbs.py
# (dated 20141017, CVS rev 1.143).
#

"""
wpylib.math.fitting.funcs_simple module
A library of simple f(x) functions for fitting

For use with OO-style x-y curve fitting interface.
"""

import numpy
from wpylib.math.fitting import fit_func_base


# Some simple function fitting--to aid fitting the complex ones later

def fit_linear(x, y):
  """Warning: the ansatz for fitting is
      C[0] + C[1]*x
  so I have to reverse the order of fit parameters.
  """
  rslt = numpy.polyfit(x, y, 1, full=True)
  return (rslt[0][::-1],) + rslt


def fit_harm(x, y):
  """Do a quadratic fit using poly fit and return it in terms of coeffs
  like this one:

      C0 + 0.5 * C1 * (x - C2)**2

  =>  0.5*C1*x**2 - C1*C2*x + (C0 + 0.5 * C1 * C2**2)

  Polyfit gives:
      a * x**2 + b * x + c

  Equating the two, we get:

      C1 = 2 * a
      C2 = -b/C1
      C0 = c - 0.5*C1*C2**2

  This function returns the recast parameters plus the original
  fit output.
  """
  rslt = numpy.polyfit(x, y, 2, full=True)

  (a,b,c) = rslt[0]
  C1 = 2*a
  C2 = -b/C1
  C0 = c - 0.5*C1*C2**2

  return ((C0,C1,C2),) + rslt



# fit_func-style functional ansatz

class const_fit_func(fit_func_base):
  """Constant function object.
  For use with fit_func function on a PEC.

  Functional form:

      C[0]

  Coefficients:
  * C[0] = the constant sought
  """
  dim = 1  # a function with 1-D domain
  param_names = ('c')
  def __call__(self, C, x):
    from numpy import exp
    y = C[0]
    self.func_call_hook(C, x, y)
    return y
  def Guess_xy(self, x, y):
    self.guess_params = (numpy.average(y),)
    return self.guess_params


class linear_fit_func(fit_func_base):
  """Linear function object.
  For use with fit_func function.

  Functional form:

      a + b * x

  Coefficients:
  * C[0] = a
  * C[1] = b
  """
  dim = 1  # a function with 1-D domain
  param_names = ('a', 'b')
  def __call__(self, C, x):
    y = C[0] + C[1] * x[0]
    self.func_call_hook(C, x, y)
    return y
  def Guess_xy(self, x, y):
    fit_rslt = fit_linear(x[0], y)
    self.guess_params = tuple(fit_rslt[0])
    return self.guess_params


class linear_leastsq_fit_func(linear_fit_func):
  def fit(self, x, y, dy=None, fit_opts=None, Funct_hook=None, Guess=None):
    from wpylib.math.fitting.linear import linregr2d_SZ
    # Changed from:
    #   rslt = fit_linear_weighted(x,y,dy)
    # to:
    rslt = linregr2d_SZ(x, y, sigma=dy)

    self.last_fit = rslt[1]
    # Retrofit for API compatibility: not necessarily meaningful
    self.guess_params = rslt[0]
    return rslt[0]


class exp_fit_func(fit_func_base):
  """Exponential function object.
  For use with fit_func function.

  Functional form:

      C[0] * (exp(C[1] * (x - C[2]))

  Coefficients:
  * C[0] = amplitude
  * C[1] = damping factor
  * C[2] = offset
  """
  dim = 1  # a function with 1-D domain
  param_names = ['A', 'B', 'x0']
  # FIXME: AD HOC PARAMETERS!
  A_guess =  -2.62681
  B_guess =  -9.05046
  x0_guess = 1.57327
  def __call__(self, C, x):
    from numpy import exp
    A, B, x0 = self.get_params(C, *(self.param_names))
    y = A * exp(B * (x[0] - x0))
    self.func_call_hook(C, x, y)
    return y
  def Guess_xy(self, x, y):
    from numpy import abs
    #y_abs = abs(y)
    # can do linear fit to guess the params,
    # but how to separate A and B*x0, I don't know.
    #imin = numpy.argmin(y)
    self.guess_params = (self.A_guess, self.B_guess, self.x0_guess)
    return self.guess_params


class expm_fit_func(exp_fit_func):
  """Similar to exp_fit_func but the exponent is always negative.
  """
  def __call__(self, C, x):
    from numpy import exp,abs
    A, B, x0 = self.get_params(C, *(self.param_names))
    y = A * exp(-abs(B) * (x[0] - x0))
    self.func_call_hook(C, x, y)
    return y


class powx_fit_func(fit_func_base):
  """Power of x function object.
  For use with fit_func function.

  Functional form:

      C[0] * ((x - C[2])**C[1])

  Coefficients:
  * C[0] = amplitude
  * C[1] = exponent (< 0)
  * C[2] = offset
  """
  dim = 1  # a function with 1-D domain
  param_names = ['A', 'B', 'x0']
  # FIXME: AD HOC PARAMETERS!
  A_guess =  -2.62681
  B_guess =  -9.05046
  x0_guess = 1.57327
  def __call__(self, C, x):
    from numpy import exp
    A, B, x0 = self.get_params(C, *(self.param_names))
    y = A * (x[0] - x0)**B
    self.func_call_hook(C, x, y)
    return y
  def Guess_xy(self, x, y):
    from numpy import abs
    #y_abs = abs(y)
    # can do linear fit to guess the params,
    # but how to separate A and B*x0, I don't know.
    #imin = numpy.argmin(y)
    self.guess_params = (self.A_guess, self.B_guess, self.x0_guess)
    return self.guess_params


class invx_fit_func(powx_fit_func):
  """Inverse of x function object that leads to 0 as x->infinity.
  For use with fit_func function.

  Functional form:

      C[0] * ((x - C[2])**C[1])

  Specialized for CBX1 extrapolation
  Coefficients:
  * C[0] = amplitude (< 0)
  * C[1] = exponent (< 0)
  * C[2] = offset (> 0)
  """
  """
  /home/wirawan/Work/GAFQMC/expt/qmc/Cr2/CBS-TZ-QZ/UHF-CBS/20140128/Exp-CBX1.d/fit-invx.plt

     Iteration 154
     WSSR        : 0.875715          delta(WSSR)/WSSR   : -9.96404e-06
     delta(WSSR) : -8.72566e-06      limit for stopping : 1e-05
     lambda	  : 0.00174063

    resultant parameter values

    A               = -29.7924
    B               = -13.2967
    x0              = 0.399396

    After 154 iterations the fit converged.
    final sum of squares of residuals : 0.875715
    rel. change during last iteration : -9.96404e-06

    degrees of freedom    (FIT_NDF)                        : 2
    rms of residuals      (FIT_STDFIT) = sqrt(WSSR/ndf)    : 0.661708
    variance of residuals (reduced chisquare) = WSSR/ndf   : 0.437858

    Final set of parameters            Asymptotic Standard Error
    =======================            ==========================

    A               = -29.7924         +/- 8027         (2.694e+04%)
    B               = -13.2967         +/- 196.1        (1474%)
    x0              = 0.399396         +/- 21.4         (5357%)


    correlation matrix of the fit parameters:

                   A      B      x0
    A               1.000
    B               1.000  1.000
    x0              1.000  1.000  1.000

  For some reason the fit code in python gives:
  A,B,x0 = (-7028.1498486021028, -16.916447508009664, 2.2572321406455487e-06)
  but they fit almost exactly the same in the region 1.8 <= r <= 3.0.

  """
  A_guess =  -29.7924
  B_guess =  -13.2967
  x0_guess = 0.399396
  def __init__(self):
    from lmfit import Parameters
    self.fit_method = "lmfit:leastsq"
    p = Parameters()
    p.add_many(
      # (Name,  Value,  Vary,   Min,  Max,  Expr)
        ('A',   -2.6,   True,  -1e6, -1e-9,  None),
        ('B',   -2.0,   True,  None, -1e-9,  None),
        ('x0',   1.9,   True,  1e-6, None,   None),
      # The values are just a placeholder. They will be set later.
    )
    self.Params = p


