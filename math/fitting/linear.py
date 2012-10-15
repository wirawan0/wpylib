#
# wpylib.math.fitting.linear module
# Created: 20121015
# Wirawan Purwanto
#

"""
wpylib.math.fitting.linear module

Linear fitting tools.
"""

import numpy
from wpylib.math.fitting import fit_result

def linregr2d_SZ(x, y, sigma=None):
  """Performs a linear least square regression to according to a
  linear model

    y(x) = a + b*x ,

  where the input y has uncertainty given by sigma.
  """
  from numpy import sum, sqrt

  # Based on Shiwei's regr.F code (from email received 20060102).
  # See Linear-regression.txt in my repository of Shiwei's files.
  # See also Numerical Recipes in C, 2nd ed, Sec. 15.2.
  xx = numpy.array(x, copy=False)
  yy = numpy.array(y, copy=False)
  if sigma == None:
    # My addition -- can be dangerous
    # In case of no errorbar, we proceed as if all measurement
    # data have the same uncertainty, taken to be 1.
    ww = numpy.ones_like(y)
  else:
    ww = numpy.array(sigma, copy=False)
    ww **= -2      # make 1/sigma**2 array

  e1 = sum(xx * yy * ww)
  e2 = sum(yy * ww)
  d11 = sum(xx * ww)
  d12 = sum(xx**2 * ww)
  d21 = sum(ww)
  d22 = d11

  detinv = 1.0 / (d11*d22 - d12*d21)
  a = (e1*d22 - e2*d12) * detinv
  b = (e2*d11 - e1*d21) * detinv
  varsum = sum((xx*d11 - d12)**2 * ww)
  var = varsum * detinv**2
  sigma = sqrt(var)

  return fit_result(
    fit_method='linregr2d_SZ',
    fit_model='linear',
    a=a,
    b=b,
    sigma=sigma,
  )



def Test_1():
  """Testcase 1.

      >>> wpylib.math.fitting.linear.Test_1()
      ...
      {'a': -1392.3182324234213,
       'b': -0.82241012516149792,
       'fit_method': 'linregr2d_SZ',
       'fit_model': 'linear',
       'sigma': 0.00048320905704467775}

  My wlinreg tool (via 'dtextrap' shell script alias gives:

      a stats:
      Total number of data     : 100000
      Average                  : -1392.32
      Sample standard deviation: 0.000460341
      Error of the average     : 1.45573e-06 (-1.046e-07%)
      b stats:
      Total number of data     : 100000
      Average                  : -0.822099
      Sample standard deviation: 0.0803118
      Error of the average     : 0.00025397 (-0.03089%)
      Summary
      a =      -1392.31823569246 +/-   0.000460341146124978 = -1392.31824(46)
      b =     -0.822098515674071 +/-     0.0803118207916705 = -0.822(80)

  """
  from wpylib.text_tools import make_matrix as mtx
  M = mtx("""
  # Source: Co+ QMC/CAS(8,11)d26 cc-pwCVQZ-DK result dated 20121015
   0.01    -1392.32619 0.00047
   0.005   -1392.32284 0.00037
   0.0025  -1392.31994 0.00038
  """)
  x = M[:,0]
  y = M[:,1]
  dy = M[:,2]
  rslt = linregr2d_SZ(x,y,dy)
  print rslt
  return rslt
