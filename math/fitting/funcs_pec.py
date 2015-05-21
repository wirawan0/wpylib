#
# wpylib.math.fitting.funcs_pec module
# Created: 20150521
# Wirawan Purwanto
#
# Imported 20150521 from Cr2_analysis_cbs.py
# (dated 20141017, CVS rev 1.143).
#

"""
wpylib.math.fitting.funcs_pec module
A library of simple f(x) functions for PEC fitting

For use with OO-style x-y curve fitting interface.
"""

import numpy


class harm_fit_func(fit_func_base):
  """Harmonic function object.
  For use with fit_func function on a PEC.

  Functional form:

      E0 + 0.5 * k * (x - re)**2

  Coefficients:
  * C[0] = energy minimum
  * C[1] = spring constant
  * C[2] = equilibrium distance
  """
  dim = 1  # a function with 1-D domain
  param_names = ('E0', 'k', 'r0')
  def __call__(self, C, x):
    xdisp = (x[0] - C[2])
    y = C[0] + 0.5 * C[1] * xdisp**2
    self.func_call_hook(C, x, y)
    return y
  def Guess_xy(self, x, y):
    fit_rslt = fit_harm(x[0], y)
    self.guess_params = tuple(fit_rslt[0])
    return self.guess_params


class harmcube_fit_func(fit_func_base):
  """Harmonic + cubic term function object.
  For use with fit_func function on a PEC.

  Functional form:

      E0 + 0.5 * k * (x - re)**2 + cub * (x - re)**3;

  Coefficients:
  * C[0] = energy minimum
  * C[1] = spring constant
  * C[2] = equilibrium distance
  * C[3] = nonlinear (cubic) constant
  """
  dim = 1  # a function with 1-D domain
  param_names = ('E0', 'k', 'r0', 'c3')
  def __call__(self, C, x):
    xdisp = (x[0] - C[2])
    y = C[0] + 0.5 * C[1] * xdisp**2 + C[3] * xdisp**3
    self.func_call_hook(C, x, y)
    return y
  def Guess_xy(self, x, y):
    fit_rslt = fit_harm(x[0], y)
    self.guess_params = tuple(fit_rslt[0]) + (0,)
    return self.guess_params
  def Guess_xy_old(self, x, y):
    imin = numpy.argmin(y)
    return (y[imin], 2, x[0][imin], 0.00001)


class morse2_fit_func(fit_func_base):
  """Morse2 function object.
  For use with fit_func function.

  Functional form:

      E0 + 0.5 * k / a**2 * (1 - exp(-a * (x - re)))**2

  Coefficients:
  * C[0] = energy minimum
  * C[1] = spring constant
  * C[2] = equilibrium distance
  * C[3] = nonlinear constant
  """
  dim = 1  # a function with 1-D domain
  param_names = ('E0', 'k', 'r0', 'a')
  def __call__(self, C, x):
    from numpy import exp
    E0, k, r0, a = self.get_params(C, *(self.param_names))
    y = E0 + 0.5 * k / a**2 * (1 - exp(-a * (x[0] - r0)))**2
    self.func_call_hook(C, x, y)
    return y
  def Guess_xy(self, x, y):
    imin = numpy.argmin(y)
    harm_params = fit_harm(x[0], y)
    if self.debug >= 10:
      print "Initial guess by fit_harm gives: ", harm_params
    self.guess_params = (y[imin], harm_params[0][1], x[0][imin], 0.01 * harm_params[0][1])
    return self.guess_params
  def Guess_xy_old(self, x, y):
    imin = numpy.argmin(y)
    return (y[imin], 2, x[0][imin], 0.01)


class ext3Bmorse2_fit_func(fit_func_base):
  """ext3Bmorse2 function object.
  For use with fit_func function.

  Functional form:

      E0 + 0.5 * k / a**2 * (1 - exp(-a * (x - re)))**2
         + C3 * (1 - exp(-a * (x - re)))**3

  Coefficients:
  * C[0] = energy minimum
  * C[1] = spring constant
  * C[2] = equilibrium distance
  * C[3] = nonlinear constant
  * C[4] = coefficient of cubic term
  """
  dim = 1  # a function with 1-D domain
  def __call__(self, C, x):
    from numpy import exp
    E = 1 - exp(-C[3] * (x[0] - C[2]))
    y = C[0] + 0.5 * C[1] / C[3]**2 * E**2 + C[4] * E**3
    self.func_call_hook(C, x, y)
    return y
  def Guess_xy(self, x, y):
    imin = numpy.argmin(y)
    harm_params = fit_harm(x[0], y)
    if self.debug >= 10:
      print "Initial guess by fit_harm gives: ", harm_params
    self.guess_params = (y[imin], harm_params[0][1], x[0][imin], 0.01 * harm_params[0][1], 0)
    return self.guess_params


