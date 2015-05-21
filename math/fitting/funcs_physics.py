#
# wpylib.math.fitting.funcs_physics module
# Created: 20150521
# Wirawan Purwanto
#
# Imported 20150521 from Cr2_analysis_cbs.py
# (dated 20141017, CVS rev 1.143).
#

"""
wpylib.math.fitting.funcs_physics module
A library of simple f(x) functions for physics-related common functional fitting

For use with OO-style x-y curve fitting interface.
"""

import numpy


class FermiDirac_fit_func(fit_func_base):
  """Fermi-Dirac function object.
  For use with fit_func function.

  Functional form:

      C[0] * (exp((x - C[1]) / C[2]) + 1)^-1

  Coefficients:
  * C[0] = amplitude
  * C[1] = transition "temperature"
  * C[2] = "smearing temperature"
  """
  dim = 1  # a function with 1-D domain
  param_names = ('A', 'F', 'T')
  # FIXME: Not good yet!!!
  F_guess = 1.9
  T_guess = 0.05
  def __call__(self, C, x):
    from numpy import exp
    A, F, T = self.get_params(C, *(self.param_names))
    y = A * (exp((x[0] - F) / T) + 1)**(-1)
    self.func_call_hook(C, x, y)
    return y
  def Guess_xy(self, x, y):
    imin = numpy.argmin(y)
    self.guess_params = (y[imin], self.F_guess, self.T_guess)
    return self.guess_params


